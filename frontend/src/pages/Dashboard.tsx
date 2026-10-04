import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Database,
  Layers,
  Target,
  Zap,
  ScanLine,
  ArrowRight,
  TrendingUp,
  Clock
} from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Cell
} from 'recharts';

import { MetricCard } from '../components/MetricCard';
import { ErrorAlert } from '../components/ErrorAlert';
import { LoadingSkeleton } from '../components/LoadingSkeleton';
import apiService, { extractErrorMessage } from '../services/api';
import type {
  ModelInfoResponse,
  DatasetInfoResponse,
  PredictionHistoryListResponse
} from '../types';

const CLASS_COLORS: Record<string, string> = {
  biodegradable: '#84cc16',
  cardboard: '#f59e0b',
  e_waste: '#a855f7',
  glass: '#06b6d4',
  metal: '#64748b',
  paper: '#3b82f6',
  plastic: '#10b981',
  trash: '#f43f5e',
};

export const Dashboard: React.FC = () => {
  const [modelInfo, setModelInfo] = useState<ModelInfoResponse | null>(null);
  const [datasetInfo, setDatasetInfo] = useState<DatasetInfoResponse | null>(null);
  const [recentPredictions, setRecentPredictions] = useState<PredictionHistoryListResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const loadDashboardData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [modelRes, datasetRes, historyRes] = await Promise.all([
        apiService.getModelInfo(),
        apiService.getDatasetInfo(),
        apiService.getPredictions(5, 0),
      ]);
      setModelInfo(modelRes);
      setDatasetInfo(datasetRes);
      setRecentPredictions(historyRes);
    } catch (err) {
      setError(extractErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadDashboardData();
  }, []);

  if (isLoading) {
    return (
      <div className="space-y-6">
        <LoadingSkeleton rows={4} height="h-32" />
      </div>
    );
  }

  if (error) {
    return <ErrorAlert message={error} onRetry={loadDashboardData} />;
  }

  const accuracyPct = modelInfo ? (modelInfo.test_accuracy * 100).toFixed(2) : '87.07';
  const macroF1Pct = modelInfo ? (modelInfo.macro_f1 * 100).toFixed(2) : '85.14';
  const weightedF1Pct = modelInfo ? (modelInfo.weighted_f1 * 100).toFixed(2) : '87.00';
  const totalImages = datasetInfo?.total_images || 2527;
  const numClasses = datasetInfo?.classes?.length || 6;

  const distributionChartData = datasetInfo?.class_distribution.map((item) => ({
    name: item.class_name.charAt(0).toUpperCase() + item.class_name.slice(1),
    count: item.count,
    percentage: item.percentage,
    color: CLASS_COLORS[item.class_name.toLowerCase()] || '#6366f1',
  })) || [];

  return (
    <div className="space-y-8">
      {/* Quick Action Hero Banner */}
      <div className="bg-gradient-to-r from-slate-900 via-slate-800 to-emerald-950 rounded-2xl p-6 md:p-8 text-white shadow-lg border border-slate-700/50 flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
        <div className="space-y-2">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/20 text-emerald-300 text-xs font-semibold border border-emerald-500/30">
            <Zap className="w-3.5 h-3.5" /> MobileNetV2 Deep Learning Inference Active
          </div>
          <h2 className="text-2xl md:text-3xl font-bold tracking-tight">
            AI-Powered Waste Classification System
          </h2>
          <p className="text-slate-300 text-sm max-w-2xl leading-relaxed">
            Instant 6-class waste categorization powered by transfer learning on the TrashNet dataset. Includes Grad-CAM convolutional attention maps and full SQLite audit history.
          </p>
        </div>
        <Link
          to="/predict"
          className="flex items-center gap-2 px-6 py-3.5 rounded-xl bg-emerald-500 text-slate-950 font-bold hover:bg-emerald-400 transition-all shadow-lg shadow-emerald-500/25 shrink-0 group"
        >
          <ScanLine className="w-5 h-5" />
          <span>Classify Image Now</span>
          <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
        </Link>
      </div>

      {/* KPI Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <MetricCard
          title="Dataset Images"
          value={totalImages.toLocaleString()}
          subtitle="TrashNet 6 Classes"
          icon={Database}
          color="blue"
          trend="100% Verified"
        />
        <MetricCard
          title="Classification Classes"
          value={numClasses}
          subtitle="Cardboard, Glass, Metal, Paper, Plastic, Trash"
          icon={Layers}
          color="emerald"
        />
        <MetricCard
          title="Test Accuracy"
          value={`${accuracyPct}%`}
          subtitle="Evaluated on 379 test samples"
          icon={Target}
          color="teal"
          trend="+18.47% vs CNN"
        />
        <MetricCard
          title="Macro F1-Score"
          value={`${macroF1Pct}%`}
          subtitle={`Weighted F1: ${weightedF1Pct}%`}
          icon={TrendingUp}
          color="amber"
          trend="Balanced"
        />
      </div>

      {/* Main Charts & Model Summary Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Class Distribution Bar Chart */}
        <div className="lg:col-span-2 bg-white rounded-xl p-6 border border-slate-200/80 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="font-bold text-slate-900 text-base">TrashNet Class Distribution</h3>
              <p className="text-xs text-slate-500">2,527 stratified images across 6 standard categories</p>
            </div>
            <Link to="/dataset" className="text-xs font-semibold text-emerald-600 hover:text-emerald-700">
              View Dataset Splits &rarr;
            </Link>
          </div>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={distributionChartData} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
                <XAxis dataKey="name" stroke="#64748b" fontSize={12} tickLine={false} />
                <YAxis stroke="#64748b" fontSize={12} tickLine={false} />
                <Tooltip
                  formatter={(val: any) => [`${val} images`, 'Count']}
                  contentStyle={{ borderRadius: '8px', border: '1px solid #e2e8f0', fontSize: '12px' }}
                />
                <Bar dataKey="count" radius={[6, 6, 0, 0]}>
                  {distributionChartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Model Architecture Quick Specs */}
        <div className="bg-white rounded-xl p-6 border border-slate-200/80 shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-bold text-slate-900 text-base">Active Model</h3>
              <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800">
                Production
              </span>
            </div>

            <div className="space-y-3 text-xs">
              <div className="p-3 rounded-lg bg-slate-50 border border-slate-100">
                <span className="text-slate-400 block font-medium">Architecture</span>
                <span className="font-bold text-slate-800 text-sm">{modelInfo?.model_name || 'MobileNetV2'}</span>
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-100">
                  <span className="text-slate-400 block">Parameters</span>
                  <span className="font-mono font-bold text-slate-800">
                    {modelInfo?.total_parameters?.toLocaleString() || '2,422,726'}
                  </span>
                </div>
                <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-100">
                  <span className="text-slate-400 block">Avg Latency</span>
                  <span className="font-mono font-bold text-emerald-700">~61.15 ms</span>
                </div>
              </div>
              <div className="p-3 rounded-lg bg-slate-50 border border-slate-100">
                <span className="text-slate-400 block font-medium">Input Specification</span>
                <span className="font-mono font-bold text-slate-800">224 x 224 x 3 (RGB)</span>
              </div>
            </div>
          </div>

          <Link
            to="/performance"
            className="mt-4 w-full py-2.5 text-center rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold text-xs transition"
          >
            Explore Performance & Confusion Matrix
          </Link>
        </div>
      </div>

      {/* Recent Predictions Table */}
      <div className="bg-white rounded-xl p-6 border border-slate-200/80 shadow-sm">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="font-bold text-slate-900 text-base">Recent Classifications</h3>
            <p className="text-xs text-slate-500">Live predictions stored in SQLite database</p>
          </div>
          <Link to="/history" className="text-xs font-semibold text-emerald-600 hover:text-emerald-700">
            Full Audit History &rarr;
          </Link>
        </div>

        {recentPredictions?.predictions && recentPredictions.predictions.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-500 font-semibold uppercase tracking-wider border-y border-slate-200">
                <tr>
                  <th className="py-3 px-4">Prediction ID</th>
                  <th className="py-3 px-4">Predicted Class</th>
                  <th className="py-3 px-4">Confidence</th>
                  <th className="py-3 px-4">Latency</th>
                  <th className="py-3 px-4">Timestamp</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-slate-700">
                {recentPredictions.predictions.map((p) => (
                  <tr key={p.prediction_id} className="hover:bg-slate-50/60 transition">
                    <td className="py-3 px-4 font-mono text-slate-500">{p.prediction_id.slice(0, 8)}...</td>
                    <td className="py-3 px-4">
                      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-bold capitalize bg-slate-100 text-slate-800">
                        {p.predicted_class}
                      </span>
                    </td>
                    <td className="py-3 px-4 font-mono font-semibold text-emerald-700">
                      {(p.confidence * 100).toFixed(2)}%
                    </td>
                    <td className="py-3 px-4 font-mono text-slate-500">{p.inference_time_ms} ms</td>
                    <td className="py-3 px-4 text-slate-500">{p.created_at}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="py-8 text-center text-slate-400 text-xs">
            <Clock className="w-8 h-8 mx-auto text-slate-300 mb-2" />
            No classifications recorded yet. Upload an image to start!
          </div>
        )}
      </div>
    </div>
  );
};
