from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Optional


@dataclass
class Owner:
    name: str
    available_minutes: int
    pet_time_budgets: dict = field(default_factory=dict)  # {pet_name: minutes} (#8)

    def budget_for(self, pet_name: str) -> int:
        """Return per-pet budget if set, otherwise fall back to available_minutes."""
        return self.pet_time_budgets.get(pet_name, self.available_minutes)


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str           # "low" | "medium" | "high"
    status: str = "pending" # "pending" | "complete"
    required: bool = False  # must-do; always included before optional tasks (#2)
    earliest_start: int = 0 # minutes from midnight; 0 = no constraint (#3)
    depends_on: Optional[str] = None  # title of task that must run first (#4)
    frequency: str = "once"           # "once" | "daily" | "weekly"
    due_date: Optional[date] = None   # when this occurrence is due

    def mark_complete(self) -> Optional["Task"]:
        """Mark this task complete and return the next occurrence if recurring."""
        self.status = "complete"
        if self.frequency == "daily":
            base = self.due_date or date.today()
            next_due = base + timedelta(days=1)
        elif self.frequency == "weekly":
            base = self.due_date or date.today()
            next_due = base + timedelta(weeks=1)
        else:
            return None
        return Task(
            title=self.title,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            required=self.required,
            earliest_start=self.earliest_start,
            depends_on=self.depends_on,
            frequency=self.frequency,
            due_date=next_due,
        )

    def priority_value(self):
        """Map priority label to a numeric score (high=3, medium=2, low=1)."""
        mapping = {"high": 3, "medium": 2, "low": 1}
        return mapping.get(self.priority, 1)

    def value_density(self):
        """Priority value per minute — higher = more bang-for-buck (#9)."""
        return self.priority_value() / self.duration_minutes


@dataclass
class Pet:
    name: str
    species: str  # "dog" | "cat" | "other"

    def __post_init__(self):
        self.tasks = []

    def add_task(self, task):
        """Append a Task to this pet's task list."""
        self.tasks.append(task)

    def get_default_tasks(self):
        """Return a species-appropriate list of starter Tasks for this pet."""
        if self.species == "dog":
            return [
                Task("Morning walk", 30, "high", required=True, earliest_start=420),
                Task("Feeding", 10, "high", required=True),
                Task("Playtime", 20, "medium"),
                Task("Grooming", 15, "low"),
            ]
        elif self.species == "cat":
            return [
                Task("Feeding", 10, "high", required=True),
                Task("Litter box cleaning", 10, "high", required=True),
                Task("Playtime", 15, "medium"),
                Task("Brushing", 10, "low"),
            ]
        else:
            return [
                Task("Feeding", 10, "high", required=True),
                Task("Cage/habitat cleaning", 20, "medium"),
                Task("Handling/socialization", 15, "low"),
            ]


class DailyPlan:
    def __init__(self, owner_name="", pet_name=""):
        self.owner_name = owner_name
        self.pet_name = pet_name
        self.scheduled_items = []   # list of {"task": Task, "start_time": int, "pet": Pet|None}
        self.dropped_tasks = []     # tasks that didn't fit or had unmet deps (#5)
        self.total_duration = 0

    def add_item(self, task, start_time, pet=None):
        """Add a scheduled task entry and accumulate its duration into the plan total."""
        self.scheduled_items.append({"task": task, "start_time": start_time, "pet": pet})
        self.total_duration += task.duration_minutes

    def sort_by_time(self):
        """Return scheduled items sorted by start time via HH:MM string comparison."""
        return sorted(
            self.scheduled_items,
            key=lambda item: f"{item['start_time'] // 60:02d}:{item['start_time'] % 60:02d}"
        )

    def filter_tasks(self, pet_name=None, status=None):
        """Filter items by pet name and/or task completion status (returns a list)."""
        result = self.scheduled_items
        if pet_name is not None:
            result = [i for i in result if i["pet"] and i["pet"].name == pet_name]
        if status is not None:
            result = [i for i in result if i["task"].status == status]
        return result

    def detect_conflicts(self):
        """Return list of (item_a, item_b) pairs whose time windows overlap."""
        sorted_items = self.sort_by_time()
        conflicts = []
        for idx_a in range(len(sorted_items)):
            for idx_b in range(idx_a + 1, len(sorted_items)):
                a, b = sorted_items[idx_a], sorted_items[idx_b]
                if a["start_time"] + a["task"].duration_minutes > b["start_time"]:
                    conflicts.append((a, b))
        return conflicts

    def explain(self):
        """Return a human-readable summary of the plan, including skipped tasks and drop reasons."""
        lines = []
        for item in self.scheduled_items:
            task = item["task"]
            start = item["start_time"]
            hour, minute = start // 60, start % 60
            req_tag = " [required]" if task.required else ""
            lines.append(
                f"{hour:02d}:{minute:02d} — {task.title} "
                f"({task.duration_minutes} min, priority: {task.priority}{req_tag})"
            )
        if self.dropped_tasks:
            lines.append("")
            lines.append("Skipped (didn't fit or dependency unmet):")
            for t in self.dropped_tasks:
                reason = f"needs '{t.depends_on}' first" if t.depends_on else "not enough time"
                lines.append(f"  • {t.title} ({t.duration_minutes} min, {t.priority}) — {reason}")
        return "\n".join(lines) if lines else "No tasks scheduled."

    def display(self):
        """Return the plan as a list of dicts suitable for st.table() or tabular display."""
        rows = []
        for item in self.scheduled_items:
            task = item["task"]
            start = item["start_time"]
            hour, minute = start // 60, start % 60
            rows.append({
                "Start Time": f"{hour:02d}:{minute:02d}",
                "Task": task.title,
                "Duration (min)": task.duration_minutes,
                "Priority": task.priority,
                "Required": "yes" if task.required else "no",
            })
        return rows


class Scheduler:
    def __init__(self, owner, pet, tasks, buffer_minutes=0):
        self.owner = owner
        self.pet = pet
        self.tasks = tasks
        self.buffer_minutes = buffer_minutes  # rest gap between tasks (#6)

    def _sort_key(self, task):
        """Sorting key: required tasks first, then descending value density, then shorter duration.

        Sorting by value density (priority / duration) maximises the total priority
        points that fit within the owner's time budget — a greedy knapsack heuristic.
        """
        # Required first; then by value density desc; then shorter duration on tie (#1, #9)
        return (not task.required, -task.value_density(), task.duration_minutes)

    def _resolve_dependencies(self, tasks):
        """Topological reorder so each task's depends_on comes before it (#4)."""
        title_map = {t.title: t for t in tasks}
        ordered, seen = [], set()

        def place(task):
            if task.title in seen:
                return
            if task.depends_on and task.depends_on in title_map:
                place(title_map[task.depends_on])
            ordered.append(task)
            seen.add(task.title)

        for t in tasks:
            place(t)
        return ordered

    def filter_tasks(self, sorted_tasks, available):
        """Required tasks are always attempted first; optional fill remaining time (#2, #5)."""
        fitting, dropped = [], []
        remaining = available

        for pass_required in (True, False):
            for task in sorted_tasks:
                if task.required != pass_required:
                    continue
                cost = task.duration_minutes + self.buffer_minutes
                if cost <= remaining:
                    fitting.append(task)
                    remaining -= cost
                else:
                    dropped.append(task)

        return fitting, dropped

    def generate_plan(self):
        """Build and return a DailyPlan for the owner/pet pair.

        Steps:
          1. Exclude already-completed tasks.
          2. Sort remaining tasks with _sort_key (required → value density → duration).
          3. Greedily select tasks that fit within the owner's time budget.
          4. Re-order selected tasks to satisfy dependency constraints.
          5. Assign start times starting at 08:00, honouring earliest_start and buffer gaps.
        """
        # Skip already-completed tasks (#10)
        task_list = [
            t for t in (self.tasks or self.pet.get_default_tasks())
            if t.status != "complete"
        ]

        sorted_tasks = sorted(task_list, key=self._sort_key)

        # Use per-pet budget if configured (#8)
        available = self.owner.budget_for(self.pet.name)

        fitting_tasks, dropped = self.filter_tasks(sorted_tasks, available)

        # Enforce dependency ordering (#4)
        fitting_tasks = self._resolve_dependencies(fitting_tasks)

        plan = DailyPlan(self.owner.name, self.pet.name)
        plan.dropped_tasks = dropped

        current_time = 480  # 8:00 AM
        for task in fitting_tasks:
            # Respect earliest_start constraint (#3)
            start = max(current_time, task.earliest_start)
            plan.add_item(task, start)
            current_time = start + task.duration_minutes + self.buffer_minutes

        return plan

    def detect_conflicts(self, plan):
        """Return a list of warning strings for any overlapping tasks in the plan.

        Lightweight strategy: never raises — callers decide what to do with warnings.
        """
        warnings = []
        for a, b in plan.detect_conflicts():
            ta, tb = a["task"], b["task"]
            pa, pb = a["pet"], b["pet"]
            a_start, b_start = a["start_time"], b["start_time"]
            a_end = a_start + ta.duration_minutes
            pa_name = pa.name if pa else "?"
            pb_name = pb.name if pb else "?"
            warnings.append(
                f"WARNING: [{pa_name}] '{ta.title}' "
                f"({a_start // 60:02d}:{a_start % 60:02d}–"
                f"{a_end // 60:02d}:{a_end % 60:02d}) "
                f"overlaps [{pb_name}] '{tb.title}' "
                f"(starts {b_start // 60:02d}:{b_start % 60:02d})"
            )
        return warnings
