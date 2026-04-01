from pawpal_system import Owner, Pet, Task, DailyPlan

# Create an owner
owner = Owner(name="Alex", available_minutes=90)

# Create two pets
dog = Pet(name="Buddy", species="dog")
cat = Pet(name="Whiskers", species="cat")

# Create tasks with different times (start times in minutes from midnight)
# 7:00 AM = 420, 8:00 AM = 480, 12:00 PM = 720
tasks = [
    {"task": Task("Morning walk", 30, "high"),      "start_time": 420,  "pet": dog},
    {"task": Task("Feeding",      10, "high"),      "start_time": 480,  "pet": dog},
    {"task": Task("Playtime",     20, "medium"),    "start_time": 720,  "pet": dog},
    {"task": Task("Feeding",      10, "high"),      "start_time": 480,  "pet": cat},
    {"task": Task("Litter box",   10, "high"),      "start_time": 490,  "pet": cat},
    {"task": Task("Brushing",     10, "low"),       "start_time": 730,  "pet": cat},
]

# Build a DailyPlan
plan = DailyPlan()
for entry in tasks:
    plan.add_item(entry["task"], entry["start_time"])

# Print Today's Schedule
print(f"=== Today's Schedule for {owner.name} ===")
print(f"Pets: {dog.name} ({dog.species}) & {cat.name} ({cat.species})")
print(f"Available time: {owner.available_minutes} minutes")
print()

for entry in tasks:
    task = entry["task"]
    start = entry["start_time"]
    pet = entry["pet"]
    hour = start // 60
    minute = start % 60
    print(f"  {hour:02d}:{minute:02d} — [{pet.name}] {task.title} ({task.duration_minutes} min, {task.priority} priority)")

print()
print(f"Total scheduled: {plan.total_duration} min")
