import React, { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, Sliders, LineChart, Cpu, Calendar, CheckCircle2, AlertTriangle, PlayCircle } from 'lucide-react';
import { mockProjects, mockExperiments, mockMetricLogs } from '../mockData';

export default function ProjectDetails() {
  const { id } = useParams();

  const project = mockProjects.find(p => p.id === Number(id));

  const projectExperiments = mockExperiments.filter(e => e.project_id === Number(id));

  const [selectedExperiment, setSelectedExperiment] = useState(projectExperiments[0] || null);

  if (!project) {
    return (
      <div className="text-center py-20">
        <h2 className="text-2xl font-bold text-zinc-200">Проєкт не знайдено</h2>
        <Link to="/projects" className="text-indigo-400 hover:underline mt-4 inline-block">Повернутися до проєктів</Link>
      </div>
    );
  }

  const renderSvgChart = (metrics, key, color) => {
    if (!metrics || metrics.length === 0) return null;
    const width = 500;
    const height = 150;
    const padding = 20;

    const values = metrics.map(m => m[key]);
    const maxVal = Math.max(...values, 1.0);
    const minVal = Math.min(...values, 0.0);

    const points = metrics.map((m, index) => {
      const x = padding + (index / (metrics.length - 1)) * (width - padding * 2);
      const y = height - padding - ((m[key] - minVal) / (maxVal - minVal || 1)) * (height - padding * 2);
      return `${x},${y}`;
    }).join(' ');

    return (
      <svg className="w-full h-36 bg-zinc-950/40 rounded-xl border border-zinc-800/80 p-2" viewBox={`0 0 ${width} ${height}`}>
        <line x1={padding} y1={padding} x2={width-padding} y2={padding} stroke="#27272a" strokeDasharray="4" />
        <line x1={padding} y1={height/2} x2={width-padding} y2={height/2} stroke="#27272a" strokeDasharray="4" />
        <line x1={padding} y1={height-padding} x2={width-padding} y2={height-padding} stroke="#27272a" strokeDasharray="4" />

        <polyline fill="none" stroke={color} strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" points={points} />

        {metrics.map((m, idx) => {
          const [cx, cy] = points.split(' ')[idx].split(',');
          return <circle key={idx} cx={cx} cy={cy} r="3" fill={color} className="hover:r-5 transition-all cursor-pointer" />;
        })}
      </svg>
    );
  };

  return (
    <div className="space-y-6">
      <div className="space-y-4">
        <Link to="/projects" className="inline-flex items-center gap-2 text-sm text-zinc-400 hover:text-zinc-200 transition-colors group">
          <ArrowLeft className="h-4 w-4 group-hover:-translate-x-1 transition-transform" />
          <span>Назад до проєктів</span>
        </Link>

        <div className="border-b border-zinc-800 pb-6">
          <h1 className="text-3xl font-bold tracking-tight text-zinc-100">{project.name}</h1>
          <p className="text-zinc-400 mt-2 max-w-4xl text-sm leading-relaxed">{project.description}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">

        <div className="lg:col-span-7 space-y-3">
          <h2 className="text-lg font-semibold text-zinc-300 px-1">Експерименти репозиторію</h2>

          {projectExperiments.length === 0 ? (
            <div className="p-8 text-center bg-zinc-900 border border-zinc-800 rounded-2xl text-zinc-500 text-sm">
              Для цього проєкту ще не запущено жодного експерименту.
            </div>
          ) : (
            projectExperiments.map((exp) => {
              const isSelected = selectedExperiment?.id === exp.id;

              return (
                <div
                  key={exp.id}
                  onClick={() => setSelectedExperiment(exp)}
                  className={`p-4 bg-zinc-900 border rounded-2xl cursor-pointer transition-all flex items-center justify-between
                    ${isSelected
                      ? 'border-indigo-500 shadow-md shadow-indigo-600/5 bg-zinc-900'
                      : 'border-zinc-800 hover:border-zinc-700 hover:bg-zinc-800/30'}`}
                >
                  <div className="space-y-1.5 min-w-0 pr-4">
                    <div className="font-mono text-xs font-semibold text-zinc-200 truncate">{exp.name}</div>
                    <div className="flex items-center gap-3 text-xs text-zinc-500">
                      <span className="flex items-center gap-1">
                        <Cpu className="h-3 w-3" /> {exp.hyperparameters.optimizer}
                      </span>
                      <span className="flex items-center gap-1">
                        <Calendar className="h-3 w-3" /> {new Date(exp.started_at).toLocaleDateString('uk-UA')}
                      </span>
                    </div>
                  </div>

                  <div>
                    {exp.status === 'completed' && (
                      <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                        <CheckCircle2 className="h-3 w-3" /> Completed
                      </span>
                    )}
                    {exp.status === 'running' && (
                      <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md text-xs font-medium bg-amber-500/10 text-amber-400 border border-amber-500/20 animate-pulse">
                        <PlayCircle className="h-3 w-3" /> Running
                      </span>
                    )}
                    {exp.status === 'failed' && (
                      <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md text-xs font-medium bg-rose-500/10 text-rose-400 border border-rose-500/20">
                        <AlertTriangle className="h-3 w-3" /> Failed
                      </span>
                    )}
                  </div>

                </div>
              );
            })
          )}
        </div>

        <div className="lg:col-span-5">
          {selectedExperiment ? (
            <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-5 space-y-6 shadow-sm sticky top-6">

              <div className="border-b border-zinc-800 pb-4">
                <span className="text-xs font-semibold text-indigo-400 font-mono">ID: #{selectedExperiment.id}</span>
                <h3 className="text-base font-bold text-zinc-100 font-mono mt-1 truncate">{selectedExperiment.name}</h3>
              </div>

              <div className="space-y-3">
                <h4 className="text-xs font-semibold text-zinc-400 uppercase tracking-wider flex items-center gap-1.5">
                  <Sliders className="h-3.5 w-3.5 text-zinc-500" /> Гіперпараметри
                </h4>
                <div className="grid grid-cols-2 gap-3 bg-zinc-950/50 p-3 rounded-xl border border-zinc-800/60 font-mono text-xs">
                  <div className="p-2 bg-zinc-900/60 rounded-lg border border-zinc-800/40">
                    <div className="text-zinc-500 mb-0.5">Learning Rate</div>
                    <div className="text-zinc-200 font-bold">{selectedExperiment.hyperparameters.learning_rate}</div>
                  </div>
                  <div className="p-2 bg-zinc-900/60 rounded-lg border border-zinc-800/40">
                    <div className="text-zinc-500 mb-0.5">Epochs</div>
                    <div className="text-zinc-200 font-bold">{selectedExperiment.hyperparameters.epochs}</div>
                  </div>
                  <div className="p-2 bg-zinc-900/60 rounded-lg border border-zinc-800/40">
                    <div className="text-zinc-500 mb-0.5">Optimizer</div>
                    <div className="text-zinc-200 font-bold">{selectedExperiment.hyperparameters.optimizer}</div>
                  </div>
                  <div className="p-2 bg-zinc-900/60 rounded-lg border border-zinc-800/40">
                    <div className="text-zinc-500 mb-0.5">Batch Size</div>
                    <div className="text-zinc-200 font-bold">{selectedExperiment.hyperparameters.batch_size || 32}</div>
                  </div>
                </div>
              </div>

              <div className="space-y-4">
                <h4 className="text-xs font-semibold text-zinc-400 uppercase tracking-wider flex items-center gap-1.5">
                  <LineChart className="h-3.5 w-3.5 text-zinc-500" /> Графіки навчання (Metrics)
                </h4>

                {selectedExperiment.id === 101 ? (
                  <div className="space-y-4">
                    {/* Графік Loss */}
                    <div className="space-y-1.5">
                      <div className="flex justify-between text-xs font-mono">
                        <span className="text-zinc-400">Loss Function (Train)</span>
                        <span className="text-rose-400 font-bold">min: {mockMetricLogs[mockMetricLogs.length-1].loss}</span>
                      </div>
                      {renderSvgChart(mockMetricLogs, 'loss', '#f43f5e')}
                    </div>

                    {/* Графік Accuracy */}
                    <div className="space-y-1.5">
                      <div className="flex justify-between text-xs font-mono">
                        <span className="text-zinc-400">Accuracy (Validation)</span>
                        <span className="text-emerald-400 font-bold">max: {mockMetricLogs[mockMetricLogs.length-1].accuracy}</span>
                      </div>
                      {renderSvgChart(mockMetricLogs, 'accuracy', '#10b981')}
                    </div>
                  </div>
                ) : (
                  <div className="p-8 text-center bg-zinc-950/40 border border-zinc-800/60 rounded-xl text-zinc-500 text-xs italic">
                    {selectedExperiment.status === 'running'
                      ? "Метрики генеруються в реальному часі. Підключіть WebSocket у Лабораторній №3."
                      : "Для цього експерименту відсутні залоговані логи метрик."}
                  </div>
                )}
              </div>

            </div>
          ) : (
            <div className="p-6 text-center bg-zinc-900/50 border border-zinc-800 border-dashed rounded-2xl text-zinc-500 text-sm italic">
              Оберіть експеримент зліва, щоб переглянути деталі.
            </div>
          )}
        </div>

      </div>
    </div>
  );
}