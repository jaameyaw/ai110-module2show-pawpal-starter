# PawPal+ — Pet Care Scheduling Assistant

**PawPal+** is a Streamlit app that helps pet owners plan and prioritize daily care tasks for their pets. It applies a greedy scheduling algorithm to fit the most valuable tasks into the owner's available time, detects scheduling conflicts, and tracks task recurrence.

---

## 📸 Demo

<a href="/course_images/ai110/your_screenshot_name.png" target="_blank"><img src='/course_images/ai110/your_screenshot_name.png' title='PawPal App' width='' alt='PawPal App' class='center-block' /></a>

---

## ✨ Features

| Feature | Description |
|---|---|
| **Owner & pet setup** | Enter owner name, pet name, species, and daily time budget. Switching any field instantly rebuilds the session. |
| **Species-based default tasks** | One-click loading of sensible starter tasks for dogs, cats, or other pets. |
| **Custom task entry** | Add tasks with title, duration, priority (low / medium / high), required flag, and frequency. |
| **Value-density sorting** | Tasks are ranked by *priority score ÷ duration* before scheduling — a greedy knapsack heuristic that maximises total priority points within the time budget. |
| **Two-pass required/optional filtering** | Required tasks are reserved first; remaining time fills with optional tasks sorted by value density. Tasks that do not fit are collected and surfaced to the user. |
| **Dependency ordering** | Tasks with a `depends_on` relationship are topologically reordered so prerequisites always run first. |
| **Earliest-start constraints** | Each task can specify the earliest minute it may begin (e.g., morning walk no earlier than 07:00). |
| **Conflict detection** | `DailyPlan.detect_conflicts()` scans sorted time windows for overlaps and returns every conflicting pair. The Streamlit UI surfaces these as warnings. |
| **Daily recurrence** | Completing a `"daily"` task automatically creates the next occurrence due the following day. |
| **Weekly recurrence** | Completing a `"weekly"` task creates the next occurrence due seven days later. |
| **One-time tasks** | Tasks marked `"once"` are simply completed with no follow-up. |
| **Configurable buffer** | A slider adds a rest gap (0–30 min) between every scheduled task. |
| **Per-pet time budgets** | The `Owner` class supports a `pet_time_budgets` dict so different pets can have different daily time allocations. |
| **Plan reasoning expander** | The UI shows a plain-English explanation of every scheduled and skipped task with drop reasons. |
| **Value-density explainer** | An in-app expander documents the priority-score table and ranking logic for transparency. |

---

## 🚀 Getting Started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Run the app

```bash
streamlit run app.py
```

### Run the test suite

```bash
python -m pytest
```

---

## 🏗️ Architecture

The system is built from four classes defined in [pawpal_system.py](pawpal_system.py):

| Class | Responsibility |
|---|---|
| `Owner` | Stores owner name, global time budget, and optional per-pet budgets. |
| `Pet` | Holds species, task list, and species-appropriate default tasks. |
| `Task` | Represents a single care task with priority, duration, recurrence, and dependency metadata. |
| `DailyPlan` | Collects scheduled items and dropped tasks; supports sorting, filtering, conflict detection, and human-readable explanation. |
| `Scheduler` | Orchestrates sorting → filtering → dependency resolution → time assignment to produce a `DailyPlan`. |

---

## 🧪 Tests

| Area | What is tested |
|---|---|
| **Sorting correctness** | `sort_by_time()` returns ascending order; `generate_plan()` assigns non-decreasing start times. |
| **Recurrence logic** | `"daily"` task advances by 1 day; `"weekly"` by 7 days; `"once"` returns `None`. |
| **Conflict detection** | Overlapping windows are flagged; back-to-back tasks (no gap) are not; same-start-time tasks produce a `WARNING` string. |
| **Core behavior** | `mark_complete()` transitions status to `"complete"`; `add_task()` grows the task list. |

All 10 tests pass. See [test_pawpal.py](test_pawpal.py) for the full suite.

### Confidence level: 4 / 5

The happy paths and critical edge cases (recurrence, conflict boundaries, sorting) are covered. One star is withheld because the scenario where a task's dependency is dropped for time — but the dependent task remains scheduled — is a known gap in both the tests and the system logic.

---

## 📁 Project Structure

```
pawpal_system.py   # Core classes: Owner, Pet, Task, DailyPlan, Scheduler
app.py             # Streamlit UI
test_pawpal.py     # Pytest test suite
requirements.txt   # Python dependencies
```
