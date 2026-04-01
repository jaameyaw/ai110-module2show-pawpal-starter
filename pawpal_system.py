from dataclasses import dataclass


@dataclass
class Owner:
    name: str
    available_minutes: int


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str  # "low" | "medium" | "high"

    def priority_value(self):
        # Returns int: high=3, medium=2, low=1
        pass


@dataclass
class Pet:
    name: str
    species: str  # "dog" | "cat" | "other"

    def get_default_tasks(self):
        # Returns a list of Task objects appropriate for this species
        pass


class DailyPlan:
    def __init__(self):
        self.scheduled_items = []  # list of {"task": Task, "start_time": int}
        self.total_duration = 0

    def add_item(self, task, start_time):
        # Adds a task to scheduled_items and updates total_duration
        pass

    def explain(self):
        # Returns a human-readable string describing each scheduled task and why it was chosen
        pass

    def display(self):
        # Returns a list of dicts for use in Streamlit (st.table / st.dataframe)
        pass


class Scheduler:
    def __init__(self, owner, pet, tasks):
        self.owner = owner  # Owner
        self.pet = pet      # Pet
        self.tasks = tasks  # list of Task

    def filter_tasks(self, sorted_tasks, available):
        # Returns only the tasks that fit within available minutes
        pass

    def generate_plan(self):
        # Sorts tasks by priority, filters to fit available time, returns a DailyPlan
        pass
