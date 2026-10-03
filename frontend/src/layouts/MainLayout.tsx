import React, { useEffect, useState } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import { Sidebar } from '../components/Sidebar';
import { Header } from '../components/Header';
import type { HealthResponse } from '../types';
import apiService from '../services/api';

const pageTitles: Record<string, { title: string; subtitle: string }> = {
  '/': { title: 'Analytics Dashboard', subtitle: 'Overview of DL Model Metrics & System Status' },
  '/predict': { title: 'AI Waste Classifier & Grad-CAM', subtitle: 'Upload real waste images for deep learning classification' },
  '/history': { title: 'Prediction History', subtitle: 'Audit log of stored classifications in SQLite database' },
  '/dataset': { title: 'TrashNet Dataset', subtitle: 'Dataset distribution, splits, and class inventory' },
  '/performance': { title: 'Model Evaluation & Metrics', subtitle: 'MobileNetV2 confusion matrix, precision, recall & F1' },
  '/training': { title: 'Model Architectures & Training', subtitle: 'Baseline Custom CNN vs Final MobileNetV2 comparison' },
  '/about': { title: 'About the DL System', subtitle: 'Project architecture, tech stack & dataset citations' },
  '/settings': { title: 'System Settings', subtitle: 'API connection parameters and environment configurations' },
};

export const MainLayout: React.FC = () => {
  const location = useLocation();
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [isLoadingHealth, setIsLoadingHealth] = useState<boolean>(true);
  const [isRefreshing, setIsRefreshing] = useState<boolean>(false);

  const fetchHealth = async () => {
    setIsRefreshing(true);
    try {
      const data = await apiService.getHealth();
      setHealth(data);
    } catch (err) {
      console.error('Failed to fetch health:', err);
    } finally {
      setIsLoadingHealth(false);
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    fetchHealth();
  }, []);

  const currentMeta = pageTitles[location.pathname] || {
    title: 'Waste Classification System',
    subtitle: 'Deep Learning Vision Platform',
  };

  return (
    <div className="flex h-screen bg-slate-50 overflow-hidden">
      {/* Sidebar */}
      <Sidebar health={health} isLoadingHealth={isLoadingHealth} />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <Header
          title={currentMeta.title}
          subtitle={currentMeta.subtitle}
          onRefresh={fetchHealth}
          isRefreshing={isRefreshing}
        />
        <main className="flex-1 overflow-y-auto p-8 bg-slate-50">
          <Outlet />
        </main>
      </div>
    </div>
  );
};
