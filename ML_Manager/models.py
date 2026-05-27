import enum
from datetime import datetime
from typing import List, Optional

from sqlalchemy import ForeignKey, String, Float, Integer, Enum, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from database import Base


# Перелічення для статусів експерименту
class ExperimentStatus(str, enum.Enum):
    running = "running"
    completed = "completed"
    failed = "failed"


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Один-до-багатьох: один проєкт має багато експериментів
    # cascade="all, delete-orphan" забезпечує видалення експериментів при видаленні проєкту
    experiments: Mapped[List["Experiment"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )


class Experiment(Base):
    __tablename__ = "experiments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    name: Mapped[str] = mapped_column(String(150), index=True)
    status: Mapped[ExperimentStatus] = mapped_column(Enum(ExperimentStatus), default=ExperimentStatus.running)

    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Зв'язки
    project: Mapped["Project"] = relationship(back_populates="experiments")

    # Один-до-одного: використовуємо uselist=False
    hyperparameters: Mapped[Optional["Hyperparameters"]] = relationship(
        back_populates="experiment", uselist=False, cascade="all, delete-orphan"
    )

    # Один-до-багатьох: експеримент має багато логів
    metric_logs: Mapped[List["MetricLog"]] = relationship(
        back_populates="experiment", cascade="all, delete-orphan"
    )


class Hyperparameters(Base):
    __tablename__ = "hyperparameters"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    # unique=True гарантує зв'язок один-до-одного на рівні БД
    experiment_id: Mapped[int] = mapped_column(ForeignKey("experiments.id"), unique=True)

    learning_rate: Mapped[float] = mapped_column(Float)
    epochs: Mapped[int] = mapped_column(Integer)
    optimizer: Mapped[str] = mapped_column(String(50))

    # Зворотний зв'язок
    experiment: Mapped["Experiment"] = relationship(back_populates="hyperparameters")


class MetricLog(Base):
    __tablename__ = "metric_logs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    experiment_id: Mapped[int] = mapped_column(ForeignKey("experiments.id"), index=True)

    epoch: Mapped[int] = mapped_column(Integer)
    loss: Mapped[float] = mapped_column(Float)
    accuracy: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Зворотний зв'язок
    experiment: Mapped["Experiment"] = relationship(back_populates="metric_logs")