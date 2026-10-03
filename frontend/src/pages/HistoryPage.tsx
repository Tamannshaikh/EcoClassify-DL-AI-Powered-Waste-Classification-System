import React, { useEffect, useState } from 'react';
import {
  History,
  Trash2,
  Eye,
  RefreshCw,
  CheckCircle2,
  X,
  ChevronLeft,
  ChevronRight,
  Image as ImageIcon,
  AlertTriangle
} from 'lucide-react';
import { ErrorAlert } from '../components/ErrorAlert';
import { LoadingSkeleton } from '../components/LoadingSkeleton';
import { ProbabilityBar } from '../components/ProbabilityBar';
import apiService, { extractErrorMessage } from '../services/api';
import type { PredictionHistoryItem } from '../types';

export const HistoryPage: React.FC = () => {
  const [predictions, setPredictions] = useState<PredictionHistoryItem[]>([]);
  const [totalCount, setTotalCount] = useState<number>(0);
  const [limit] = useState<number>(15);
  const [page, setPage] = useState<number>(1);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedRecord, setSelectedRecord] = useState<PredictionHistoryItem | null>(null);
  const [recordToDelete, setRecordToDelete] = useState<PredictionHistoryItem | null>(null);
  const [isDeletingId, setIsDeletingId] = useState<string | null>(null);

  const getFullImageUrl = (url?: string) => {
    if (!url) return '';
    if (url.startsWith('http://') || url.startsWith('https://')) return url;
    return `http://127.0.0.1:8000${url.startsWith('/') ? '' : '/'}${url}`;
  };

  const fetchHistory = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const offset = (page - 1) * limit;
      const data = await apiService.getPredictions(limit, offset);
      setPredictions(data.predictions);
      setTotalCount(data.total);
    } catch (err) {
      setError(extractErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, [page]);

  const confirmDelete = async (id: string) => {
    setIsDeletingId(id);
    try {
      await apiService.deletePrediction(id);
      if (selectedRecord?.prediction_id === id) {
        setSelectedRecord(null);
      }
      setRecordToDelete(null);
      await fetchHistory();
    } catch (err) {
      setError(`Failed to delete record: ${extractErrorMessage(err)}`);
    } finally {
      setIsDeletingId(null);
    }
  };

  const totalPages = Math.max(1, Math.ceil(totalCount / limit));

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      {/* Header bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 pb-4">
        <div>
          <h2 className="text-2xl font-bold text-slate-900 tracking-tight">Prediction Audit History</h2>
          <p className="text-sm text-slate-500 mt-1">
            Browse, inspect, and manage persistent classification logs with stored analyzed images in SQLite.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-xs font-semibold px-3 py-1.5 rounded-lg bg-slate-100 text-slate-700 border border-slate-200">
            Total Records: <strong>{totalCount}</strong>
          </span>
          <button
            onClick={fetchHistory}
            disabled={isLoading}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white border border-slate-300 text-xs font-semibold text-slate-700 hover:bg-slate-50 transition shadow-sm disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin text-emerald-600' : ''}`} />
            Refresh
          </button>
        </div>
      </div>

      {error && <ErrorAlert message={error} onRetry={fetchHistory} />}

      {/* History Table Container */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-sm overflow-hidden">
        {isLoading ? (
          <div className="p-6">
            <LoadingSkeleton rows={5} height="h-12" />
          </div>
        ) : predictions.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50/80 text-slate-500 font-semibold uppercase tracking-wider border-b border-slate-200">
                <tr>
                  <th className="py-3.5 px-4">ID</th>
                  <th className="py-3.5 px-4">Image</th>
                  <th className="py-3.5 px-4">Original Filename</th>
                  <th className="py-3.5 px-4">Predicted Class</th>
                  <th className="py-3.5 px-4">Confidence</th>
                  <th className="py-3.5 px-4">Inference Latency</th>
                  <th className="py-3.5 px-4">Grad-CAM</th>
                  <th className="py-3.5 px-4">Timestamp</th>
                  <th className="py-3.5 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-slate-700">
                {predictions.map((p) => (
                  <tr key={p.prediction_id} className="hover:bg-slate-50/70 transition">
                    <td className="py-3.5 px-4 font-mono font-bold text-slate-900">
                      {p.prediction_id}
                    </td>
                    <td className="py-3.5 px-4">
                      {p.image_url ? (
                        <div className="w-10 h-10 rounded-lg overflow-hidden border border-slate-200 bg-slate-50 relative flex items-center justify-center">
                          <img
                            src={getFullImageUrl(p.image_url)}
                            alt={p.prediction_id}
                            className="w-full h-full object-cover cursor-pointer hover:opacity-80 transition"
                            onClick={() => setSelectedRecord(p)}
                            onError={(e) => {
                              (e.target as HTMLElement).style.display = 'none';
                              const fallback = (e.target as HTMLElement).parentElement?.querySelector('.img-fallback');
                              if (fallback) (fallback as HTMLElement).classList.remove('hidden');
                            }}
                          />
                          <div className="img-fallback hidden w-full h-full flex items-center justify-center text-slate-400 bg-slate-100">
                            <ImageIcon className="w-4 h-4" />
                          </div>
                        </div>
                      ) : (
                        <div className="w-10 h-10 rounded-lg bg-slate-100 border border-slate-200 flex items-center justify-center text-slate-400">
                          <ImageIcon className="w-4 h-4" />
                        </div>
                      )}
                    </td>
                    <td className="py-3.5 px-4 font-medium text-slate-800 max-w-[140px] truncate" title={p.original_filename}>
                      {p.original_filename}
                    </td>
                    <td className="py-3.5 px-4">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold capitalize bg-slate-100 text-slate-800">
                        {p.predicted_class}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 font-mono font-bold text-emerald-700">
                      {(p.confidence * 100).toFixed(2)}%
                    </td>
                    <td className="py-3.5 px-4 font-mono text-slate-500">{p.inference_time_ms} ms</td>
                    <td className="py-3.5 px-4">
                      {p.gradcam_generated ? (
                        <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                          <CheckCircle2 className="w-3 h-3" /> Yes
                        </span>
                      ) : (
                        <span className="text-[11px] text-slate-400">No</span>
                      )}
                    </td>
                    <td className="py-3.5 px-4 text-slate-500 whitespace-nowrap">{p.created_at}</td>
                    <td className="py-3.5 px-4 text-right">
                      <div className="flex items-center justify-end gap-1.5">
                        <button
                          onClick={() => setSelectedRecord(p)}
                          className="p-1.5 rounded-lg text-slate-500 hover:text-emerald-600 hover:bg-emerald-50 transition"
                          title="View Probability Details & Image"
                        >
                          <Eye className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => setRecordToDelete(p)}
                          className="p-1.5 rounded-lg text-slate-500 hover:text-rose-600 hover:bg-rose-50 transition"
                          title="Delete from SQLite & Disk"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="py-16 text-center text-slate-400 space-y-2">
            <History className="w-10 h-10 mx-auto text-slate-300 mb-1" />
            <p className="font-semibold text-slate-700 text-sm">No History Records Available</p>
            <p className="text-xs text-slate-400 max-w-sm mx-auto">
              Run predictions in the Image Prediction tab to generate verifiable persistent records.
            </p>
          </div>
        )}

        {/* Pagination Footer */}
        {totalPages > 1 && (
          <div className="p-4 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
            <span>
              Page <strong>{page}</strong> of <strong>{totalPages}</strong> ({totalCount} total)
            </span>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page <= 1}
                className="p-1.5 rounded-lg border border-slate-200 hover:bg-slate-100 disabled:opacity-40 transition"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              <button
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                disabled={page >= totalPages}
                className="p-1.5 rounded-lg border border-slate-200 hover:bg-slate-100 disabled:opacity-40 transition"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Delete Confirmation Modal */}
      {recordToDelete && (
        <div className="fixed inset-0 z-50 bg-slate-950/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl border border-slate-200 space-y-4 animate-in fade-in zoom-in duration-150">
            <div className="flex items-center gap-3">
              <div className="p-3 rounded-full bg-rose-50 text-rose-600 border border-rose-100">
                <AlertTriangle className="w-6 h-6" />
              </div>
              <div>
                <h3 className="font-bold text-slate-900 text-base">Delete Prediction Record</h3>
                <p className="text-xs text-slate-500 font-mono">ID: {recordToDelete.prediction_id}</p>
              </div>
            </div>

            <p className="text-xs text-slate-600 leading-relaxed">
              Are you sure you want to delete prediction <strong className="font-mono text-slate-800">{recordToDelete.prediction_id}</strong> (<span className="capitalize">{recordToDelete.predicted_class}</span>, {recordToDelete.original_filename}) and remove its stored image from SQLite?
            </p>

            <div className="flex items-center justify-end gap-2 pt-2">
              <button
                onClick={() => setRecordToDelete(null)}
                disabled={isDeletingId !== null}
                className="px-4 py-2 rounded-xl border border-slate-200 text-xs font-semibold text-slate-700 hover:bg-slate-50 transition"
              >
                Cancel
              </button>
              <button
                onClick={() => confirmDelete(recordToDelete.prediction_id)}
                disabled={isDeletingId !== null}
                className="px-4 py-2 rounded-xl bg-rose-600 text-white text-xs font-semibold hover:bg-rose-700 transition flex items-center gap-1.5 shadow-sm disabled:opacity-50"
              >
                {isDeletingId ? (
                  <>
                    <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                    <span>Deleting...</span>
                  </>
                ) : (
                  <>
                    <Trash2 className="w-3.5 h-3.5" />
                    <span>Delete Record</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Detail Modal */}
      {selectedRecord && (
        <div className="fixed inset-0 z-50 bg-slate-950/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl border border-slate-200 space-y-5 animate-in fade-in zoom-in duration-150 max-h-[90vh] overflow-y-auto">
            <div className="flex items-start justify-between border-b border-slate-100 pb-3">
              <div>
                <h3 className="font-bold text-slate-900 text-lg">Prediction Audit Record</h3>
                <p className="text-sm font-mono font-bold text-emerald-600 mt-0.5">ID: {selectedRecord.prediction_id}</p>
              </div>
              <button
                onClick={() => setSelectedRecord(null)}
                className="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Stored Analyzed Image */}
            <div className="rounded-xl overflow-hidden border border-slate-200 bg-slate-50 flex items-center justify-center p-2 min-h-[160px] relative">
              {selectedRecord.image_url ? (
                <img
                  src={getFullImageUrl(selectedRecord.image_url)}
                  alt={selectedRecord.prediction_id}
                  className="max-h-60 w-auto object-contain rounded-lg shadow-xs"
                  onError={(e) => {
                    (e.target as HTMLElement).style.display = 'none';
                    const fallback = (e.target as HTMLElement).parentElement?.querySelector('.modal-img-fallback');
                    if (fallback) (fallback as HTMLElement).classList.remove('hidden');
                  }}
                />
              ) : null}
              <div className={`modal-img-fallback flex flex-col items-center justify-center text-slate-400 py-6 ${selectedRecord.image_url ? 'hidden' : 'flex'}`}>
                <ImageIcon className="w-8 h-8 text-slate-300 mb-1" />
                <span className="text-xs font-medium text-slate-500">Analyzed image unavailable</span>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3 text-xs">
              <div className="p-3 rounded-lg bg-slate-50 border border-slate-100">
                <span className="text-slate-400 block font-medium">Original Filename</span>
                <span className="font-bold text-slate-800 truncate block mt-0.5" title={selectedRecord.original_filename}>
                  {selectedRecord.original_filename}
                </span>
              </div>
              <div className="p-3 rounded-lg bg-slate-50 border border-slate-100">
                <span className="text-slate-400 block font-medium">Logged Timestamp</span>
                <span className="font-bold text-slate-800 block mt-0.5">{selectedRecord.created_at}</span>
              </div>
              <div className="p-3 rounded-lg bg-emerald-50 border border-emerald-100">
                <span className="text-emerald-700 block font-medium">Predicted Class</span>
                <span className="font-bold text-emerald-950 text-base capitalize block mt-0.5">
                  {selectedRecord.predicted_class}
                </span>
              </div>
              <div className="p-3 rounded-lg bg-emerald-50 border border-emerald-100">
                <span className="text-emerald-700 block font-medium">Confidence Score</span>
                <span className="font-mono font-bold text-emerald-950 text-base block mt-0.5">
                  {(selectedRecord.confidence * 100).toFixed(2)}%
                </span>
              </div>
            </div>

            {/* Probability Breakdown */}
            <div className="space-y-2">
              <h4 className="text-xs font-bold text-slate-700">Stored Probability Distribution:</h4>
              <div className="space-y-2">
                {Object.entries(selectedRecord.probabilities).map(([cls, prob]) => (
                  <ProbabilityBar
                    key={cls}
                    classNameString={cls}
                    probability={prob}
                    isTopClass={cls.toLowerCase() === selectedRecord.predicted_class.toLowerCase()}
                  />
                ))}
              </div>
            </div>

            <div className="pt-2 flex items-center justify-between border-t border-slate-100">
              <button
                onClick={() => {
                  const target = selectedRecord;
                  setSelectedRecord(null);
                  setRecordToDelete(target);
                }}
                className="px-3 py-2 rounded-xl text-rose-600 hover:bg-rose-50 text-xs font-semibold transition flex items-center gap-1.5"
              >
                <Trash2 className="w-4 h-4" />
                <span>Delete Record</span>
              </button>
              <button
                onClick={() => setSelectedRecord(null)}
                className="px-4 py-2 rounded-xl bg-slate-900 text-white text-xs font-semibold hover:bg-slate-800 transition"
              >
                Close Audit View
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
