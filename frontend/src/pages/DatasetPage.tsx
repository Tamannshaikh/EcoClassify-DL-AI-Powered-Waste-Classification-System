import React, { useEffect, useState } from 'react';
import {
  Database,
  Layers,
  PieChart as PieChartIcon,
  BarChart3,
  ShieldCheck,
  FileCheck2,
  FolderTree
} from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Cell,
  PieChart,
  Pie,
  Legend
} from 'recharts';

import { MetricCard } from '../components/MetricCard';
import { ErrorAlert } from '../components/ErrorAlert';
import { LoadingSkeleton } from '../components/LoadingSkeleton';
import apiService, { extractErrorMessage } from '../services/api';
import type { DatasetInfoResponse } from '../types';

const CLASS_COLORS: Record<string, string> = {
  cardboard: '#f59e0b',
  glass: '#06b6d4',
  metal: '#64748b',
  paper: '#3b82f6',
  plastic: '#10b981',
  trash: '#f43f5e',
};

export const DatasetPage: React.FC = () => {
  const [datasetInfo, setDatasetInfo] = useState<DatasetInfoResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDataset = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await apiService.getDatasetInfo();
      setDatasetInfo(data);
    } catch (err) {
      setError(extractErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDataset();
  }, []);

  if (isLoading) {
    return (
      <div className="space-y-6 max-w-6xl mx-auto">
        <LoadingSkeleton rows={4} height="h-32" />
      </div>
    );
  }

  if (error || !datasetInfo) {
    return (
      <div className="max-w-6xl mx-auto">
        <ErrorAlert message={error || 'Failed to load dataset metadata.'} onRetry={fetchDataset} />
      </div>
    );
  }

  const chartData = datasetInfo.class_distribution.map((item) => ({
    name: item.class_name.charAt(0).toUpperCase() + item.class_name.slice(1),
    count: item.count,
    percentage: item.percentage,
    color: CLASS_COLORS[item.class_name.toLowerCase()] || '#6366f1',
  }));

  const splitData = [
    { name: 'Training Set (70%)', count: datasetInfo.splits.train, color: '#10b981' },
    { name: 'Validation Set (15%)', count: datasetInfo.splits.val, color: '#f59e0b' },
    { name: 'Test Set (15%)', count: datasetInfo.splits.test, color: '#3b82f6' },
  ];

  return (
    <div className="space-y-8 max-w-6xl mx-auto">
      {/* Page Title & Intro */}
      <div className="border-b border-slate-200 pb-4">
        <h2 className="text-2xl font-bold text-slate-900 tracking-tight">TrashNet Dataset Inventory</h2>
        <p className="text-sm text-slate-500 mt-1">
          Detailed breakdown of the 2,527 benchmark images, class distributions, and leak-free split partitioning.
        </p>
      </div>

      {/* Top Metrics Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <MetricCard
          title="Total Dataset"
          value={datasetInfo.total_images.toLocaleString()}
          subtitle="Images (512x384 RGB)"
          icon={Database}
          color="blue"
        />
        <MetricCard
          title="Training Split"
          value={datasetInfo.splits.train.toLocaleString()}
          subtitle="70% of dataset"
          icon={FolderTree}
          color="emerald"
        />
        <MetricCard
          title="Validation Split"
          value={datasetInfo.splits.val.toLocaleString()}
          subtitle="15% for checkpointing"
          icon={Layers}
          color="amber"
        />
        <MetricCard
          title="Test Split"
          value={datasetInfo.splits.test.toLocaleString()}
          subtitle="15% held-out evaluation"
          icon={FileCheck2}
          color="teal"
        />
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Class Distribution Chart */}
        <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-bold text-slate-900 text-sm flex items-center gap-2">
              <BarChart3 className="w-4 h-4 text-emerald-600" />
              <span>Class Sample Distribution</span>
            </h3>
            <span className="text-xs text-slate-400">2,527 Total</span>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
                <XAxis dataKey="name" stroke="#64748b" fontSize={11} tickLine={false} />
                <YAxis stroke="#64748b" fontSize={11} tickLine={false} />
                <Tooltip
                  formatter={(val: any) => [`${val} images`, 'Count']}
                  contentStyle={{ borderRadius: '8px', border: '1px solid #e2e8f0', fontSize: '12px' }}
                />
                <Bar dataKey="count" radius={[6, 6, 0, 0]}>
                  {chartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Dataset Split Donut Chart */}
        <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-bold text-slate-900 text-sm flex items-center gap-2">
              <PieChartIcon className="w-4 h-4 text-teal-600" />
              <span>Stratified Split Breakdown</span>
            </h3>
            <span className="text-xs text-slate-400">70 / 15 / 15 Partition</span>
          </div>

          <div className="h-64 w-full flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={splitData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={85}
                  paddingAngle={4}
                  dataKey="count"
                >
                  {splitData.map((entry, index) => (
                    <Cell key={`cell-split-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  formatter={(val: any) => [`${val} images`, 'Samples']}
                  contentStyle={{ borderRadius: '8px', border: '1px solid #e2e8f0', fontSize: '12px' }}
                />
                <Legend
                  verticalAlign="bottom"
                  iconSize={10}
                  wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Detailed Class Distribution Table */}
      <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-sm">
        <h3 className="font-bold text-slate-900 text-sm mb-4">Class Frequency & Composition Table</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-500 font-semibold uppercase tracking-wider border-y border-slate-200">
              <tr>
                <th className="py-3 px-4">Class Name</th>
                <th className="py-3 px-4">Total Samples</th>
                <th className="py-3 px-4">Dataset Share</th>
                <th className="py-3 px-4">Train (70%)</th>
                <th className="py-3 px-4">Val (15%)</th>
                <th className="py-3 px-4">Test (15%)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-700">
              {datasetInfo.class_distribution.map((item) => {
                const trainEst = Math.round(item.count * 0.70);
                const valEst = Math.round(item.count * 0.15);
                const testEst = item.count - trainEst - valEst;
                return (
                  <tr key={item.class_name} className="hover:bg-slate-50/70 transition">
                    <td className="py-3 px-4 font-bold capitalize text-slate-900 flex items-center gap-2">
                      <span
                        className="w-2.5 h-2.5 rounded-full"
                        style={{ backgroundColor: CLASS_COLORS[item.class_name.toLowerCase()] || '#6366f1' }}
                      />
                      {item.class_name}
                    </td>
                    <td className="py-3 px-4 font-mono font-bold text-slate-900">{item.count}</td>
                    <td className="py-3 px-4 font-mono text-emerald-700 font-semibold">{item.percentage.toFixed(2)}%</td>
                    <td className="py-3 px-4 font-mono text-slate-600">{trainEst}</td>
                    <td className="py-3 px-4 font-mono text-slate-600">{valEst}</td>
                    <td className="py-3 px-4 font-mono text-slate-600">{testEst}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Dataset Integrity & Audit Report */}
      <div className="bg-slate-900 rounded-2xl p-6 text-white border border-slate-800 shadow-md space-y-4">
        <div className="flex items-center gap-2 text-emerald-400 font-bold text-sm">
          <ShieldCheck className="w-5 h-5" />
          <span>Verified Dataset Integrity & Duplicate Protection</span>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs text-slate-300">
          <div className="p-3.5 rounded-xl bg-slate-800/80 border border-slate-700/60">
            <span className="font-bold text-white block mb-1">Zero Corrupted Images</span>
            <p className="text-slate-400 leading-relaxed">
              Every single image of the 2,527 was structurally verified with Pillow headers and uniform 512×384 RGB channel alignment.
            </p>
          </div>
          <div className="p-3.5 rounded-xl bg-slate-800/80 border border-slate-700/60">
            <span className="font-bold text-white block mb-1">Group-Aware Leakage Prevention</span>
            <p className="text-slate-400 leading-relaxed">
              All 3 cross-class SHA-256 duplicate pairs were strictly isolated inside the training set, guaranteeing 0% test contamination.
            </p>
          </div>
          <div className="p-3.5 rounded-xl bg-slate-800/80 border border-slate-700/60">
            <span className="font-bold text-white block mb-1">Exact Standard Classes</span>
            <p className="text-slate-400 leading-relaxed">
              Strict adherence to standard TrashNet classes: cardboard, glass, metal, paper, plastic, and trash.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
