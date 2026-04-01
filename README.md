# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## Smarter Scheduling

The scheduler now goes beyond a simple priority list with three enhancements:

**Sorting by value density** — Instead of sorting purely by priority label, tasks are ranked by *priority value ÷ duration* before being added to the plan. This greedy knapsack heuristic fits more high-value work into the owner's time budget (e.g., a short high-priority task beats a long medium-priority one).

**Filtering with two-pass selection** — Required tasks are always attempted first and reserved before optional tasks compete for the remaining time. Any task that doesn't fit (or whose dependency isn't in the plan) is collected in `dropped_tasks` and surfaced in the UI so the owner knows what was skipped and why.

**Conflict detection** — `DailyPlan.detect_conflicts()` scans the sorted schedule for overlapping time windows and returns every conflicting pair. `Scheduler.detect_conflicts()` wraps this into human-readable warning strings, making it easy to surface issues in the Streamlit UI or the `main.py` demo.

## Testing PawPal+

### Running the test suite

```bash
python -m pytest
```

### What the tests cover

| Area | Tests |
|---|---|
| **Sorting correctness** | Verifies `sort_by_time()` returns items in ascending order and that `generate_plan()` assigns non-decreasing start times |
| **Recurrence logic** | Confirms that completing a `"daily"` task spawns a new task due the next day, a `"weekly"` task advances by 7 days, and a `"once"` task returns `None` |
| **Conflict detection** | Checks that overlapping time windows are flagged, back-to-back tasks (no gap) are not flagged, and same-start-time tasks produce a `WARNING` string |
| **Core behavior** | `mark_complete()` transitions status to `"complete"`; `add_task()` grows the pet's task list |

### Confidence level

**4 / 5 stars**

The happy paths and most critical edge cases (recurrence, conflict boundaries, sorting) are covered and all 10 tests pass. One star is withheld because the dependency-dropped scenario — where a task's prerequisite is dropped for time and the dependent task is still scheduled — is a known gap in both the tests and the system logic.
