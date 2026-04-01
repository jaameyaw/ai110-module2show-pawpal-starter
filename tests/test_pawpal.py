import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import date
from pawpal_system import Task, Pet, Owner, Scheduler, DailyPlan


def test_mark_complete_changes_status():
    """Calling mark_complete() should change task status from 'pending' to 'complete'."""
    task = Task("Morning walk", 30, "high")
    assert task.status == "pending"
    task.mark_complete()
    assert task.status == "complete"


def test_add_task_increases_pet_task_count():
    """Adding a task to a Pet should increase that pet's task count by one."""
    pet = Pet("Buddy", "dog")
    initial_count = len(pet.tasks)
    pet.add_task(Task("Feeding", 10, "high"))
    assert len(pet.tasks) == initial_count + 1


# --- Sorting Correctness ---

def test_sort_by_time_returns_chronological_order():
    """sort_by_time() should return items in ascending start-time order."""
    plan = DailyPlan()
    task_a = Task("Evening walk", 30, "medium")
    task_b = Task("Feeding",      10, "high")
    task_c = Task("Playtime",     20, "low")

    # Add in reverse chronological order: 18:00, 12:00, 08:00
    plan.add_item(task_a, start_time=1080)  # 18:00
    plan.add_item(task_b, start_time=720)   # 12:00
    plan.add_item(task_c, start_time=480)   # 08:00

    sorted_items = plan.sort_by_time()
    start_times = [item["start_time"] for item in sorted_items]
    assert start_times == sorted(start_times), "Items should be in ascending time order"


def test_generate_plan_schedules_tasks_in_time_order():
    """generate_plan() should assign start times that increase from task to task."""
    owner = Owner("Alex", available_minutes=120)
    pet   = Pet("Luna", "cat")
    tasks = [
        Task("Feeding",             10, "high",   required=True),
        Task("Litter box cleaning", 10, "high",   required=True),
        Task("Playtime",            15, "medium"),
        Task("Brushing",            10, "low"),
    ]

    plan = Scheduler(owner, pet, tasks).generate_plan()
    start_times = [item["start_time"] for item in plan.scheduled_items]
    assert start_times == sorted(start_times), "Plan start times should be non-decreasing"


# --- Recurrence Logic ---

def test_daily_task_creates_next_occurrence_one_day_later():
    """mark_complete() on a daily task should return a new Task due the next day."""
    today = date(2026, 4, 1)
    task  = Task("Feeding", 10, "high", frequency="daily", due_date=today)

    next_task = task.mark_complete()

    assert next_task is not None, "daily task should produce a follow-up task"
    assert next_task.due_date == date(2026, 4, 2), "next occurrence should be due tomorrow"
    assert next_task.status == "pending", "new occurrence starts as pending"
    assert next_task.title == task.title, "recurrence inherits the same title"


def test_weekly_task_creates_next_occurrence_seven_days_later():
    """mark_complete() on a weekly task should return a new Task due 7 days later."""
    today = date(2026, 4, 1)
    task  = Task("Grooming", 15, "medium", frequency="weekly", due_date=today)

    next_task = task.mark_complete()

    assert next_task is not None
    assert next_task.due_date == date(2026, 4, 8)


def test_once_task_returns_none_on_complete():
    """mark_complete() on a one-off task should return None (no recurrence)."""
    task = Task("Vet visit", 60, "high", frequency="once")
    assert task.mark_complete() is None


# --- Conflict Detection ---

def test_detect_conflicts_flags_overlapping_tasks():
    """Two tasks whose time windows overlap should be reported as a conflict."""
    plan   = DailyPlan()
    pet    = Pet("Buddy", "dog")
    task_a = Task("Morning walk", 30, "high")
    task_b = Task("Feeding",      10, "high")

    # task_a runs 08:00–08:30; task_b starts at 08:15 — overlap
    plan.add_item(task_a, start_time=480, pet=pet)
    plan.add_item(task_b, start_time=495, pet=pet)

    conflicts = plan.detect_conflicts()
    assert len(conflicts) == 1, "Exactly one overlapping pair should be detected"


def test_detect_conflicts_none_for_sequential_tasks():
    """Tasks scheduled back-to-back (no gap) should NOT produce a conflict."""
    plan   = DailyPlan()
    pet    = Pet("Buddy", "dog")
    task_a = Task("Morning walk", 30, "high")
    task_b = Task("Feeding",      10, "high")

    # task_a ends exactly at 08:30; task_b starts at 08:30 — no overlap
    plan.add_item(task_a, start_time=480, pet=pet)
    plan.add_item(task_b, start_time=510, pet=pet)

    conflicts = plan.detect_conflicts()
    assert len(conflicts) == 0, "Back-to-back tasks should not be flagged as a conflict"


def test_scheduler_detect_conflicts_warns_on_same_start_time():
    """Two tasks with the same start time should trigger a Scheduler conflict warning."""
    owner  = Owner("Alex", available_minutes=120)
    pet    = Pet("Buddy", "dog")
    plan   = DailyPlan()
    task_a = Task("Morning walk", 30, "high")
    task_b = Task("Feeding",      10, "high")

    # Force both onto the same start time
    plan.add_item(task_a, start_time=480, pet=pet)
    plan.add_item(task_b, start_time=480, pet=pet)

    scheduler = Scheduler(owner, pet, [])
    warnings  = scheduler.detect_conflicts(plan)
    assert len(warnings) > 0, "Identical start times should produce at least one warning"
    assert "WARNING" in warnings[0]
