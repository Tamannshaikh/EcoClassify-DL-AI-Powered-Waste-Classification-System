import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { MainLayout } from './layouts/MainLayout';
import { Dashboard } from './pages/Dashboard';
import { PredictionPage } from './pages/PredictionPage';
import { HistoryPage } from './pages/HistoryPage';
import { DatasetPage } from './pages/DatasetPage';
import { PerformancePage } from './pages/PerformancePage';
import { TrainingPage } from './pages/TrainingPage';
import { AboutPage } from './pages/AboutPage';
import { SettingsPage } from './pages/SettingsPage';

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<MainLayout />}>
          <Route index element={<Dashboard />} />
          <Route path="predict" element={<PredictionPage />} />
          <Route path="history" element={<HistoryPage />} />
          <Route path="dataset" element={<DatasetPage />} />
          <Route path="performance" element={<PerformancePage />} />
          <Route path="training" element={<TrainingPage />} />
          <Route path="about" element={<AboutPage />} />
          <Route path="settings" element={<SettingsPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
};

export default App;
