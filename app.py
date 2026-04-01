import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Quick Demo Inputs (UI only)")
owner_name = st.text_input("Owner name", value="Jordan")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

if "owner" not in st.session_state:
    st.session_state.owner = Owner(name=owner_name, available_minutes=120)

if "pet" not in st.session_state:
    st.session_state.pet = Pet(name=pet_name, species=species)

st.markdown("### Tasks")
st.caption("Add a few tasks. These feed directly into your scheduler.")

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
with col4:
    required = st.checkbox("Required", value=False)
with col5:
    frequency = st.selectbox("Frequency", ["once", "daily", "weekly"])

if st.button("Add task"):
    new_task = Task(title=task_title, duration_minutes=int(duration), priority=priority,
                    required=required, frequency=frequency)
    st.session_state.pet.add_task(new_task)

if st.session_state.pet.tasks:
    st.write("Current tasks:")
    for i, t in enumerate(st.session_state.pet.tasks):
        col_info, col_btn = st.columns([5, 1])
        with col_info:
            due_str = f" — due {t.due_date}" if t.due_date else ""
            st.write(
                f"**{t.title}** | {t.duration_minutes} min | {t.priority} priority "
                f"| {t.frequency} | {'required' if t.required else 'optional'} "
                f"| status: `{t.status}`{due_str}"
            )
        with col_btn:
            if t.status != "complete" and st.button("✓ Done", key=f"complete_{i}"):
                next_task = t.mark_complete()
                if next_task:
                    st.session_state.pet.add_task(next_task)
                    st.success(f"'{t.title}' complete! Next due: {next_task.due_date}")
                else:
                    st.success(f"'{t.title}' marked complete.")
                st.rerun()
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("Generates a daily plan sorted by priority, filtered to fit available time.")

buffer_minutes = st.slider("Buffer between tasks (minutes)", min_value=0, max_value=30, value=0, step=5)

if st.button("Generate schedule"):
    scheduler = Scheduler(
        owner=st.session_state.owner,
        pet=st.session_state.pet,
        tasks=st.session_state.pet.tasks,
        buffer_minutes=buffer_minutes,
    )
    plan = scheduler.generate_plan()
    st.success(f"Schedule built for {plan.owner_name} and {plan.pet_name}!")
    st.table(plan.display())
    if plan.dropped_tasks:
        st.warning(
            "Skipped (didn't fit): "
            + ", ".join(f"{t.title} ({t.duration_minutes} min)" for t in plan.dropped_tasks)
        )
    st.markdown("**Plan summary:**")
    st.text(plan.explain())
