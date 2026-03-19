import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def sigmoid(z: np.array):
    return 1 / (1 + np.exp(-z))

class LogisticRegression():
    def __init__(self, lr=0.1, iterations=500, tol=1e-7):
        self.x = None
        self.y = None
        self.w = None
        self.lr = lr
        self.max_iter = iterations
        self.tol = tol

    def fit(self, x: np.ndarray, y: np.array):
        self.x = x
        self.y = y.reshape(-1, 1)

    def fit_data(self, data: pd.DataFrame, classification_field: str):
        self.x = data.drop(classification_field, axis = 1).to_numpy()
        self.y = data[classification_field].to_numpy().reshape(-1, 1)


    def train(self):
        m_samples, n_features = self.x.shape
        y = self.y
        x = np.concatenate(np.ones((m_samples, 1), self.x), axis = 1)
        weights = np.zeros((n_features + 1, 1))

        for _ in range(self.max_iter):
            gradient = 1/m_samples * (x.T @ (sigmoid(x @ weights.T)-y))
            weights -= self.lr * gradient

            if np.linalg.norm(gradient)<self.tol:
                break
        self.w = weights

    def predict(self):
        if self.w is None:
            raise Exception("Model has not been trained yet.")
        m_samples, n_features = self.x.shape
        x = np.concatenate((np.ones((m_samples, 1)), self.x), axis=1)
        prob = sigmoid(x @ self.w)
        return prob>=0.5

