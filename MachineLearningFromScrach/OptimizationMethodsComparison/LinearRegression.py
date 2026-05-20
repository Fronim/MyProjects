import numpy as np
import time

class LinearRegression:
    def __init__(self, numerical_data, target, tol = 1e-5, normalize=True):
        raw_X = np.array(numerical_data)
        raw_y = np.array(target)

        if normalize:
            self.mean_X = np.mean(raw_X, axis=0)
            self.std_X = np.std(raw_X, axis=0)
            self.std_X = np.where(self.std_X == 0, 1e-8, self.std_X)
            self.X = (raw_X - self.mean_X) / self.std_X

            self.mean_y = np.mean(raw_y)
            self.std_y = np.std(raw_y)
            self.y = (raw_y - self.mean_y) / (self.std_y + 1e-8)
        else:
            self.mean_X = np.zeros(raw_X.shape[1])
            self.std_X = np.ones(raw_X.shape[1])
            self.mean_y = 0.0
            self.std_y = 1.0
            self.X = raw_X
            self.y = raw_y

        self.theta = np.zeros(np.shape(self.X)[1]).T
        self.b = 0.0
        self.tol = tol

        self.loss_history = None
        self.val_loss_history = None
        self.time_history = None

    def fit_batch_grad(self, alpha=0.01, max_epochs=1000, penalty='l2', lambda_param=0.01, X_validation=None, y_validation=None, track_history=False, verbose=True):
        m, n = np.shape(self.X)
        prev_loss = float('inf')

        if track_history:
            self.loss_history = []
            self.val_loss_history = []
            self.time_history = []
            cumulative_train_time = 0.0

        for epoch in range(max_epochs):
            if track_history:
                epoch_start = time.perf_counter()

            predictions = self.X @ self.theta + self.b
            errors = predictions - self.y

            pure_mse = np.mean(errors ** 2) / 2
            if penalty == 'l2':
                reg_loss = (lambda_param / (2 * m)) * np.sum(self.theta ** 2)
            elif penalty == 'l1':
                reg_loss = (lambda_param / m) * np.sum(np.abs(self.theta))
            else:
                reg_loss = 0

            current_loss = pure_mse + reg_loss

            grad_theta = (self.X.T @ errors) / m
            grad_b = np.sum(errors) / m

            if penalty == 'l2':
                grad_theta += (lambda_param / m) * self.theta
            elif penalty == 'l1':
                grad_theta += (lambda_param / m) * np.sign(self.theta)

            self.theta -= alpha * grad_theta
            self.b -= alpha * grad_b

            if track_history:
                cumulative_train_time += (time.perf_counter() - epoch_start)

            if track_history:
                self.loss_history.append(current_loss)

                self.time_history.append(cumulative_train_time)

                if X_validation is not None and y_validation is not None:
                    self.val_loss_history.append(self.evaluate_mse(X_validation, y_validation))

            if abs(prev_loss - current_loss) < self.tol:
                if verbose:
                    penalty_str = f" (Penalty={penalty})" if penalty else ""
                    print(f"Batch Gradient Descent{penalty_str}: Рання зупинка на епосі {epoch}.")
                break

            prev_loss = current_loss

        if track_history:
            return {
                "epochs_run": len(self.loss_history),
                "loss_history": self.loss_history,
                "val_loss_history": self.val_loss_history,
                "time_history": self.time_history
            }


    def fit_mini_batch_grad(self, alpha = 0.01, batch_size = 64, max_epochs=1000, penalty=None, lambda_param=0.01, X_validation=None, y_validation=None, track_history = False, verbose = True):
        m, n = np.shape(self.X)
        if batch_size > m:
            print(f"Batch size is too big. Make it strictly smaller than total number of training samples (< {m})")
            return
        prev_loss = float('inf')

        if track_history:
            self.loss_history = []
            self.val_loss_history = []
            self.time_history = []
            cumulative_train_time = 0.0

        for epoch in range(max_epochs):
            if track_history:
                epoch_start = time.perf_counter()

            indices = np.random.permutation(m)

            for k in range(0, m, batch_size):
                batch_idx = indices[k : k + batch_size]
                current_batch_size = len(batch_idx)

                batch_X = self.X[batch_idx]
                batch_y = self.y[batch_idx]

                predictions = batch_X @ self.theta + self.b
                errors = predictions - batch_y

                grad_theta = (batch_X.T @ errors) / current_batch_size
                grad_b = np.sum(errors) / current_batch_size

                if penalty == 'l2':
                    grad_theta += (lambda_param / m) * self.theta
                elif penalty == 'l1':
                    grad_theta += (lambda_param / m) * np.sign(self.theta)

                self.theta -= alpha * grad_theta
                self.b -= alpha * grad_b

            if track_history:
                cumulative_train_time += (time.perf_counter() - epoch_start)

            predictions = self.X @ self.theta + self.b
            pure_mse = np.mean((predictions - self.y) ** 2) / 2

            if penalty == 'l2':
                reg_loss = (lambda_param / (2 * m)) * np.sum(self.theta ** 2)
            elif penalty == 'l1':
                reg_loss = (lambda_param / m) * np.sum(np.abs(self.theta))
            else:
                reg_loss = 0

            current_loss = pure_mse + reg_loss

            if track_history:
                self.loss_history.append(current_loss)
                self.time_history.append(cumulative_train_time)
                if X_validation is not None and y_validation is not None:
                    self.val_loss_history.append(self.evaluate_mse(X_validation, y_validation))

            if abs(prev_loss - current_loss) < self.tol:
                if verbose:
                    print(f"Mini-Batch SGD зійшлося на епосі {epoch}")
                break
            prev_loss = current_loss

        if track_history:
            return {
                "epochs_run": len(self.loss_history),
                "loss_history": self.loss_history,
                "val_loss_history": self.val_loss_history,
                "time_history": self.time_history
            }
        else:
            return


    def fit_adam_batch(self, alpha = 0.01, beta1 = 0.9, beta2 = 0.999, penalty=None, lambda_param=0.01, batch_size = 64, max_epochs = 1000, eps = 1e-8, X_validation=None, y_validation=None, track_history=False, verbose=True):
        m, n = np.shape(self.X)
        if batch_size >= m:
            print(f"Batch size is too big. Make it strictly smaller than total number of training samples (< {m})")
            return

        m_th = np.zeros(n)
        v_th = np.zeros(n)
        v_b = 0.0
        m_b = 0.0
        t = 0

        prev_loss = float('inf')

        if track_history:
            self.loss_history = []
            self.val_loss_history = []
            self.time_history = []
            cumulative_train_time = 0.0

        for epoch in range(max_epochs):
            if track_history:
                epoch_start = time.perf_counter()

            indices = np.random.permutation(m)

            for k in range(0, m, batch_size):

                t += 1
                batch_idx = indices[k: k + batch_size]
                current_batch_size = len(batch_idx)

                batch_X = self.X[batch_idx]
                batch_y = self.y[batch_idx]

                predictions = batch_X @ self.theta + self.b
                errors = predictions - batch_y

                grad_theta = (batch_X.T @ errors) / current_batch_size
                grad_b = np.sum(errors) / current_batch_size

                if penalty == 'l2':
                    grad_theta += (lambda_param / m) * self.theta
                elif penalty == 'l1':
                    grad_theta += (lambda_param / m) * np.sign(self.theta)

                m_th = beta1 * m_th + (1 - beta1) * grad_theta
                v_th = beta2 * v_th + (1 - beta2) * grad_theta ** 2
                m_b = beta1 * m_b + (1 - beta1) * grad_b
                v_b = beta2 * v_b + (1 - beta2) * grad_b ** 2

                mhat_th = m_th / (1 - beta1 ** t)
                vhat_th = v_th / (1 - beta2 ** t)
                mhat_b = m_b / (1 - beta1 ** t)
                vhat_b = v_b / (1 - beta2 ** t)

                self.theta -= alpha * mhat_th / (np.sqrt(vhat_th) + eps)
                self.b -= alpha * mhat_b / (np.sqrt(vhat_b) + eps)

            if track_history:
                cumulative_train_time += (time.perf_counter() - epoch_start)

            predictions = self.X @ self.theta + self.b
            pure_mse = np.mean((predictions - self.y) ** 2) / 2

            if penalty == 'l2':
                reg_loss = (lambda_param / (2 * m)) * np.sum(self.theta ** 2)
            elif penalty == 'l1':
                reg_loss = (lambda_param / m) * np.sum(np.abs(self.theta))
            else:
                reg_loss = 0

            current_loss = pure_mse + reg_loss

            if track_history:
                self.loss_history.append(current_loss)
                self.time_history.append(cumulative_train_time)  # Записуємо чистий час
                if X_validation is not None and y_validation is not None:
                    self.val_loss_history.append(self.evaluate_mse(X_validation, y_validation))

            if abs(prev_loss - current_loss) < self.tol:
                if verbose:
                    penalty_str = f" (Penalty={penalty})" if penalty else ""
                    print(f"Mini-Batch Adam{penalty_str} зійшовся на епосі {epoch}")
                break

            prev_loss = current_loss

        if track_history:
            return {
                "epochs_run": len(self.loss_history),
                "loss_history": self.loss_history,
                "val_loss_history": self.val_loss_history,
                "time_history": self.time_history
            }
        else:
            return


    def predict(self, X):
        X_scaled = (np.array(X) - self.mean_X) / self.std_X
        preds_scaled = X_scaled @ self.theta + self.b
        return preds_scaled

    def evaluate_r(self, X, y):
        X_scaled = (np.array(X) - self.mean_X) / self.std_X
        y_scaled = (np.array(y) - self.mean_y) / (self.std_y + 1e-8)

        preds_scaled = X_scaled @ self.theta + self.b

        r_squared = 1 - np.sum((y_scaled - preds_scaled) ** 2) / np.sum((y_scaled - np.mean(y_scaled)) ** 2)
        return r_squared

    def evaluate_mse(self, X, y):
        X_scaled = (np.array(X) - self.mean_X) / self.std_X
        y_scaled = (np.array(y) - self.mean_y) / (self.std_y + 1e-8)

        preds_scaled = X_scaled @ self.theta + self.b
        loss = np.mean((y_scaled - preds_scaled) ** 2)
        return loss