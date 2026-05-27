// src/pages/Projects.jsx
import React from 'react';
import { Link } from 'react-router-dom';
import { Calendar, Layers, ArrowRight } from 'lucide-react';
import { mockProjects } from '../mockData';

export default function Projects() {
  return (
    <div className="space-y-8">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-zinc-100">Projects Workspace</h1>
          <p className="text-sm text-zinc-400 mt-1">Менеджмент дослідницьких репозиторіїв та ізольованих ML-задач.</p>
        </div>
        <Link
          to="/experiments/new"
          className="inline-flex items-center justify-center bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-sm px-4 py-2.5 rounded-xl transition-all shadow-md shadow-indigo-600/10 self-start sm:self-auto"
        >
          Новий Експеримент
        </Link>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {mockProjects.map((project) => (
          <div
            key={project.id}
            className="group bg-zinc-900 border border-zinc-800 rounded-2xl p-6 flex flex-col justify-between shadow-sm hover:border-zinc-700/80 hover:-translate-y-1 transition-all duration-300"
          >
            <div className="space-y-4">
              <div className="flex items-start justify-between gap-4">
                <h3 className="text-lg font-bold text-zinc-100 group-hover:text-indigo-400 transition-colors line-clamp-1">
                  {project.name}
                </h3>
                <span className="shrink-0 inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-semibold bg-zinc-800 text-zinc-400 border border-zinc-700/60">
                  <Layers className="h-3 w-3" />
                  {project.experiments_count} exp
                </span>
              </div>

              <p className="text-sm text-zinc-400 line-clamp-3 leading-relaxed">
                {project.description}
              </p>
            </div>

            <div className="mt-6 pt-4 border-t border-zinc-800/60 flex items-center justify-between">
              <div className="flex items-center gap-1.5 text-xs text-zinc-500">
                <Calendar className="h-3.5 w-3.5" />
                <span>
                  {new Date(project.created_at).toLocaleDateString('uk-UA', {
                    year: 'numeric', month: 'short', day: 'numeric'
                  })}
                </span>
              </div>

              <Link
                to={`/projects/${project.id}`}
                className="inline-flex items-center gap-1 text-sm font-medium text-zinc-300 hover:text-white transition-colors"
              >
                <span>Відкрити проєкт</span>
                <ArrowRight className="h-4 w-4 group-hover:translate-x-1 transition-transform" />
              </Link>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}