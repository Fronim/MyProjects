import React from 'react';
import { BrowserRouter, Routes, Route, useParams } from 'react-router-dom';
import Layout from './components/common/Layout';
import Dashboard from './pages/Dashboard';
import Projects from './pages/Projects';

const ProjectDetailsStub = () => {
  const { id } = useParams();
  return (
    <div>
      <h1 className="text-3xl font-bold tracking-tight mb-2">Project #{id} Details</h1>
      <p className="text-zinc-400">Тут будуть відображатися гіперпараметри та таблиця пов'язаних експериментів.</p>
    </div>
  );
};

const NewExperimentStub = () => (
  <div>
    <h1 className="text-3xl font-bold tracking-tight mb-2">Launch New Experiment</h1>
    <p className="text-zinc-400">Конфігурація параметрів тренування (Learning Rate, Optimizer, Epochs) перед запуском.</p>
  </div>
);

const NotFoundStub = () => (
  <div className="text-center py-20">
    <h1 className="text-6xl font-bold text-indigo-500 mb-4">404</h1>
    <p className="text-zinc-400 text-lg">Сторінку не знайдено в просторі експериментів.</p>
  </div>
);


export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />

          <Route path="projects" element={<Projects />} />
          <Route path="projects/:id" element={<ProjectDetailsStub />} />
          <Route path="experiments/new" element={<NewExperimentStub />} />

          <Route path="*" element={<NotFoundStub />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}