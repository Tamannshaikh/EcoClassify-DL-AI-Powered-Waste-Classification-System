import React, { useEffect, useState } from 'react';
import {
  Server,
  Cpu,
  CheckCircle2,
  AlertCircle,
  RefreshCw,
  ShieldCheck
} from 'lucide-react';
import { ErrorAlert } from '../components/ErrorAlert';
import { LoadingSkeleton } from '../components/LoadingSkeleton';
import apiService, { extractErrorMessage } from '../services/api';
import type { HealthResponse } from '../types';

export const SettingsPage: React.FC = () => {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [pingLatency, setPingLatency] = useState<number | null>(null);

  const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/v1';

  const checkConnection = async () => {
    setIsLoading(true);
    setError(null);
    const t0 = performance.now();
    try {
      const data = await apiService.getHealth();
      const t1 = performance.now();
      setPingLatency(Math.round(t1 - t0));
      setHealth(data);
    } catch (err) {
      setError(extractErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    checkConnection();
  }, []);

  return (
    <div className="space-y-8 max-w-4xl mx-auto">
      {/* Header */}
      <div className="border-b border-slate-200 pb-4">
        <h2 className="text-2xl font-bold text-slate-900 tracking-tight">System Settings & Status</h2>
        <p className="text-sm text-slate-500 mt-1">
          Inspect backend connection status, active model weights, and local environment configurations.
        </p>
      </div>

      {error && <ErrorAlert message={error} onRetry={checkConnection} />}

      {/* Backend Connection Card */}
      <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-sm space-y-5">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-emerald-100 flex items-center justify-center text-emerald-700 font-bold">
              <Server className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-bold text-slate-900 text-base">FastAPI REST Server</h3>
              <p className="text-xs text-slate-400">Local backend connection monitor</p>
            </div>
          </div>

          <button
            onClick={checkConnection}
            disabled={isLoading}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold transition disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin text-emerald-600' : ''}`} />
            Ping Backend
          </button>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
          <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-100 space-y-1">
            <span className="text-slate-400 font-medium">Configured Base URL</span>
            <div className="font-mono font-bold text-slate-800 text-xs break-all">{apiBaseUrl}</div>
          </div>

          <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-100 space-y-1">
            <span className="text-slate-400 font-medium">Connection Status</span>
            <div>
              {isLoading ? (
                <span className="text-amber-600 font-semibold">Testing connection...</span>
              ) : health?.status === 'ok' ? (
                <span className="inline-flex items-center gap-1 text-emerald-600 font-bold">
                  <CheckCircle2 className="w-4 h-4" /> Online ({pingLatency} ms ping)
                </span>
              ) : (
                <span className="inline-flex items-center gap-1 text-rose-600 font-bold">
                  <AlertCircle className="w-4 h-4" /> Offline / Disconnected
                </span>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Model Status Card */}
      <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-sm space-y-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-teal-100 flex items-center justify-center text-teal-700 font-bold">
            <Cpu className="w-5 h-5" />
          </div>
          <div>
            <h3 className="font-bold text-slate-900 text-base">Model Runtime Environment</h3>
            <p className="text-xs text-slate-400">TensorFlow / Keras model loaded into memory</p>
          </div>
        </div>

        {isLoading ? (
          <LoadingSkeleton rows={2} height="h-16" />
        ) : health ? (
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
            <div className="p-3 rounded-lg bg-slate-50 border border-slate-100">
              <span className="text-slate-400 block font-medium">Model Name</span>
              <span className="font-bold text-slate-800 text-xs block mt-0.5">{health.model_name}</span>
            </div>
            <div className="p-3 rounded-lg bg-slate-50 border border-slate-100">
              <span className="text-slate-400 block font-medium">Model Version</span>
              <span className="font-bold text-slate-800 text-xs block mt-0.5">{health.model_version}</span>
            </div>
            <div className="p-3 rounded-lg bg-slate-50 border border-slate-100">
              <span className="text-slate-400 block font-medium">Target Classes</span>
              <span className="font-bold text-slate-800 text-xs block mt-0.5">
                {health.classes.join(', ')}
              </span>
            </div>
          </div>
        ) : null}
      </div>

      {/* Security & System Diagnostics */}
      <div className="bg-slate-900 rounded-2xl p-6 text-white border border-slate-800 shadow-md space-y-4">
        <div className="flex items-center gap-2 text-emerald-400 font-bold text-sm">
          <ShieldCheck className="w-5 h-5" />
          <span>Local Security & Execution Parameters</span>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs text-slate-300">
          <div className="p-3.5 rounded-xl bg-slate-800/80 border border-slate-700/60">
            <span className="font-bold text-white block mb-0.5">Client-Side File Safeguards</span>
            <p className="text-slate-400 leading-relaxed">
              Enforces 10MB maximum upload limit and strict MIME validation prior to payload dispatch to FastAPI.
            </p>
          </div>
          <div className="p-3.5 rounded-xl bg-slate-800/80 border border-slate-700/60">
            <span className="font-bold text-white block mb-0.5">Zero Cloud Telemetry</span>
            <p className="text-slate-400 leading-relaxed">
              All inference and history persistence reside exclusively in local memory and local SQLite storage.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
