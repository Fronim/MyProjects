import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
import itertools
from OptimizationMethodsComparison.LinearRegression import LinearRegression

def plot_optimization_results(res_bgd, res_mbgd, res_adam):
    # Встановлюємо приємний стиль графіків
    sns.set_theme(style="whitegrid")

    # ---------------------------------------------------------
    # ЧАСТИНА 1: Індивідуальні графіки (Train vs Val)
    # ---------------------------------------------------------
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))

    # Пакуємо результати в словник для зручної ітерації
    results = {
        "Batch Gradient Descent": (res_bgd, "#1f77b4"),  # Синій
        "Mini-Batch SGD": (res_mbgd, "#2ca02c"),  # Зелений
        "Adam (Mini-Batch)": (res_adam, "#d62728")  # Червоний
    }

    for ax, (title, (res, color)) in zip(axes, results.items()):
        epochs = range(res["epochs_run"])

        # Тренувальна помилка (суцільна лінія)
        ax.plot(epochs, res["loss_history"], label="Train Loss", color=color, linewidth=2)

        # Валідаційна помилка (пунктирна лінія), якщо вона передана
        if res.get("val_loss_history"):
            ax.plot(epochs, res["val_loss_history"], label="Validation Loss", color=color, linestyle="--", alpha=0.8)

        ax.set_title(f"{title}\n(Зійшлося за {res['epochs_run']} епох)", fontsize=14, pad=10)
        ax.set_xlabel("Епохи", fontsize=12)
        ax.set_ylabel("MSE Loss", fontsize=12)
        ax.legend()

    plt.tight_layout()
    plt.show()

    # ---------------------------------------------------------
    # ЧАСТИНА 2: Пряме зіткнення (Порівняння швидкості збіжності)
    # ---------------------------------------------------------
    plt.figure(figsize=(10, 6))

    plt.plot(range(res_bgd["epochs_run"]), res_bgd["loss_history"],
             label=f'BGD (Епох: {res_bgd["epochs_run"]})', color="#1f77b4", linewidth=2)

    plt.plot(range(res_mbgd["epochs_run"]), res_mbgd["loss_history"],
             label=f'Mini-Batch SGD (Епох: {res_mbgd["epochs_run"]})', color="#2ca02c", linewidth=2)

    plt.plot(range(res_adam["epochs_run"]), res_adam["loss_history"],
             label=f'Adam (Епох: {res_adam["epochs_run"]})', color="#d62728", linewidth=2)

    plt.title("Порівняння алгоритмів оптимізації (Train Loss)", fontsize=16, pad=15)
    plt.xlabel("Епохи", fontsize=12)
    plt.ylabel("MSE Loss", fontsize=12)

    # Обмежуємо вісь Y трохи вище мінімального лоссу для кращої деталізації
    all_losses = res_bgd["loss_history"] + res_mbgd["loss_history"] + res_adam["loss_history"]
    plt.ylim(min(all_losses) * 0.95, np.percentile(all_losses, 80))  # Зрізаємо верхні 20% початкового шуму

    plt.legend(fontsize=12)
    # ---------------------------------------------------------
    # ЧАСТИНА 3: Справжня гонка (Loss vs Time)
    # ---------------------------------------------------------
    plt.figure(figsize=(10, 6))

    plt.plot(res_bgd["time_history"], res_bgd["loss_history"],
             label=f'BGD', color="#1f77b4", linewidth=2)

    plt.plot(res_mbgd["time_history"], res_mbgd["loss_history"],
             label=f'Mini-Batch SGD', color="#2ca02c", linewidth=2)

    plt.plot(res_adam["time_history"], res_adam["loss_history"],
             label=f'Adam', color="#d62728", linewidth=2)

    plt.title("Абсолютно чесне порівняння: Loss vs Час (секунди)", fontsize=16, pad=15)
    plt.xlabel("Час (секунди)", fontsize=12)
    plt.ylabel("MSE Loss", fontsize=12)

    # Знову ж таки, обрізаємо верхівку для кращої деталізації
    plt.ylim(min(all_losses) * 0.95, np.percentile(all_losses, 80))

    plt.legend(fontsize=12)
    plt.show()


def plot_summary_bars(model_bgd, model_mbgd, model_adam,
                      res_bgd, res_mbgd, res_adam,
                      X_test, y_test):
    sns.set_theme(style="whitegrid")

    # Підготовка даних для графіків
    labels = ["BGD", "Mini-Batch SGD", "Adam"]
    colors = ["#1f77b4", "#2ca02c", "#d62728"]

    # 1. Отримуємо фінальний R^2 на тестовій вибірці
    r2_scores = [
        model_bgd.evaluate_r(X_test, y_test),
        model_mbgd.evaluate_r(X_test, y_test),
        model_adam.evaluate_r(X_test, y_test)
    ]

    # 2. Дістаємо загальний час виконання (останнє значення в списку time_history)
    times = [
        res_bgd["time_history"][-1],
        res_mbgd["time_history"][-1],
        res_adam["time_history"][-1]
    ]

    # Створюємо полотно для двох графіків поруч
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # ---------------------------------------------------------
    # Графік 1: Порівняння R^2 Score
    # ---------------------------------------------------------
    sns.barplot(x=labels, y=r2_scores, ax=axes[0], hue=labels)
    axes[0].set_title("Фінальна точність (R² Score на Test)", fontsize=15, pad=15)
    axes[0].set_ylabel("R² Score", fontsize=12)

    # Обмежуємо вісь Y, щоб графік виглядав логічно (R^2 зазвичай до 1.0)
    # Якщо ваші R^2 дуже близькі (напр. 0.98), можна зробити зріз осі Y для контрасту
    min_r2 = min(r2_scores)
    axes[0].set_ylim(min_r2 * 0.95 if min_r2 > 0 else 0, max(r2_scores) * 1.05)

    # Додаємо точні значення над кожним стовпчиком
    for i, v in enumerate(r2_scores):
        axes[0].text(i, v + (max(r2_scores) * 0.005), f"{v:.4f}",
                     ha='center', va='bottom', fontweight='bold', fontsize=12)

    # ---------------------------------------------------------
    # Графік 2: Порівняння Часу виконання
    # ---------------------------------------------------------
    sns.barplot(x=labels, y=times, ax=axes[1], hue=labels)
    axes[1].set_title("Загальний час збіжності", fontsize=15, pad=15)
    axes[1].set_ylabel("Час (секунди)", fontsize=12)

    # Додаємо точні значення над кожним стовпчиком
    for i, v in enumerate(times):
        axes[1].text(i, v + (max(times) * 0.01), f"{v:.4f} s",
                     ha='center', va='bottom', fontweight='bold', fontsize=12)

    plt.tight_layout()
    plt.show()


def run_grid_search_bgd(X_train, y_train, X_test, y_test, alphas = [0.001, 0.01, 0.05, 0.1, 0.5, 1.0], lambdas = [0.001, 0.01, 0.1, 1.0], weights_on = True):
    penalties = [None, 'l1', 'l2']

    results = []
    best_r2 = -float('inf')
    best_params = None
    best_model = None

    print("Починаємо Grid Search для BGD...")

    for alpha, penalty in itertools.product(alphas, penalties):

        current_lambdas = lambdas if penalty is not None else [0]

        for lam in current_lambdas:
            model = LinearRegression(X_train, y_train, normalize=True)

            res = model.fit_batch_grad(
                alpha=alpha,
                max_epochs=2000,
                penalty=penalty,
                lambda_param=lam,
                track_history=True,
                verbose=False
            )
            test_r2 = model.evaluate_r(X_test, y_test)
            test_mse = model.evaluate_mse(X_test, y_test)

            results.append({
                'Alpha': alpha,
                'Penalty': penalty,
                'Lambda': lam if penalty else 'N/A',
                'Epochs': res['epochs_run'],
                'Test R2': test_r2,
                'Test MSE': test_mse,
                'Weights (Theta)': ("NaN" if np.isnan(test_r2) else np.round(model.theta, 4)) if weights_on else "Turned off"
            })

            if test_r2 > best_r2:
                best_r2 = test_r2
                best_params = {'alpha': alpha, 'penalty': penalty, 'lambda': lam}
                best_model = model

    print("Grid Search завершено!\n")

    results_df = pd.DataFrame(results).sort_values(by='Test R2', ascending=False).reset_index(drop=True)

    return best_model, best_params, results_df


def run_grid_search_adam(X_train, y_train, X_test, y_test, batch_size=64, alphas = [0.001, 0.01, 0.1, 0.5], lambdas = [0.01, 0.1, 1.0], weights_on = True):
    penalties = [None, 'l1', 'l2']

    results = []
    best_r2 = -float('inf')
    best_params = None
    best_model = None

    print("Починаємо Grid Search для Adam ...")

    for alpha, penalty in itertools.product(alphas, penalties):
        current_lambdas = lambdas if penalty is not None else [0]

        for lam in current_lambdas:
            model = LinearRegression(X_train, y_train, normalize=True)

            res = model.fit_adam_batch(
                alpha=alpha,
                batch_size=batch_size,
                max_epochs=2000,
                penalty=penalty,
                lambda_param=lam,
                track_history=True,
                verbose=False
            )

            test_r2 = model.evaluate_r(X_test, y_test)
            test_mse = model.evaluate_mse(X_test, y_test)

            if np.isnan(test_mse) or np.isinf(test_mse):
                test_r2 = -999.0
                epochs_run = "EXPLODED"
            else:
                epochs_run = res['epochs_run']

            results.append({
                'Alpha': alpha,
                'Penalty': penalty,
                'Lambda': lam if penalty else 'N/A',
                'Epochs': epochs_run,
                'Test R2': test_r2,
                'Test MSE': test_mse,
                'Weights (Theta)': ("NaN" if np.isnan(test_r2) else np.round(model.theta, 4)) if weights_on else "Turned off"
            })

            if test_r2 > best_r2:
                best_r2 = test_r2
                best_params = {'alpha': alpha, 'penalty': penalty, 'lambda': lam}
                best_model = model

    print("Grid Search завершено!\n")

    results_df = pd.DataFrame(results).sort_values(by='Test R2', ascending=False).reset_index(drop=True)
    return best_model, best_params, results_df