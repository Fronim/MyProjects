import random
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session

import models
from database import SessionLocal, engine, Base
from models import ExperimentStatus


def seed_database():
    print("[+] Ініціалізація бази даних та створення таблиць...")
    # Створюємо таблиці, якщо їх ще немає
    Base.metadata.drop_all(bind=engine)  # Скидаємо базу перед сіданням для чистоти тестів
    Base.metadata.create_all(bind=engine)

    db: Session = SessionLocal()

    try:
        print("[+] Наповнення бази тестовими даними...")

        # =====================================================================
        # 1. СТВОРЕННЯ ПРОЄКТІВ
        # =====================================================================
        project_cv = models.Project(
            name="Computer Vision Pipeline",
            description="Розробка та тренування Vision Transformer (ViT) та EfficientNet для детекції deepfake-контенту та артефактів генерації."
        )
        project_trading = models.Project(
            name="Algorithmic Trading Bot",
            description="Оптимізація портфеля за коефіцієнтом Шарпа та розробка ботів для детекції ринкових режимів."
        )
        project_crypto = models.Project(
            name="Cryptography Performance",
            description="Бенчмаркінг та аналіз швидкості криптографічних алгоритмів (RC5, RSA, MD5) під навантаженням."
        )

        db.add_all([project_cv, project_trading, project_crypto])
        db.commit()  # Фіксуємо проєкти, щоб отримати їхні ID

        # =====================================================================
        # 2. ЕКСПЕРИМЕНТИ ДЛЯ COMPUTER VISION
        # =====================================================================
        # Експеримент 1: Успішно завершений (Adam)
        exp_cv_1 = models.Experiment(
            project_id=project_cv.id,
            name="ViT_Base_Adam_LR_1e-4",
            status=ExperimentStatus.completed,
            started_at=datetime.now(timezone.utc) - timedelta(hours=3),
            finished_at=datetime.now(timezone.utc) - timedelta(hours=2)
        )
        # Експеримент 2: Впав посеред навчання (SGD)
        exp_cv_2 = models.Experiment(
            project_id=project_cv.id,
            name="EfficientNet_B4_SGD_LR_1e-2",
            status=ExperimentStatus.failed,
            started_at=datetime.now(timezone.utc) - timedelta(hours=1),
            finished_at=datetime.now(timezone.utc) - timedelta(minutes=40)
        )

        db.add_all([exp_cv_1, exp_cv_2])
        db.commit()

        # Гіперпараметри для CV
        hp_cv_1 = models.Hyperparameters(experiment_id=exp_cv_1.id, learning_rate=0.0001, epochs=15, optimizer="Adam")
        hp_cv_2 = models.Hyperparameters(experiment_id=exp_cv_2.id, learning_rate=0.01, epochs=20, optimizer="SGD")
        db.add_all([hp_cv_1, hp_cv_2])

        # ГЕНЕРАЦІЯ ЛОГІВ ДЛЯ CV ЕКСПЕРИМЕНТІВ
        # Для успішного ViT (Loss стабільно падає з 0.9 до 0.15, Accuracy росте до 0.92)
        loss = 0.92
        accuracy = 0.20
        for epoch in range(1, 16):
            loss = max(0.08, loss - 0.06 + random.uniform(-0.02, 0.02))
            accuracy = min(0.96, accuracy + 0.05 + random.uniform(-0.01, 0.01))
            log = models.MetricLog(
                experiment_id=exp_cv_1.id,
                epoch=epoch,
                loss=round(loss, 4),
                accuracy=round(accuracy, 4),
                timestamp=exp_cv_1.started_at + timedelta(minutes=epoch * 4)
            )
            db.add(log)

        # Для фейлнутого SGD (Loss застряг на 0.7, Accuracy не росте, впав на 6 епосі)
        loss = 0.85
        accuracy = 0.40
        for epoch in range(1, 7):
            loss = loss - 0.02 + random.uniform(-0.03, 0.03)
            accuracy = accuracy + 0.01 + random.uniform(-0.02, 0.02)
            log = models.MetricLog(
                experiment_id=exp_cv_2.id,
                epoch=epoch,
                loss=round(loss, 4),
                accuracy=round(accuracy, 4),
                timestamp=exp_cv_2.started_at + timedelta(minutes=epoch * 3)
            )
            db.add(log)

        # =====================================================================
        # 3. ЕКСПЕРИМЕНТИ ДЛЯ TRADING BOT
        # =====================================================================
        # Експеримент 3: Зараз виконується (AdamW)
        exp_trade_1 = models.Experiment(
            project_id=project_trading.id,
            name="Sharpe_Optimization_LSTM_AdamW",
            status=ExperimentStatus.running,
            started_at=datetime.now(timezone.utc) - timedelta(minutes=15)
        )

        db.add(exp_trade_1)
        db.commit()

        hp_trade_1 = models.Hyperparameters(experiment_id=exp_trade_1.id, learning_rate=0.001, epochs=10,
                                            optimizer="AdamW")
        db.add(hp_trade_1)

        # Логи для запущеного експерименту (встиг пройти лише 4 епохи)
        loss = 0.65
        accuracy = 0.51
        for epoch in range(1, 5):
            loss = max(0.01, loss - 0.04 + random.uniform(-0.01, 0.01))
            accuracy = min(0.99, accuracy + 0.03 + random.uniform(-0.01, 0.01))
            log = models.MetricLog(
                experiment_id=exp_trade_1.id,
                epoch=epoch,
                loss=round(loss, 4),
                accuracy=round(accuracy, 4),
                timestamp=exp_trade_1.started_at + timedelta(minutes=epoch * 2)
            )
            db.add(log)

        # Фінальний комміт усіх метрик
        db.commit()
        print("[+] Базу даних успішно наповнено! Створено 3 проекти та 3 експерименти.")

    except Exception as e:
        db.rollback()
        print(f"[-] Помилка під час наповнення бази: {e}")
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()