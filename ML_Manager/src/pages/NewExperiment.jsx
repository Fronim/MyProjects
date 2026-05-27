import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Play, ArrowLeft, Sliders, Info } from 'lucide-react';
import { mockProjects } from '../mockData';

export default function NewExperiment() {
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    name: '',
    project_id: mockProjects[0]?.id || '',
    learning_rate: 0.001,
    epochs: 10,
    optimizer: 'Adam',
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    const parsedValue = name === 'learning_rate' || name === 'epochs' || name === 'project_id'
      ? Number(value)
      : value;

    setFormData((prev) => ({
      ...prev,
      [name]: parsedValue,
    }));
  };

  const isLrInvalid = formData.learning_rate <= 0 || formData.learning_rate > 1;
  const isEpochsInvalid = formData.epochs < 1 || formData.epochs > 1000;
  const isNameInvalid = formData.name.trim().length === 0;

  const isFormInvalid = isLrInvalid || isEpochsInvalid || isNameInvalid;

  const handleSubmit = (e) => {
    e.preventDefault();

    if (isFormInvalid) return;

    console.log('[+] Сабміт форми нового експерименту:', formData);

    navigate('/');
  };

  return (
    <div className="space-y-6 max-w-2xl mx-auto">
      <div className="space-y-4">
        <Link to="/" className="inline-flex items-center gap-2 text-sm text-zinc-400 hover:text-zinc-200 transition-colors group">
          <ArrowLeft className="h-4 w-4 group-hover:-translate-x-1 transition-transform" />
          <span>Скасувати та повернутися</span>
        </Link>

        <div>
          <h1 className="text-3xl font-bold tracking-tight text-zinc-100">Configure New Experiment</h1>
          <p className="text-sm text-zinc-400 mt-1">
            Задайте архітектурні гіперпараметри для ініціалізації нового циклу навчання моделі.
          </p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="bg-zinc-900 border border-zinc-800 rounded-2xl p-6 space-y-6 shadow-sm">

        <div className="space-y-4 border-b border-zinc-800/60 pb-6">
          <h3 className="text-sm font-semibold text-zinc-400 uppercase tracking-wider flex items-center gap-2">
            <Info className="h-4 w-4 text-zinc-500" /> Загальні налаштування
          </h3>

          <div className="flex flex-col gap-2">
            <label htmlFor="name" className="text-xs font-medium text-zinc-300">Назва експерименту</label>
            <input
              type="text"
              id="name"
              name="name"
              value={formData.name}
              onChange={handleChange}
              placeholder="e.g., ResNet50_Adam_Batch64"
              className="px-4 py-2.5 bg-zinc-950 border border-zinc-800 rounded-xl font-mono text-sm text-zinc-100 focus:outline-none focus:border-indigo-500 transition-colors placeholder:text-zinc-600"
            />
            {isNameInvalid && (
              <span className="text-xs text-zinc-500 italic">Назва не може бути порожньою</span>
            )}
          </div>

          <div className="flex flex-col gap-2">
            <label htmlFor="project_id" className="text-xs font-medium text-zinc-300">Цільовий проєкт (Workspace)</label>
            <select
              id="project_id"
              name="project_id"
              value={formData.project_id}
              onChange={handleChange}
              className="px-4 py-2.5 bg-zinc-950 border border-zinc-800 rounded-xl text-sm text-zinc-100 focus:outline-none focus:border-indigo-500 transition-colors cursor-pointer"
            >
              {mockProjects.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="space-y-4">
          <h3 className="text-sm font-semibold text-zinc-400 uppercase tracking-wider flex items-center gap-2">
            <Sliders className="h-4 w-4 text-zinc-500" /> Гіперпараметри моделі
          </h3>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="flex flex-col gap-2">
              <label htmlFor="learning_rate" className="text-xs font-medium text-zinc-300">Learning Rate (швидкість навчання)</label>
              <input
                type="number"
                id="learning_rate"
                name="learning_rate"
                step="0.0001"
                min="0"
                max="1"
                value={formData.learning_rate}
                onChange={handleChange}
                className={`px-4 py-2.5 bg-zinc-950 border rounded-xl font-mono text-sm text-zinc-100 focus:outline-none transition-colors
                  ${isLrInvalid ? 'border-rose-500/80 focus:border-rose-500' : 'border-zinc-800 focus:border-indigo-500'}`}
              />
              {isLrInvalid && (
                <span className="text-xs text-rose-400">Значення має бути в межах від 0.0001 до 1.0</span>
              )}
            </div>

            <div className="flex flex-col gap-2">
              <label htmlFor="epochs" className="text-xs font-medium text-zinc-300">Кількість епох тренування</label>
              <input
                type="number"
                id="epochs"
                name="epochs"
                min="1"
                max="1000"
                value={formData.epochs}
                onChange={handleChange}
                className={`px-4 py-2.5 bg-zinc-950 border rounded-xl font-mono text-sm text-zinc-100 focus:outline-none transition-colors
                  ${isEpochsInvalid ? 'border-rose-500/80 focus:border-rose-500' : 'border-zinc-800 focus:border-indigo-500'}`}
              />
              {isEpochsInvalid && (
                <span className="text-xs text-rose-400">Кількість епох має бути не менше 1</span>
              )}
            </div>
          </div>

          <div className="flex flex-col gap-2">
            <label htmlFor="optimizer" className="text-xs font-medium text-zinc-300">Оптимізатор градієнтного спуску</label>
            <select
              id="optimizer"
              name="optimizer"
              value={formData.optimizer}
              onChange={handleChange}
              className="px-4 py-2.5 bg-zinc-950 border border-zinc-800 rounded-xl font-mono text-sm text-zinc-100 focus:outline-none focus:border-indigo-500 transition-colors cursor-pointer"
            >
              <option value="Adam">Adam</option>
              <option value="SGD">SGD</option>
              <option value="RMSprop">RMSprop</option>
            </select>
          </div>
        </div>

        <div className="pt-4 border-t border-zinc-800/60 flex items-center justify-end">
          <button
            type="submit"
            disabled={isFormInvalid}
            className={`inline-flex items-center gap-2 px-5 py-3 rounded-xl font-semibold text-sm transition-all shadow-md
              ${isFormInvalid
                ? 'bg-zinc-800 text-zinc-500 border border-zinc-700/30 cursor-not-allowed shadow-none'
                : 'bg-indigo-600 hover:bg-indigo-500 text-white shadow-indigo-600/10 active:scale-[0.98]'}`}
          >
            <Play className="h-4 w-4" />
            <span>Запустити експеримент</span>
          </button>
        </div>

      </form>
    </div>
  );
}