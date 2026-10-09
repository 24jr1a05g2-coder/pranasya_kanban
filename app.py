
import sqlite3
from datetime import date

import streamlit as st
from streamlit_sortables import sort_items


# =====================================================
# 1. PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="Pranasya's Smart Kanban Board",
    page_icon="📋",
    layout="wide"
)


# =====================================================
# 2. PROFESSIONAL PASTEL CSS
# =====================================================

st.markdown("""
<style>
/* Main background */
.stApp {
    background: linear-gradient(
        135deg,
        #f8faff 0%,
        #f3f0ff 50%,
        #effbff 100%
    );
}

/* Main title */
h1 {
    color: #51458c;
    font-weight: 800;
    letter-spacing: -1px;
}

/* Section headings */
h2, h3 {
    color: #435578;
    font-weight: 700;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #e8eaff 0%,
        #e4f4ff 100%
    );
    border-right: 1px solid #dce4f5;
}

/* Dashboard metric cards */
div[data-testid="stMetric"] {
    background: linear-gradient(
        145deg,
        #ffffff,
        #f4f6ff
    );
    padding: 20px;
    border-radius: 18px;
    border: 1px solid #e0e5fa;
    box-shadow: 0 5px 15px rgba(99, 102, 180, 0.08);
}

/* Dashboard metric values */
[data-testid="stMetricValue"] {
    color: #6256a6;
    font-weight: 800;
}

/* Task containers */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: rgba(255, 255, 255, 0.92);
    border-radius: 16px;
    border: 1px solid #e2e7f4;
    padding: 12px;
    box-shadow: 0 3px 12px rgba(67, 85, 120, 0.05);
}

/* Buttons */
.stButton button,
.stFormSubmitButton button {
    background: linear-gradient(
        135deg,
        #8b83e6,
        #7773d9
    );
    color: white;
    border: none;
    border-radius: 10px;
    font-weight: 600;
    transition: all 0.2s ease;
}

/* Button hover */
.stButton button:hover,
.stFormSubmitButton button:hover {
    background: linear-gradient(
        135deg,
        #756bd3,
        #625ac4
    );
    color: white;
    border: none;
}

/* Input fields */
.stTextInput input,
.stDateInput input {
    background-color: #ffffff;
    border-radius: 10px;
}

/* Expanders */
[data-testid="stExpander"] {
    background-color: #ffffff;
    border: 1px solid #e2e7f4;
    border-radius: 14px;
}

/* Progress bar */
.stProgress > div > div > div {
    background: linear-gradient(
        90deg,
        #8b83e6,
        #7bd8d0
    );
    border-radius: 10px;
}

/* Dividers */
hr {
    border-color: #dfe5f4;
}

/* Alert messages */
[data-testid="stAlert"] {
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)


# =====================================================
# 3. HEADER
# =====================================================

st.title("📋 Pranasya's Smart Kanban Board")
st.caption("✨ Organize your work. Track your progress. Achieve your goals.")

st.divider()


# =====================================================
# 4. DATABASE CONNECTION
# =====================================================

def get_connection():
    return sqlite3.connect("kanban.db")


# =====================================================
# 5. CREATE DATABASE TABLE
# =====================================================

with get_connection() as conn:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            status TEXT NOT NULL,
            priority TEXT NOT NULL,
            deadline TEXT
        )
    """)


# =====================================================
# 6. FETCH TASKS
# =====================================================

def fetch_tasks():
    with get_connection() as conn:
        return conn.execute("""
            SELECT id, name, status, priority, deadline
            FROM tasks
            ORDER BY id
        """).fetchall()


# =====================================================
# 7. ADD NEW TASK
# =====================================================

st.sidebar.title("✨ Task Manager")
st.sidebar.header("➕ Add a New Task")

statuses = ["To Do", "In Progress", "Done"]
priorities = ["Low", "Medium", "High"]

with st.sidebar.form("add_task_form", clear_on_submit=True):

    task_name = st.text_input(
        "Task Name",
        placeholder="What do you need to do?"
    )

    task_priority = st.selectbox(
        "Priority",
        priorities
    )

    task_deadline = st.date_input(
        "Deadline",
        value=date.today()
    )

    task_status = st.selectbox(
        "Initial Status",
        statuses
    )

    add_button = st.form_submit_button(
        "➕ Add Task",
        use_container_width=True
    )

    if add_button:
        if task_name.strip():
            with get_connection() as conn:
                conn.execute("""
                    INSERT INTO tasks
                    (name, status, priority, deadline)
                    VALUES (?, ?, ?, ?)
                """, (
                    task_name.strip(),
                    task_status,
                    task_priority,
                    task_deadline.isoformat()
                ))

            st.sidebar.success("Task added successfully!")
            st.rerun()

        else:
            st.sidebar.warning("Please enter a task name.")


# =====================================================
# 8. PROJECT DASHBOARD
# =====================================================

all_tasks = fetch_tasks()

total_tasks = len(all_tasks)

todo_count = sum(
    1 for task in all_tasks
    if task[2] == "To Do"
)

progress_count = sum(
    1 for task in all_tasks
    if task[2] == "In Progress"
)

done_count = sum(
    1 for task in all_tasks
    if task[2] == "Done"
)

st.subheader("📊 Project Dashboard")

c1, c2, c3, c4 = st.columns(4)

c1.metric("📋 Total Tasks", total_tasks)
c2.metric("📝 To Do", todo_count)
c3.metric("⚡ In Progress", progress_count)
c4.metric("✅ Completed", done_count)

completion = (
    done_count / total_tasks
    if total_tasks > 0
    else 0
)

st.write("**Project Completion**")
st.progress(completion)
st.caption(f"{completion:.0%} of all tasks completed.")

st.divider()


# =====================================================
# 9. DRAG-AND-DROP KANBAN BOARD
# =====================================================

st.subheader("🗂️ My Kanban Board")
st.caption("Drag a task card into another column to update its status.")

all_tasks = fetch_tasks()

task_map = {
    f"#{task[0]} | {task[1]}": task
    for task in all_tasks
}

items = [
    {
        "header": status,
        "items": [
            f"#{task[0]} | {task[1]}"
            for task in all_tasks
            if task[2] == status
        ]
    }
    for status in statuses
]

new_items = sort_items(
    items,
    multi_containers=True,
    key="smartkanban_drag_board"
)

# Save status changes from drag-and-drop.
with get_connection() as conn:
    for column in new_items:
        new_status = column.get("header")

        if new_status not in statuses:
            continue

        for task_label in column.get("items", []):
            task = task_map.get(task_label)

            if task is not None and task[2] != new_status:
                conn.execute("""
                    UPDATE tasks
                    SET status = ?
                    WHERE id = ?
                """, (new_status, task[0]))


# =====================================================
# 10. TASK DETAILS, EDIT AND DELETE
# =====================================================

st.divider()
st.subheader("📝 Manage Your Tasks")

all_tasks = fetch_tasks()

if not all_tasks:
    st.info(
        "🌱 Your board is empty. Add your first task using the sidebar!"
    )

for task in all_tasks:

    task_id, name, status, priority, deadline = task

    with st.container(border=True):

        left, middle, right = st.columns([3, 2, 2])

        with left:
            st.markdown(f"### 📌 {name}")
            st.caption(f"Task ID: {task_id}")

        with middle:
            st.write(f"📍 **Status:** {status}")
            st.write(f"🎯 **Priority:** {priority}")

        with right:
            st.write(f"📅 **Deadline:** {deadline or 'Not set'}")

        # -----------------------------
        # EDIT TASK
        # -----------------------------

        with st.expander("✏️ Edit Task"):

            with st.form(f"edit_task_{task_id}"):

                edited_name = st.text_input(
                    "Task Name",
                    value=name,
                    key=f"name_{task_id}"
                )

                edited_priority = st.selectbox(
                    "Priority",
                    priorities,
                    index=priorities.index(priority),
                    key=f"priority_{task_id}"
                )

                edited_status = st.selectbox(
                    "Status",
                    statuses,
                    index=statuses.index(status),
                    key=f"status_{task_id}"
                )

                try:
                    default_deadline = (
                        date.fromisoformat(deadline)
                        if deadline
                        else date.today()
                    )
                except ValueError:
                    default_deadline = date.today()

                edited_deadline = st.date_input(
                    "Deadline",
                    value=default_deadline,
                    key=f"deadline_{task_id}"
                )

                save_button = st.form_submit_button(
                    "💾 Save Changes"
                )

                if save_button:

                    if edited_name.strip():

                        with get_connection() as conn:
                            conn.execute("""
                                UPDATE tasks
                                SET name = ?,
                                    priority = ?,
                                    status = ?,
                                    deadline = ?
                                WHERE id = ?
                            """, (
                                edited_name.strip(),
                                edited_priority,
                                edited_status,
                                edited_deadline.isoformat(),
                                task_id
                            ))

                        st.success("Task updated successfully!")
                        st.rerun()

                    else:
                        st.warning("Task name cannot be empty.")

        # -----------------------------
        # DELETE TASK
        # -----------------------------

        if st.button(
            "🗑️ Delete Task",
            key=f"delete_{task_id}"
        ):

            with get_connection() as conn:
                conn.execute(
                    "DELETE FROM tasks WHERE id = ?",
                    (task_id,)
                )

            st.rerun()


# =====================================================
# 11. FOOTER
# =====================================================

st.divider()

st.markdown(
    "<center>💜 Built with Python, Streamlit and SQLite"
    " | Pranasya's Smart Kanban Board</center>",
    unsafe_allow_html=True
)