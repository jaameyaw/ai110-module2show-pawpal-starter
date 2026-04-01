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

The scheduler considers three constraints, in order of strictness:

1. **Required flag** — tasks marked `required=True` are reserved first, before any optional task competes for time. This acts as a hard constraint: a required task is included regardless of its value density, as long as it physically fits in the budget.

2. **Time budget** — `Owner.available_minutes` is the hard ceiling. No combination of tasks can exceed it. The scheduler accumulates duration greedily and stops adding tasks once the remaining time would be exceeded.

3. **Value density (priority ÷ duration)** — among optional tasks, the scheduler ranks by this ratio rather than raw priority. A 5-minute medium-priority task (density 0.4) beats a 60-minute high-priority task (density 0.05) when time is tight, because it delivers more value per minute.

The required constraint came first because pet care has non-negotiable tasks (medication, feeding) where no optimization logic should override the owner's intent. Time was next because the entire system is built around a finite daily budget. Value density was chosen over simple priority because raw priority ignores duration — a naive sort by priority alone would greedily schedule long, important tasks and crowd out many shorter, useful ones.

**b. Tradeoffs**

The conflict-detection algorithm uses an exhaustive O(n²) pair comparison: every scheduled item is compared against every later item to check whether their time windows overlap. A more sophisticated approach — such as a sweep-line algorithm — would run in O(n log n) and could also group overlapping tasks into "conflict clusters" rather than listing every individual pair.

The tradeoff is **simplicity and correctness over performance and output quality**. For a daily pet-care schedule, the number of tasks is typically small (fewer than 20), so the quadratic cost is invisible in practice. The explicit nested loop also makes the algorithm's intent easy to read and verify. Grouping conflicts into clusters would produce cleaner output for the owner, but it would require significantly more code and is not worth the complexity at this scale.

If the app were extended to manage dozens of pets or generate weekly bulk plans, switching to a sweep-line approach and conflict clustering would become the right call.

---

## 3. AI Collaboration

**a. How you used AI**

AI was used in three distinct phases, each with a different mode of interaction:

- **Design phase (brainstorming):** I used chat to stress-test the class diagram before writing any code. Prompts like "What happens if the task list is empty when generate_plan() runs?" and "Does DailyPlan need to know who it belongs to, or can the UI figure that out?" surfaced the two design gaps that became the Section 1b changes — the fallback to `get_default_tasks()` and passing `owner_name`/`pet_name` into `DailyPlan`.

- **Implementation phase (code generation and debugging):** Copilot inline completions were most useful for boilerplate-heavy methods like `display()` (building the list-of-dicts structure) and the `detect_conflicts()` nested loop. For logic-heavy methods like `generate_plan()`, I drafted the structure myself and used Copilot to fill in the inner body, then read the output carefully before accepting.

- **Testing phase (edge-case generation):** Chat was useful for generating a list of edge cases I might not have considered ("what if two tasks have exactly the same start time?" "what if available_minutes is less than the shortest required task?"). These became the basis for additional test cases.

The most productive prompt pattern was **constraint + goal + current state**: "Given that `generate_plan()` must always include required tasks and then fill remaining time by value density, and given that the task list may be empty, what should the method do at the top before sorting?" That specificity got useful answers immediately; vague prompts like "help me write the scheduler" produced generic code that didn't match the design.

**b. Judgment and verification**

During the implementation of `generate_plan()`, Copilot suggested sorting all tasks by `priority_value()` descending as the first step, then filtering by time — essentially the original naive design. I rejected this because it ignores the required/optional split and uses raw priority instead of value density.

I evaluated the suggestion by tracing through a concrete example: an owner with 30 minutes, one required 20-minute low-priority task (medication), and one optional 30-minute high-priority task (long walk). The Copilot version would schedule the walk (higher priority) and drop the medication — the wrong answer. My version reserves the medication first, then sees only 10 minutes remain and skips the walk. Working through that specific case made the flaw concrete and confirmed that the required-first, value-density-second ordering was correct.

**c. VS Code Copilot — AI Strategy**

*Which features were most effective for building your scheduler?*

Two Copilot features stood out. **Inline completions** were most useful during implementation of repetitive but error-prone structures — specifically the nested loop in `detect_conflicts()` and the list-of-dicts construction in `display()`. Copilot inferred the pattern from surrounding code and completed the body correctly, saving time without requiring me to describe the intent. **Copilot Chat** (the side-panel conversation mode) was more useful during the design and testing phases, where I needed to reason about behavior rather than just produce syntax. Asking "given this class structure, what inputs would break generate_plan()?" produced useful edge cases I could turn directly into tests.

*One AI suggestion I rejected or modified to keep the design clean:*

Copilot Chat suggested adding a `schedule_time` attribute directly on `Task` so that each task "knows" when it is scheduled. I rejected this because it violates single responsibility: a `Task` is a description of care work, not a scheduled appointment. If `schedule_time` lives on `Task`, then the same task object cannot appear in multiple plans (a daily recurring task would need to be cloned for each day), and the class becomes harder to reason about in isolation. I kept the time data in `DailyPlan.scheduled_items` as a dictionary pairing `{"task": task, "start_time": minutes}` — the plan owns the scheduling data, and the task stays a pure data object.

*How separate chat sessions for different phases helped with organization:*

Starting a new chat session at each phase boundary — design, implementation, testing — prevented context pollution. During the design session, the conversation focused entirely on class relationships and invariants, with no code yet written; Copilot's suggestions stayed at the architectural level. When I opened a fresh implementation session with the finalized class diagram as context, the suggestions were grounded in the actual design rather than half-remembered earlier drafts. The testing session started with the finished code, so edge-case suggestions were realistic. If I had used one long session throughout, later suggestions would have been influenced by early exploratory ideas that were ultimately discarded.

*What I learned about being the "lead architect" when collaborating with powerful AI tools:*

The lead architect's job is not to write every line — it is to hold the system's invariants in mind and evaluate every suggestion against them. AI tools are fast and fluent; they will produce plausible-looking code for almost any prompt. The danger is accepting suggestions that are locally correct (the method runs, the tests pass) but globally wrong (the design becomes coupled, the responsibility boundaries erode). Acting as lead architect meant deciding before prompting: what must this method do, what must it not do, and what does "correct" look like for this specific design? With those decisions made, AI could do the implementation work. Without them, every suggestion becomes a negotiation with no fixed ground truth to negotiate against.

---

## 4. Testing and Verification

**a. What you tested**

The test suite covers behavior across four areas:

1. **Task prioritization and value density** — verified that `priority_value()` returns the correct integer for each string label, and that `value_density()` produces the correct ratio. These matter because the entire scheduling algorithm depends on the ordering these methods produce.

2. **Scheduler output composition** — confirmed that `generate_plan()` includes required tasks regardless of density, excludes tasks that exceed the time budget, and correctly adds dropped tasks to `plan.dropped_tasks`. These tests validate the core invariants of the scheduling logic.

3. **Conflict detection** — tested pairs of items with overlapping windows, adjacent (non-overlapping) windows, and identical start times to verify the O(n²) comparison correctly identifies real conflicts and does not flag false positives.

4. **DailyPlan output** — tested that `explain()` produces a non-empty string and that `display()` / `sort_by_time()` return data in the expected format, since those methods are the contract between the scheduler and the Streamlit UI.

These tests matter because the scheduler is the only component that cannot be checked visually in the UI during development. A mistake in `generate_plan()`'s ordering logic produces a plausible-looking but wrong schedule — no error is raised, so automated tests are the only reliable check.

**b. Confidence**

I am confident the scheduler is correct for the common cases covered by the test suite: mixed required/optional tasks, budgets that force some tasks to be dropped, and overlapping conflict detection. My confidence is lower for two areas:

- **Dependency chains** — `Task` has a `dependencies` field but `generate_plan()` does not currently enforce ordering between dependent tasks. A dependent task could be scheduled before its prerequisite.
- **Exact-budget boundary** — if the sum of all tasks equals exactly `available_minutes`, the scheduler should include all of them. I did not write a test for this boundary case.

If I had more time, I would add tests for both of these, plus a fuzz-style test that generates random task lists and checks that the total scheduled duration never exceeds `available_minutes`.

---

## 5. Reflection

**a. What went well**

The part I am most satisfied with is the value-density scheduling algorithm and the decision to separate required tasks from optional ones before sorting. It is a simple idea — divide priority by duration, reserve hard constraints first — but it produces genuinely useful behavior: a pet owner with 30 minutes gets their non-negotiable tasks done and fills the remaining time with the highest-return optional tasks, rather than running out of time on a single long low-priority item. The logic is also clean enough to read in one pass, which made writing tests for it straightforward.

**b. What you would improve**

The dependency system is the clearest gap. `Task` stores a `dependencies` list, but `generate_plan()` ignores it entirely. In a real scheduling context — for example, "groom the dog" depends on "bathe the dog" — this matters. I would redesign `generate_plan()` to perform a topological sort on the dependency graph before applying the value-density ranking, so that ordering constraints are respected without the user having to manually sequence tasks.

I would also redesign the `detect_conflicts()` return type. Currently it returns a list of human-readable warning strings, which is convenient for the UI but makes the data hard to use programmatically. Returning structured conflict objects (with references to the two conflicting `Task` instances) would let downstream code suggest resolutions rather than just display messages.

**c. Key takeaway**

The most important thing I learned is that **AI tools accelerate execution but cannot substitute for design**. Copilot could generate a working `detect_conflicts()` loop in seconds, but it could not decide whether conflicts should be returned as strings or structured objects, whether required tasks should preempt optional ones, or whether value density was the right ranking criterion. Every one of those decisions required understanding the problem, not just the syntax.

The "lead architect" role means making those decisions before touching the AI tools — not after. When I gave Copilot a clear structure to fill in, the output was useful. When I asked it to design something open-ended, I got generic code that fit no particular design. The AI is a fast, capable implementer; the human has to be the one who knows what to implement and why.
