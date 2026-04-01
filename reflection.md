# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

The initial design centers on three core user actions:

1. **Set up a pet profile** — The user enters their name, their pet's name, and the pet's species. This gives the scheduler the context it needs to understand what kind of care is appropriate (e.g., dogs need walks, cats may not).

2. **Add and manage care tasks** — The user creates tasks, each with a title, estimated duration in minutes, and a priority level (low, medium, or high). These tasks form the input list the scheduler draws from when building a plan.

3. **Generate and view today's schedule** — The user triggers the scheduler, which selects and orders tasks based on priority and available time, then displays the resulting plan along with a brief explanation of why each task was included and when it is scheduled.

To support these actions, the design uses five classes:

- **Owner** — a simple data holder storing the owner's `name` and `available_minutes` (total time per day they can spend on pet care). It has no behavior of its own; its only job is to carry the time constraint into the scheduler.

- **Pet** — stores the pet's `name` and `species`. It also provides `get_default_tasks()`, which returns a species-appropriate starter list of `Task` objects so the user does not have to build a task list from scratch.

- **Task** — represents a single care activity with a `title`, `duration_minutes`, and a string `priority` ("low", "medium", or "high"). The `priority_value()` method converts that string to an integer (high=3, medium=2, low=1) so tasks can be sorted numerically by the scheduler.

- **Scheduler** — the coordinator. It holds an `Owner`, a `Pet`, and a list of `Task` objects. Its `generate_plan()` method sorts tasks by priority, calls `filter_tasks()` to remove anything that won't fit in the owner's available time, then assembles and returns a `DailyPlan`. Separating filtering into its own method keeps the logic readable and testable.

- **DailyPlan** — the output of the scheduler. It maintains a list of scheduled items (each pairing a `Task` with a start time in minutes from midnight) and a running `total_duration`. The `add_item()` method appends to that list, `explain()` returns a human-readable summary of what was scheduled and why, and `display()` formats the data as a list of dicts for the Streamlit UI.

**b. Design changes**

Two structural changes were made after reviewing the initial skeleton for missing relationships and logic gaps:

1. **`DailyPlan` now receives `owner_name` and `pet_name` at construction.** In the original design, `DailyPlan` held no reference to the owner or pet, so `explain()` and `display()` could not say whose plan it was or which pet it covered. Passing those two strings in makes the plan self-contained and lets the UI display a meaningful header without reaching back into the scheduler.

2. **`generate_plan()` falls back to `pet.get_default_tasks()` when the task list is empty.** In the original design, `pet` was stored on `Scheduler` but never used — it was a dead attribute. Adding the fallback puts `pet` to work and means the app produces a useful schedule even when the user hasn't manually added any tasks, which is a common first-run situation.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
