// src/mockData.js

export const mockProjects = [
  {
    id: 1,
    name: "Computer Vision Pipeline",
    description: "Розробка та тренування Vision Transformer (ViT) та EfficientNet для детекції deepfake-контенту та артефактів генерації.",
    created_at: "2026-03-15T10:00:00Z",
    experiments_count: 2
  },
  {
    id: 2,
    name: "Algorithmic Trading Bot",
    description: "Оптимізація портфеля за коефіцієнтом Шарпа та розробка ботів для детекції ринкових режимів за допомогою LSTM.",
    created_at: "2026-04-01T14:30:00Z",
    experiments_count: 1
  },
  {
    id: 3,
    name: "Cryptography Performance",
    description: "Бенчмаркінг та аналіз швидкості криптографічних алгоритмів (RC5, RSA, MD5) під навантаженням.",
    created_at: "2026-05-10T09:15:00Z",
    experiments_count: 0
  }
];

export const mockExperiments = [
  {
    id: 101,
    project_id: 1,
    name: "ViT_Base_Adam_LR_1e-4",
    status: "completed", // 'running', 'completed', 'failed'
    started_at: "2026-05-25T12:00:00Z",
    finished_at: "2026-05-25T15:00:00Z",
    hyperparameters: {
      id: 1,
      experiment_id: 101,
      learning_rate: 0.0001,
      epochs: 15,
      optimizer: "Adam",
      batch_size: 32 // Додаткове поле для гнучкості UI
    }
  },
  {
    id: 102,
    project_id: 1,
    name: "EfficientNet_B4_SGD_LR_1e-2",
    status: "failed",
    started_at: "2026-05-26T08:00:00Z",
    finished_at: "2026-05-26T08:40:00Z",
    hyperparameters: {
      id: 2,
      experiment_id: 102,
      learning_rate: 0.01,
      epochs: 20,
      optimizer: "SGD",
      batch_size: 64
    }
  },
  {
    id: 103,
    project_id: 2,
    name: "Sharpe_Optimization_LSTM_AdamW",
    status: "running",
    started_at: "2026-05-26T16:00:00Z",
    finished_at: null,
    hyperparameters: {
      id: 3,
      experiment_id: 103,
      learning_rate: 0.001,
      epochs: 10,
      optimizer: "AdamW",
      batch_size: 128
    }
  }
];

// Імітація згасання loss та росту accuracy для побудови красивих графіків на фронтенді
// Зв'язано з експериментом №101 (ViT_Base_Adam_LR_1e-4)
export const mockMetricLogs = [
  { id: 1, experiment_id: 101, epoch: 1, loss: 0.9124, accuracy: 0.2105, timestamp: "2026-05-25T12:04:00Z" },
  { id: 2, experiment_id: 101, epoch: 2, loss: 0.8241, accuracy: 0.3542, timestamp: "2026-05-25T12:08:00Z" },
  { id: 3, experiment_id: 101, epoch: 3, loss: 0.7102, accuracy: 0.4918, timestamp: "2026-05-25T12:12:00Z" },
  { id: 4, experiment_id: 101, epoch: 4, loss: 0.6015, accuracy: 0.5824, timestamp: "2026-05-25T12:16:00Z" },
  { id: 5, experiment_id: 101, epoch: 5, loss: 0.5122, accuracy: 0.6411, timestamp: "2026-05-25T12:20:00Z" },
  { id: 6, experiment_id: 101, epoch: 6, loss: 0.4419, accuracy: 0.7023, timestamp: "2026-05-25T12:24:00Z" },
  { id: 7, experiment_id: 101, epoch: 7, loss: 0.3854, accuracy: 0.7419, timestamp: "2026-05-25T12:28:00Z" },
  { id: 8, experiment_id: 101, epoch: 8, loss: 0.3321, accuracy: 0.7802, timestamp: "2026-05-25T12:32:00Z" },
  { id: 9, experiment_id: 101, epoch: 9, loss: 0.2914, accuracy: 0.8145, timestamp: "2026-05-25T12:36:00Z" },
  { id: 10, experiment_id: 101, epoch: 10, loss: 0.2541, accuracy: 0.8391, timestamp: "2026-05-25T12:40:00Z" },
  { id: 11, experiment_id: 101, epoch: 11, loss: 0.2218, accuracy: 0.8612, timestamp: "2026-05-25T12:44:00Z" },
  { id: 12, experiment_id: 101, epoch: 12, loss: 0.1984, accuracy: 0.8804, timestamp: "2026-05-25T12:48:00Z" },
  { id: 13, experiment_id: 101, epoch: 13, loss: 0.1752, accuracy: 0.8993, timestamp: "2026-05-25T12:52:00Z" },
  { id: 14, experiment_id: 101, epoch: 14, loss: 0.1591, accuracy: 0.9124, timestamp: "2026-05-25T12:56:00Z" },
  { id: 15, experiment_id: 101, epoch: 15, loss: 0.1423, accuracy: 0.9251, timestamp: "2026-05-25T13:00:00Z" }
];