from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session, joinedload
from typing import List

import models
import schemas
from database import SessionLocal, engine, Base

import asyncio
from datetime import datetime, timezone
from fastapi import WebSocket, WebSocketDisconnect

# Створюємо таблиці в базі даних (у продакшені для цього використовують Alembic)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ML Experiment Tracker API",
    description="Бекенд для трекінгу гіперпараметрів та метрик машинного навчання",
    version="1.0.0"
)

# Налаштування CORS для підключення фронтенду (React/Vue/Vite)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],  # Дозволяємо всі методи (GET, POST, PUT, DELETE, OPTIONS)
    allow_headers=["*"],  # Дозволяємо всі заголовки
)


# Залежність (Dependency) для безпечного отримання та закриття сесії БД
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==========================================
# PROJECTS ENDPOINTS
# ==========================================

@app.get("/projects", response_model=List[schemas.ProjectResponse])
async def get_projects(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    projects = db.query(models.Project).offset(skip).limit(limit).all()
    return projects


@app.post("/projects", response_model=schemas.ProjectResponse, status_code=201)
async def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db)):
    # Перевірка, чи не існує вже проєкт з такою назвою
    db_project = db.query(models.Project).filter(models.Project.name == project.name).first()
    if db_project:
        raise HTTPException(status_code=400, detail="Проєкт з такою назвою вже існує")

    new_project = models.Project(**project.model_dump())
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return new_project


# ==========================================
# EXPERIMENTS ENDPOINTS
# ==========================================

@app.get("/projects/{project_id}/experiments", response_model=List[schemas.ExperimentResponse])
async def get_project_experiments(project_id: int, db: Session = Depends(get_db)):
    # Перевіряємо, чи існує проєкт
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Проєкт не знайдено")

    # Senior-патерн: використовуємо joinedload для уникнення проблеми N+1.
    # Це завантажить всі пов'язані метрики та гіперпараметри одним SQL-запитом,
    # що дозволить Pydantic validator'у (`metrics_count`) відпрацювати миттєво.
    experiments = (
        db.query(models.Experiment)
        .options(
            joinedload(models.Experiment.hyperparameters),
            joinedload(models.Experiment.metric_logs)
        )
        .filter(models.Experiment.project_id == project_id)
        .all()
    )
    return experiments


@app.post("/projects/{project_id}/experiments", response_model=schemas.ExperimentResponse, status_code=201)
async def create_experiment(
        project_id: int,
        experiment: schemas.ExperimentCreate,
        db: Session = Depends(get_db)
):
    # Перевіряємо, чи існує проєкт
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Проєкт не знайдено")

    if experiment.project_id != project_id:
        raise HTTPException(status_code=400, detail="project_id в URL та тілі запиту не співпадають")

    new_experiment = models.Experiment(**experiment.model_dump())
    db.add(new_experiment)
    db.commit()
    db.refresh(new_experiment)
    return new_experiment


# ==========================================
# METRICS ENDPOINTS
# ==========================================

@app.get("/experiments/{experiment_id}/metrics", response_model=List[schemas.MetricLogResponse])
async def get_experiment_metrics(experiment_id: int, db: Session = Depends(get_db)):
    # Перевіряємо, чи існує експеримент
    experiment = db.query(models.Experiment).filter(models.Experiment.id == experiment_id).first()
    if not experiment:
        raise HTTPException(status_code=404, detail="Експеримент не знайдено")

    metrics = (
        db.query(models.MetricLog)
        .filter(models.MetricLog.experiment_id == experiment_id)
        .order_by(models.MetricLog.epoch.asc())  # Сортуємо по епохах для коректної побудови графіків
        .all()
    )
    return metrics


@app.websocket("/ws/experiments/{experiment_id}/stream")
async def experiment_stream(websocket: WebSocket, experiment_id: int):
    # Приймаємо підключення від клієнта (фронтенду або тренінг-скрипта)
    await websocket.accept()

    # Відкриваємо окрему сесію БД для цього вебсокет-з'єднання
    db = SessionLocal()
    try:
        # Завантажуємо експеримент разом із його гіперпараметрами
        experiment = (
            db.query(models.Experiment)
            .options(joinedload(models.Experiment.hyperparameters))
            .filter(models.Experiment.id == experiment_id)
            .first()
        )

        if not experiment:
            await websocket.send_json({"error": f"Експеримент {experiment_id} не знайдено"})
            await websocket.close(code=4004)
            return

        if not experiment.hyperparameters:
            await websocket.send_json({"error": "Для цього експерименту не задані гіперпараметри (epochs)"})
            await websocket.close(code=4000)
            return

        # Переводимо експеримент у статус running, якщо він був у іншому стані
        if experiment.status != models.ExperimentStatus.running:
            experiment.status = models.ExperimentStatus.running
            db.commit()

        max_epochs = experiment.hyperparameters.epochs

        # Визначаємо стартову епоху. Якщо експеримент перезапустили,
        # продовжуємо з останньої залогованої епохи, інакше — з 1.
        last_log = (
            db.query(models.MetricLog)
            .filter(models.MetricLog.experiment_id == experiment_id)
            .order_by(models.MetricLog.epoch.desc())
            .first()
        )

        current_epoch = last_log.epoch + 1 if last_log else 1

        # Початкові значення для симуляції ML-процесу
        current_loss = last_log.loss if last_log else 0.85
        current_accuracy = last_log.accuracy if (last_log and last_log.accuracy) else 0.15

        # Головний цикл симуляції навчання
        while current_epoch <= max_epochs:
            await asyncio.sleep(1)  # Затримка в 1 секунду між епохами

            # Симулюємо адекватну поведінку нейромережі: loss падає, accuracy росте
            current_loss = max(0.01, current_loss - 0.05)
            current_accuracy = min(0.99, current_accuracy + 0.04)

            # Створюємо новий запис метрики в БД
            new_log = models.MetricLog(
                experiment_id=experiment_id,
                epoch=current_epoch,
                loss=round(current_loss, 4),
                accuracy=round(current_accuracy, 4)
            )
            db.add(new_log)
            db.commit()
            db.refresh(new_log)

            # Senior-патерн: Серіалізуємо об'єкт через Pydantic.
            # mode="json" автоматично конвертує об'єкти datetime у валідні JSON-стрічки.
            log_data = schemas.MetricLogResponse.model_validate(new_log).model_dump(mode="json")

            # Миттєво відправляємо метрику на фронтенд
            await websocket.send_json({
                "event": "metric_logged",
                "data": log_data
            })

            current_epoch += 1

        # Якщо цикл завершився успішно (досягли max_epochs) — оновлюємо статус експерименту
        experiment.status = models.ExperimentStatus.completed
        experiment.finished_at = datetime.now(timezone.utc)
        db.commit()

        # Повідомляємо клієнта про успішне завершення
        await websocket.send_json({
            "event": "experiment_completed",
            "message": f"Експеримент успішно завершено після {max_epochs} епох."
        })
        await websocket.close(code=1000)

    except WebSocketDisconnect:
        # Важливий блок: якщо користувач закрив вкладку браузера або розірвав з'єднання
        print(f"[-] Клієнт відключився від стріму експерименту {experiment_id}")

        # Опціонально: якщо з'єднання зникло посеред процесу, маркуємо експеримент як failed
        # Але оскільки це симуляція, ми можемо або залишити як є, або зафіксувати статус:
        experiment = db.query(models.Experiment).filter(models.Experiment.id == experiment_id).first()
        if experiment and experiment.status == models.ExperimentStatus.running:
            experiment.status = models.ExperimentStatus.failed
            experiment.finished_at = datetime.now(timezone.utc)
            db.commit()

    finally:
        # Гарантовано закриваємо сесію SQLAlchemy, щоб уникнути витоку пам'яті та блокувань БД
        db.close()