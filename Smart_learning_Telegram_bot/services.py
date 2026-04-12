from sqlalchemy.orm import Session
from database import SessionLocal
from models import UserBasicInfo, StudyPlan, StudentActivity


# -------------------------------
# DB SESSION
# -------------------------------
def get_db() -> Session:
    return SessionLocal()


# -------------------------------
# GET USER
# -------------------------------
def get_user_by_telegram_id(telegram_id: str):
    db = get_db()
    try:
        return db.query(UserBasicInfo).filter_by(
            telegram_id=telegram_id
        ).first()
    finally:
        db.close()


# -------------------------------
# REGISTER USER
# -------------------------------
def register_user_full(user_data: dict):
    db = get_db()
    try:
        user = db.query(UserBasicInfo).filter_by(
            telegram_id=user_data["telegram_id"]
        ).first()

        if user:
            return user

        allowed_fields = {
            "student_name",
            "university",
            "college_name",
            "stream",
            "std_year",
            "department",
            "sem",
            "mobile_no",
            "email_id",
            "telegram_id",
        }

        filtered = {k: v for k, v in user_data.items() if k in allowed_fields}

        # normalize
        filtered["university"] = filtered["university"].lower()
        filtered["stream"] = filtered["stream"].lower()
        filtered["department"] = filtered["department"].lower()

        user = UserBasicInfo(**filtered)

        db.add(user)
        db.commit()
        db.refresh(user)

        # 🔥 Assign FIRST task immediately
        assign_task(db, user)

        return user

    finally:
        db.close()


# -------------------------------
# ASSIGN NEXT TASK
# -------------------------------
def assign_task(db: Session, student):
    try:
        # ✅ Get completed task IDs
        done_ids = db.query(StudentActivity.study_plan_id).filter_by(
            student_id=student.student_id,
            is_done=True
        ).all()

        done_ids = [d[0] for d in done_ids]

        # ✅ Build query safely
        query = db.query(StudyPlan).filter(
            StudyPlan.universities == student.university,
            StudyPlan.stream == student.stream,
            StudyPlan.departments == student.department,
            StudyPlan.sem == student.sem,
        )

        if done_ids:
            query = query.filter(~StudyPlan.study_plan_id.in_(done_ids))

        task = query.order_by(StudyPlan.study_plan_id).first()

        if not task:
            return None

        # ✅ Prevent duplicate
        existing = db.query(StudentActivity).filter_by(
            student_id=student.student_id,
            study_plan_id=task.study_plan_id
        ).first()

        if not existing:
            activity = StudentActivity(
                student_id=student.student_id,
                study_plan_id=task.study_plan_id,
                is_done=False,
                mark=0
            )
            db.add(activity)
            db.commit()

        return task

    except Exception as e:
        print("ERROR in assign_task:", e)
        return None


# -------------------------------
# GET CURRENT TASK
# -------------------------------
def get_pending_task(telegram_id: str):
    db = get_db()
    try:
        user = db.query(UserBasicInfo).filter_by(
            telegram_id=telegram_id
        ).first()

        if not user:
            return None

        # ✅ Try to get current task
        activity = db.query(StudentActivity).filter_by(
            student_id=user.student_id,
            is_done=False
        ).first()

        # 🔥 If no task → assign first task
        if not activity:
            task = assign_task(db, user)
            return task

        return db.query(StudyPlan).filter_by(
            study_plan_id=activity.study_plan_id
        ).first()

    finally:
        db.close()


# -------------------------------
# COMPLETE TASK + AUTO NEXT
# -------------------------------
def complete_task(telegram_id: str):
    db = get_db()
    try:
        user = db.query(UserBasicInfo).filter_by(
            telegram_id=telegram_id
        ).first()

        if not user:
            return None

        # ✅ Get current task
        activity = db.query(StudentActivity).filter_by(
            student_id=user.student_id,
            is_done=False
        ).first()

        if not activity:
            return None

        # ✅ Mark complete
        activity.is_done = True
        activity.mark = 100

        db.commit()

        # 🔥 Assign next task
        next_task = assign_task(db, user)

        return next_task

    except Exception as e:
        print("ERROR in complete_task:", e)
        return None

    finally:
        db.close()


# -------------------------------
# DELETE USER
# -------------------------------
def delete_user_by_telegram_id(telegram_id: str):
    db = get_db()
    try:
        user = db.query(UserBasicInfo).filter_by(
            telegram_id=telegram_id
        ).first()

        if not user:
            return False

        db.delete(user)
        db.commit()
        return True

    finally:
        db.close()