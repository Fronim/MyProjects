from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field, model_validator
from models import ExperimentStatus


# ==========================================
# METRIC LOG SCHEMAS
# ==========================================
class MetricLogBase(BaseModel):
    epoch: int = Field(..., ge=0, description="Номер епохи навчання")
    loss: float = Field(..., description="Значення функції втрат (Loss)")
    accuracy: Optional[float] = Field(None, ge=0.0, le=1.0, description="Метрика точності моделі (Accuracy)")


class MetricLogCreate(MetricLogBase):
    pass


class MetricLogResponse(MetricLogBase):
    id: int
    experiment_id: int
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# HYPERPARAMETERS SCHEMAS
# ==========================================
class HyperparametersBase(BaseModel):
    learning_rate: float = Field(..., gt=0, description="Швидкість навчання (Learning Rate)")
    epochs: int = Field(..., gt=0, description="Загальна кількість епох для тренування")
    optimizer: str = Field(..., max_length=50, description="Назва оптимізатора (напр., 'Adam', 'SGD', 'RMSprop')")


class HyperparametersCreate(HyperparametersBase):
    pass


class HyperparametersResponse(HyperparametersBase):
    id: int
    experiment_id: int

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# EXPERIMENT SCHEMAS
# ==========================================
class ExperimentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=150, description="Назва або короткий опис експерименту")
    status: ExperimentStatus = Field(default=ExperimentStatus.running, description="Поточний статус виконання")


class ExperimentCreate(ExperimentBase):
    project_id: int


class ExperimentResponse(ExperimentBase):
    id: int
    project_id: int
    started_at: datetime
    finished_at: Optional[datetime] = None

    # Вкладені поля згідно з вимогами архітектури
    hyperparameters: Optional[HyperparametersResponse] = None
    metrics_count: int = Field(0, description="Загальна кількість залогованих метрик для цього експерименту")

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="before")
    @classmethod
    def custom_orm_mapping(cls, data):
        """
        Senior-патерн: Замість того, щоб серіалізувати тисячі логів метрик (що вб'є перформанс API),
        ми використовуємо model_validator для швидкого підрахунку кількості елементів прямо з SQLAlchemy relationship.
        """
        if not isinstance(data, dict):
            # Якщо data — це SQLAlchemy об'єкт (lazy loading підтягне зв'язки, якщо вони завантажені)
            return {
                "id": data.id,
                "project_id": data.project_id,
                "name": data.name,
                "status": data.status,
                "started_at": data.started_at,
                "finished_at": data.finished_at,
                "hyperparameters": data.hyperparameters,
                "metrics_count": len(data.metric_logs) if data.metric_logs else 0
            }
        else:
            # Якщо дані прийшли у вигляді звичайного словника
            data["metrics_count"] = len(data.get("metric_logs", []))
        return data


# ==========================================
# PROJECT SCHEMAS
# ==========================================
class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Унікальна назва проєкту")
    description: Optional[str] = Field(None, max_length=500, description="Детальний опис бізнес-задачі або датасету")


class ProjectCreate(ProjectBase):
    pass


class ProjectResponse(ProjectBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)