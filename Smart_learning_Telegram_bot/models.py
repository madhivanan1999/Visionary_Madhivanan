from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class StudyPlan(Base):
    __tablename__ = "study_plan"
    __table_args__ = {"schema": "vs"}

    study_plan_id = Column(Integer, primary_key=True, index=True)
    universities = Column(String(100), nullable=False)
    stream = Column(String(100), nullable=False)
    departments = Column(String(100), nullable=False)
    subjects = Column(String(100))
    sem = Column(Integer, nullable=False)
    module_no = Column(Integer, nullable=False)
    model_description = Column(String(100))
    topics = Column(String(200))


class UserBasicInfo(Base):
    __tablename__ = "user_basic_info"
    __table_args__ = {"schema": "vs"}

    student_id = Column(Integer, primary_key=True, index=True)
    student_name = Column(String(100), nullable=False)
    university = Column(String(100), nullable=False)
    college_name = Column(String(100), nullable=False)
    stream = Column(String(100), nullable=False)
    std_year = Column(Integer, nullable=False)
    department = Column(String(100), nullable=False)
    sem = Column(Integer, nullable=False)
    mobile_no = Column(String(15), unique=True, nullable=False)
    email_id = Column(String(100), unique=True, nullable=False)
    telegram_id = Column(String(50), unique=True, nullable=False)

    activities = relationship(
        "StudentActivity",
        back_populates="student",
        cascade="all, delete"
    )


class StudentActivity(Base):
    __tablename__ = "student_activity"
    __table_args__ = {"schema": "vs"}

    id_no = Column(Integer, primary_key=True, index=True)
    student_id = Column(
        Integer,
        ForeignKey("vs.user_basic_info.student_id", ondelete="CASCADE"),
        nullable=False,
    )
    study_plan_id = Column(
        Integer,
        ForeignKey("vs.study_plan.study_plan_id", ondelete="CASCADE"),
        nullable=False,
    )
    is_done = Column(String(50), nullable=False, default="No")
    mark = Column(Integer, default=0)

    student = relationship("UserBasicInfo", back_populates="activities")
    study_plan = relationship("StudyPlan")