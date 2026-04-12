from services import (
    get_pending_task,
    complete_task,
    get_user_by_telegram_id
)

# -------------------------------
# PostgreSQL Tools
# -------------------------------

def fetch_user(telegram_id: str):
    user = get_user_by_telegram_id(telegram_id)
    if not user:
        return {"error": "User not found"}

    return {
        "student_name": user.student_name,
        "university": user.university,
        "stream": user.stream,
        "department": user.department,
        "sem": user.sem,
    }


def fetch_pending_task(telegram_id: str):
    task = get_pending_task(telegram_id)
    if not task:
        return {"message": "No pending tasks"}

    return {
        "subject": task.subjects,
        "topic": task.topics,
        "module": task.module_no,
        "description": task.model_description,
    }


def mark_task_complete(telegram_id: str):
    task = complete_task(telegram_id)
    if not task:
        return {"message": "No active task"}

    return {
        "status": "completed",
        "subject": task.subjects,
        "topic": task.topics,
    }


# -------------------------------
# MCP Tool Registry
# -------------------------------

MCP_TOOLS = {
    "fetch_user": fetch_user,
    "fetch_pending_task": fetch_pending_task,
    "mark_task_complete": mark_task_complete,
}