import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pawpal_system import Task, Pet


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
