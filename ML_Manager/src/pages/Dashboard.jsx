import React from 'react';
import { Link } from 'react-router-dom';
import { Layers, Activity, CheckCircle, ArrowUpRight } from 'lucide-react';
import { mockProjects, mockExperiments } from '../mockData';

export default function Dashboard() {
  const totalProjects = mockProjects.length;
  const activeExperiments = mockExperiments.filter(e => e.status === 'running').length;

  const completedExp = mockExperiments.filter(e => e.status === 'completed').length;
  const totalFinishedExp = mockExperiments.filter(e => e.status !== 'running').length;
  const successRate = totalFinishedExp > 0 ? Math.round((completedExp / totalFinishedExp) * 100) : 0;

  const statusStyles = {
    running: 'bg-blue-500/10 text-blue-400 border-blue-500/20 animate-pulse',
    completed: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
    failed: 'bg-rose-500/10 text-rose-400 border-rose-500/20',
  };

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-zinc-100">Dashboard Overview</h1>
        <p className="text-sm text-zinc-400 mt-1">Загальна аналітика розробки та моніторинг моделей у реальному часі.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        <div className="p-6 bg-zinc-900 border border-zinc-800 rounded-2xl flex items-center justify-between shadow-sm hover:border-zinc-700 transition-all">
          <div className="space-y-2">
            <span className="text-xs font-medium text-zinc-400 uppercase tracking-wider">Загалом Проєктів</span>
            <h3 className="text-3xl font-bold text-zinc-100">{totalProjects}</h3>
          </div>
          <div className="p-3 bg-zinc-800 rounded-xl border border-zinc-700">
            <Layers className="h-6 w-6 text-indigo-400" />
          </div>
        </div>

        <div className="p-6 bg-zinc-900 border border-zinc-800 rounded-2xl flex items-center justify-between shadow-sm hover:border-zinc-700 transition-all">
          <div className="space-y-2">
            <span className="text-xs font-medium text-zinc-400 uppercase tracking-wider">Активні Експерименти</span>
            <h3 className="text-3xl font-bold text-zinc-100">{activeExperiments}</h3>
          </div>
          <div className="p-3 bg-zinc-800 rounded-xl border border-zinc-700">
            <Activity className="h-6 w-6 text-blue-400" />
          </div>
        </div>

        <div className="p-6 bg-zinc-900 border border-zinc-800 rounded-2xl flex items-center justify-between shadow-sm hover:border-zinc-700 transition-all">
          <div className="space-y-2">
            <span className="text-xs font-medium text-zinc-400 uppercase tracking-wider">Успішність Моделей</span>
            <h3 className="text-3xl font-bold text-zinc-100">{successRate}%</h3>
          </div>
          <div className="p-3 bg-zinc-800 rounded-xl border border-zinc-700">
            <CheckCircle className="h-6 w-6 text-emerald-400" />
          </div>
        </div>
      </div>

      <div className="bg-zinc-900 border border-zinc-800 rounded-2xl overflow-hidden shadow-sm">
        <div className="p-5 border-b border-zinc-800 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-zinc-200">Останні запущені експерименти</h2>
          <span className="text-xs text-zinc-500 font-mono">Сортування: за датою</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-zinc-800 text-xs font-semibold text-zinc-400 uppercase bg-zinc-900/50">
                <th className="p-4 pl-6">Назва Експерименту</th>
                <th className="p-4">Статус</th>
                <th className="p-4">Оптимізатор</th>
                <th className="p-4">Дата Старту</th>
                <th className="p-4 pr-6 text-right">Дії</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-800/60 text-sm text-zinc-300">
              {mockExperiments.map((exp) => (
                <tr key={exp.id} className="hover:bg-zinc-800/30 transition-colors">
                  <td className="p-4 pl-6 font-medium text-zinc-200 font-mono text-xs">{exp.name}</td>
                  <td className="p-4">
                    <span className={`px-2.5 py-1 rounded-md text-xs font-medium border ${statusStyles[exp.status]}`}>
                      {exp.status}
                    </span>
                  </td>
                  <td className="p-4 text-zinc-400 font-mono text-xs">{exp.hyperparameters.optimizer}</td>
                  <td className="p-4 text-zinc-400">
                    {new Date(exp.started_at).toLocaleDateString('uk-UA', {
                      day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit'
                    })}
                  </td>
                  <td className="p-4 pr-6 text-right">
                    <Link
                      to={`/projects/${exp.project_id}`}
                      className="inline-flex items-center gap-1 text-xs font-medium text-indigo-400 hover:text-indigo-300 transition-colors"
                    >
                      <span>Переглянути</span>
                      <ArrowUpRight className="h-3 w-3" />
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}