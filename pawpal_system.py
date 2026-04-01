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
    status: str = "pending"  # "pending" | "complete"

    def mark_complete(self):
        self.status = "complete"

    def priority_value(self):
        # Returns int: high=3, medium=2, low=1
        mapping = {"high": 3, "medium": 2, "low": 1}
        return mapping.get(self.priority, 1)


@dataclass
class Pet:
    name: str
    species: str  # "dog" | "cat" | "other"

    def __post_init__(self):
        self.tasks = []

    def add_task(self, task):
        self.tasks.append(task)

    def get_default_tasks(self):
        # Returns a list of Task objects appropriate for this species
        if self.species == "dog":
            return [
                Task("Morning walk", 30, "high"),
                Task("Feeding", 10, "high"),
                Task("Playtime", 20, "medium"),
                Task("Grooming", 15, "low"),
            ]
        elif self.species == "cat":
            return [
                Task("Feeding", 10, "high"),
                Task("Litter box cleaning", 10, "high"),
                Task("Playtime", 15, "medium"),
                Task("Brushing", 10, "low"),
            ]
        else:
            return [
                Task("Feeding", 10, "high"),
                Task("Cage/habitat cleaning", 20, "medium"),
                Task("Handling/socialization", 15, "low"),
            ]


class DailyPlan:
    def __init__(self, owner_name, pet_name):
        self.owner_name = owner_name      # str — whose plan this is
        self.pet_name = pet_name          # str — which pet this plan is for
        self.scheduled_items = []         # list of {"task": Task, "start_time": int}
        self.total_duration = 0

    def add_item(self, task, start_time):
        # Adds a task to scheduled_items and updates total_duration
        self.scheduled_items.append({"task": task, "start_time": start_time})
        self.total_duration += task.duration_minutes

    def explain(self):
        # Returns a human-readable string describing each scheduled task and why it was chosen
        lines = []
        for item in self.scheduled_items:
            task = item["task"]
            start = item["start_time"]
            hour = start // 60
            minute = start % 60
            lines.append(
                f"{hour:02d}:{minute:02d} — {task.title} ({task.duration_minutes} min, priority: {task.priority})"
            )
        return "\n".join(lines) if lines else "No tasks scheduled."

    def display(self):
        # Returns a list of dicts for use in Streamlit (st.table / st.dataframe)
        rows = []
        for item in self.scheduled_items:
            task = item["task"]
            start = item["start_time"]
            hour = start // 60
            minute = start % 60
            rows.append({
                "Start Time": f"{hour:02d}:{minute:02d}",
                "Task": task.title,
                "Duration (min)": task.duration_minutes,
                "Priority": task.priority,
            })
        return rows


class Scheduler:
    def __init__(self, owner, pet, tasks):
        self.owner = owner  # Owner
        self.pet = pet      # Pet
        self.tasks = tasks  # list of Task

    def filter_tasks(self, sorted_tasks, available):
        # Returns only the tasks that fit within available minutes
        result = []
        remaining = available
        for task in sorted_tasks:
            if task.duration_minutes <= remaining:
                result.append(task)
                remaining -= task.duration_minutes
        return result

    def generate_plan(self):
        # Sorts tasks by priority, filters to fit available time, returns a DailyPlan
        task_list = self.tasks if self.tasks else self.pet.get_default_tasks()
        sorted_tasks = sorted(task_list, key=lambda t: t.priority_value(), reverse=True)
        fitting_tasks = self.filter_tasks(sorted_tasks, self.owner.available_minutes)

        plan = DailyPlan(self.owner.name, self.pet.name)
        current_time = 480  # 8:00 AM in minutes from midnight
        for task in fitting_tasks:
            plan.add_item(task, current_time)
            current_time += task.duration_minutes
        return plan
