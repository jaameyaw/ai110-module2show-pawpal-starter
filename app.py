import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")
st.caption("A smart pet care scheduling assistant.")

# ── Owner & Pet setup ──────────────────────────────────────────────────────────
st.subheader("Owner & Pet")

col_o, col_p, col_s, col_t = st.columns(4)
with col_o:
    owner_name = st.text_input("Owner name", value="Jordan")
with col_p:
    pet_name = st.text_input("Pet name", value="Mochi")
with col_s:
    species = st.selectbox("Species", ["dog", "cat", "other"])
with col_t:
    available_minutes = st.number_input(
        "Time budget (min)", min_value=10, max_value=480, value=120, step=10
    )

# Rebuild owner/pet if any input changes
owner = Owner(name=owner_name, available_minutes=available_minutes)
pet_key = f"{pet_name}_{species}"
if st.session_state.get("pet_key") != pet_key:
    st.session_state.pet = Pet(name=pet_name, species=species)
    st.session_state.pet_key = pet_key

pet = st.session_state.pet

st.divider()

# ── Task management ────────────────────────────────────────────────────────────
st.subheader("Tasks")

if st.button("Load default tasks for this species"):
    defaults = pet.get_default_tasks()
    existing_titles = {t.title for t in pet.tasks}
    added = 0
    for t in defaults:
        if t.title not in existing_titles:
            pet.add_task(t)
            added += 1
    st.success(f"Added {added} default task(s) for {species}.")

st.caption("Add a task:")
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
with col4:
    required = st.checkbox("Required", value=False)
with col5:
    frequency = st.selectbox("Frequency", ["once", "daily", "weekly"])

if st.button("Add task"):
    new_task = Task(
        title=task_title,
        duration_minutes=int(duration),
        priority=priority,
        required=required,
        frequency=frequency,
    )
    pet.add_task(new_task)
    st.rerun()

if pet.tasks:
    st.markdown("**Current tasks:**")
    for i, t in enumerate(pet.tasks):
        col_info, col_btn = st.columns([5, 1])
        with col_info:
            density = f"{t.value_density():.3f}"
            due_str = f" — due {t.due_date}" if t.due_date else ""
            req_tag = " · required" if t.required else ""
            st.write(
                f"**{t.title}** | {t.duration_minutes} min | {t.priority} priority"
                f"{req_tag} | density {density} | {t.frequency}"
                f" | `{t.status}`{due_str}"
            )
        with col_btn:
            if t.status != "complete" and st.button("Done", key=f"done_{i}"):
                next_task = t.mark_complete()
                if next_task:
                    pet.add_task(next_task)
                    st.success(f"'{t.title}' complete! Next due: {next_task.due_date}")
                else:
                    st.success(f"'{t.title}' marked complete.")
                st.rerun()
else:
    st.info("No tasks yet. Add one above or load defaults.")

st.divider()

# ── Schedule generation ────────────────────────────────────────────────────────
st.subheader("Build Schedule")
st.caption(
    "Required tasks are reserved first. Remaining time fills with optional tasks "
    "sorted by value density (priority ÷ duration)."
)

buffer_minutes = st.slider(
    "Buffer between tasks (min)", min_value=0, max_value=30, value=0, step=5
)

if st.button("Generate schedule", type="primary"):
    if not pet.tasks:
        st.warning("Add at least one task before generating a schedule.")
    else:
        scheduler = Scheduler(
            owner=owner,
            pet=pet,
            tasks=pet.tasks,
            buffer_minutes=buffer_minutes,
        )
        plan = scheduler.generate_plan()

        # ── Conflict detection ─────────────────────────────────────────────────
        conflict_warnings = scheduler.detect_conflicts(plan)
        if conflict_warnings:
            for w in conflict_warnings:
                st.warning(w)
        else:
            st.success(
                f"Schedule built for **{plan.owner_name}** and **{plan.pet_name}** "
                f"— no conflicts detected."
            )

        # ── Schedule table ─────────────────────────────────────────────────────
        if plan.scheduled_items:
            rows = []
            for item in plan.sort_by_time():
                task = item["task"]
                start = item["start_time"]
                hour, minute = start // 60, start % 60
                end = start + task.duration_minutes
                rows.append(
                    {
                        "Start": f"{hour:02d}:{minute:02d}",
                        "End": f"{end // 60:02d}:{end % 60:02d}",
                        "Task": task.title,
                        "Min": task.duration_minutes,
                        "Priority": task.priority,
                        "Required": "yes" if task.required else "no",
                        "Value Density": round(task.value_density(), 3),
                    }
                )
            st.dataframe(rows, use_container_width=True, hide_index=True)

            total = plan.total_duration
            st.caption(
                f"Total scheduled: **{total} min** of {available_minutes} min budget. "
                f"({available_minutes - total} min remaining)"
            )
        else:
            st.info("No tasks fit within the time budget.")

        # ── Dropped tasks ──────────────────────────────────────────────────────
        if plan.dropped_tasks:
            dropped_names = ", ".join(
                f"{t.title} ({t.duration_minutes} min)" for t in plan.dropped_tasks
            )
            st.warning(f"Skipped (didn't fit or dependency unmet): {dropped_names}")

        # ── Reasoning ─────────────────────────────────────────────────────────
        with st.expander("Plan reasoning"):
            st.text(plan.explain())

        with st.expander("How tasks were ranked"):
            st.markdown(
                "Tasks are sorted by **value density = priority score ÷ duration**. "
                "This greedy heuristic fits more high-value work into the time budget. "
                "Required tasks are always reserved before optional ones compete.\n\n"
                "| Priority | Score |\n|---|---|\n"
                "| high | 3 |\n| medium | 2 |\n| low | 1 |"
            )
