from pawpal_system import Owner, Pet, Task, DailyPlan, Scheduler

# ── Setup ──────────────────────────────────────────────────────────────────────
owner = Owner(name="Alex", available_minutes=120)
dog = Pet(name="Buddy", species="dog")
cat = Pet(name="Whiskers", species="cat")

# ── Generate individual plans via Scheduler ────────────────────────────────────
dog_scheduler = Scheduler(owner, dog, dog.get_default_tasks())
cat_scheduler = Scheduler(owner, cat, cat.get_default_tasks())

dog_plan = dog_scheduler.generate_plan()
cat_plan = cat_scheduler.generate_plan()

# ── Merge into one combined plan for sorting / filtering / conflict detection ──
combined = DailyPlan(owner_name=owner.name)
for item in dog_plan.scheduled_items:
    combined.add_item(item["task"], item["start_time"], dog)
for item in cat_plan.scheduled_items:
    combined.add_item(item["task"], item["start_time"], cat)

# Add a second explicit conflict: both pets get an extra "Feeding" at 12:00 PM
combined.add_item(Task("Lunch feeding", 10, "high"), 720, dog)
combined.add_item(Task("Lunch feeding", 10, "high"), 720, cat)  # same time — conflict!

# ── 1. SORTING ─────────────────────────────────────────────────────────────────
print(f"=== {owner.name}'s Full Schedule (sorted by time) ===")
for item in combined.sort_by_time():
    t, s, p = item["task"], item["start_time"], item["pet"]
    hh, mm = s // 60, s % 60
    pet_label = f"[{p.name}]" if p else ""
    print(f"  {hh:02d}:{mm:02d}  {pet_label:12s} {t.title:20s} "
          f"{t.duration_minutes:3d} min  {t.priority:<6s}  freq={t.frequency}")

# ── 2. FILTERING by pet ────────────────────────────────────────────────────────
print()
print(f"=== Buddy's tasks only ===")
for item in combined.filter_tasks(pet_name="Buddy"):
    t, s = item["task"], item["start_time"]
    hh, mm = s // 60, s % 60
    print(f"  {hh:02d}:{mm:02d}  {t.title:20s}  status={t.status}")

# ── 3. FILTERING by status ─────────────────────────────────────────────────────
print()
print(f"=== Pending tasks (all pets) ===")
pending = combined.filter_tasks(status="pending")
print(f"  {len(pending)} task(s) still pending")
for item in pending:
    t, p = item["task"], item["pet"]
    print(f"    -[{p.name if p else '?'}] {t.title}")

# ── 4. RECURRING TASK auto-creation ───────────────────────────────────────────
print()
print("=== Recurring task demo ===")
walk_item = next(i for i in combined.scheduled_items if i["task"].title == "Morning walk")
walk_task = walk_item["task"]
print(f"  Completing '{walk_task.title}' (freq={walk_task.frequency}, due={walk_task.due_date})")

next_task = walk_task.mark_complete()
if next_task:
    combined.add_item(next_task, walk_item["start_time"], walk_item["pet"])
    print(f"  Auto-created next occurrence -> due {next_task.due_date}")
else:
    print("  One-time task — no recurrence created.")

print()
print("=== Pending tasks after completing Morning walk ===")
for item in combined.filter_tasks(status="pending"):
    t, p = item["task"], item["pet"]
    due = f"  due={t.due_date}" if t.due_date else ""
    print(f"    -[{p.name if p else '?'}] {t.title}{due}")

completed = combined.filter_tasks(status="complete")
print()
print(f"=== Completed tasks: {len(completed)} ===")
for item in completed:
    t, p = item["task"], item["pet"]
    print(f"    -[{p.name if p else '?'}] {t.title}")

# ── 5. CONFLICT DETECTION via Scheduler ───────────────────────────────────────
print()
print("=== Conflict Detection (via Scheduler) ===")
warnings = dog_scheduler.detect_conflicts(combined)
if warnings:
    for w in warnings:
        print(f"  {w}")
else:
    print("  No conflicts found.")

print()
print(f"Total duration in plan: {combined.total_duration} min")
