import React, { useState, useRef } from 'react';
import {
  Upload,
  Image as ImageIcon,
  X,
  Zap,
  Eye,
  CheckCircle2,
  Clock,
  Sparkles,
  Info,
  RefreshCw
} from 'lucide-react';
import { ProbabilityBar } from '../components/ProbabilityBar';
import { ErrorAlert } from '../components/ErrorAlert';
import apiService, { extractErrorMessage } from '../services/api';
import type { PredictionResponse } from '../types';

const MAX_FILE_SIZE_MB = 10;
const ALLOWED_EXTENSIONS = ['image/jpeg', 'image/jpg', 'image/png'];

const DISPOSAL_TIPS: Record<string, { title: string; desc: string; bin: string }> = {
  cardboard: {
    title: 'Recyclable Paper/Cardboard',
    desc: 'Flatten cardboard boxes to save space. Keep dry and free of greasy food residue.',
    bin: 'Blue / Dry Recyclables Bin',
  },
  glass: {
    title: 'Recyclable Glass',
    desc: 'Rinse glass bottles and jars clean. Do not include broken lightbulbs, mirrors, or ceramics.',
    bin: 'Teal / Glass Recyclables Bin',
  },
  metal: {
    title: 'Recyclable Metal',
    desc: 'Rinse aluminum soda cans and steel food tins. Remove loose plastic wrappers.',
    bin: 'Grey / Metal Recyclables Bin',
  },
  paper: {
    title: 'Recyclable Clean Paper',
    desc: 'Newspapers, office paper, clean magazines. Do not recycle heavily soiled napkins or waxed paper.',
    bin: 'Blue / Paper Recyclables Bin',
  },
  plastic: {
    title: 'Recyclable Plastic Container',
    desc: 'Empty liquids and rinse. Check for resin identification codes (PET, HDPE). Crush bottles if possible.',
    bin: 'Yellow / Plastic Recyclables Bin',
  },
  trash: {
    title: 'Non-Recyclable Residual Waste',
    desc: 'Contaminated items, composite materials, or non-recyclable multi-layer packaging.',
    bin: 'Black / General Landfill Bin',
  },
};

export const PredictionPage: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [isGradCamRequested, setIsGradCamRequested] = useState<boolean>(true);
  const [isPredicting, setIsPredicting] = useState<boolean>(false);
  const [predictionResult, setPredictionResult] = useState<PredictionResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState<boolean>(false);
  const [activeImageView, setActiveImageView] = useState<'original' | 'gradcam'>('original');

  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const handleFileSelect = (file: File) => {
    setError(null);
    setPredictionResult(null);

    // Validate type
    if (!ALLOWED_EXTENSIONS.includes(file.type) && !file.name.match(/\.(jpg|jpeg|png)$/i)) {
      setError(`Unsupported file type '${file.name}'. Please upload a JPG, JPEG, or PNG image.`);
      return;
    }

    // Validate size (10 MB)
    if (file.size > MAX_FILE_SIZE_MB * 1024 * 1024) {
      setError(`File size (${(file.size / (1024 * 1024)).toFixed(2)} MB) exceeds the maximum allowed ${MAX_FILE_SIZE_MB}MB.`);
      return;
    }

    // Release old preview
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }

    setSelectedFile(file);
    const objectUrl = URL.createObjectURL(file);
    setPreviewUrl(objectUrl);
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFileSelect(e.dataTransfer.files[0]);
    }
  };

  const handleClear = () => {
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    setSelectedFile(null);
    setPreviewUrl(null);
    setPredictionResult(null);
    setError(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const executePrediction = async () => {
    if (!selectedFile) return;

    setIsPredicting(true);
    setError(null);

    try {
      let result: PredictionResponse;
      if (isGradCamRequested) {
        result = await apiService.predictGradCAM(selectedFile);
        if (result.gradcam_base64) {
          setActiveImageView('gradcam');
        }
      } else {
        result = await apiService.predictImage(selectedFile);
        setActiveImageView('original');
      }
      setPredictionResult(result);
    } catch (err) {
      setError(extractErrorMessage(err));
    } finally {
      setIsPredicting(false);
    }
  };

  return (
    <div className="space-y-8 max-w-6xl mx-auto">
      {/* Page Title & Intro */}
      <div className="border-b border-slate-200 pb-4">
        <h2 className="text-2xl font-bold text-slate-900 tracking-tight">AI Waste Classification</h2>
        <p className="text-sm text-slate-500 mt-1">
          Upload any waste item photo to predict its category among 6 classes using MobileNetV2 with Grad-CAM activation visualization.
        </p>
      </div>

      {error && <ErrorAlert message={error} onRetry={selectedFile ? executePrediction : undefined} />}

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left Column: Image Upload & Preview (5 cols) */}
        <div className="lg:col-span-5 space-y-5">
          <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-sm">
            <h3 className="font-bold text-slate-900 text-sm mb-3 flex items-center justify-between">
              <span>Image Upload</span>
              <span className="text-[11px] font-normal text-slate-400">Max {MAX_FILE_SIZE_MB}MB (JPG/PNG)</span>
            </h3>

            {/* Drag & Drop Box */}
            {!previewUrl ? (
              <div
                onDragOver={(e) => {
                  e.preventDefault();
                  setIsDragging(true);
                }}
                onDragLeave={() => setIsDragging(false)}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current?.click()}
                className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all flex flex-col items-center justify-center min-h-[260px] ${
                  isDragging
                    ? 'border-emerald-500 bg-emerald-50/50 scale-[1.01]'
                    : 'border-slate-300 hover:border-emerald-400 hover:bg-slate-50/60'
                }`}
              >
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/jpeg,image/png,image/jpg"
                  className="hidden"
                  onChange={(e) => {
                    if (e.target.files && e.target.files.length > 0) {
                      handleFileSelect(e.target.files[0]);
                    }
                  }}
                />
                <div className="w-14 h-14 rounded-2xl bg-emerald-50 border border-emerald-100 flex items-center justify-center text-emerald-600 mb-4 shadow-sm">
                  <Upload className="w-7 h-7" />
                </div>
                <p className="font-bold text-slate-800 text-sm">Drag & drop image here</p>
                <p className="text-xs text-slate-400 mt-1">or click to browse your computer</p>
                <div className="mt-4 flex gap-1.5 text-[10px] font-semibold text-slate-400 uppercase tracking-wider">
                  <span className="bg-slate-100 px-2 py-0.5 rounded">JPG</span>
                  <span className="bg-slate-100 px-2 py-0.5 rounded">JPEG</span>
                  <span className="bg-slate-100 px-2 py-0.5 rounded">PNG</span>
                </div>
              </div>
            ) : (
              /* Selected Image Preview */
              <div className="space-y-4">
                <div className="relative rounded-xl overflow-hidden border border-slate-200 bg-slate-950/5 aspect-square flex items-center justify-center">
                  <img
                    src={
                      activeImageView === 'gradcam' && predictionResult?.gradcam_base64
                        ? predictionResult.gradcam_base64
                        : previewUrl
                    }
                    alt="Upload Preview"
                    className="max-h-full max-w-full object-contain"
                  />
                  <button
                    onClick={handleClear}
                    disabled={isPredicting}
                    className="absolute top-3 right-3 p-1.5 rounded-full bg-slate-900/80 hover:bg-slate-900 text-white transition shadow-md disabled:opacity-50"
                    title="Remove image"
                  >
                    <X className="w-4 h-4" />
                  </button>

                  {/* Overlay Badge */}
                  <div className="absolute bottom-3 left-3 bg-slate-900/80 backdrop-blur-sm text-white px-2.5 py-1 rounded-md text-[11px] font-medium flex items-center gap-1.5">
                    <ImageIcon className="w-3.5 h-3.5" />
                    <span>{selectedFile?.name}</span>
                  </div>
                </div>

                {/* Switch between Original / Grad-CAM view */}
                {predictionResult?.gradcam_base64 && (
                  <div className="flex rounded-lg bg-slate-100 p-1 text-xs font-semibold">
                    <button
                      onClick={() => setActiveImageView('original')}
                      className={`flex-1 py-1.5 rounded-md transition ${
                        activeImageView === 'original'
                          ? 'bg-white text-slate-900 shadow-sm'
                          : 'text-slate-500 hover:text-slate-800'
                      }`}
                    >
                      Original Photo
                    </button>
                    <button
                      onClick={() => setActiveImageView('gradcam')}
                      className={`flex-1 py-1.5 rounded-md transition flex items-center justify-center gap-1 ${
                        activeImageView === 'gradcam'
                          ? 'bg-emerald-600 text-white shadow-sm'
                          : 'text-slate-500 hover:text-slate-800'
                      }`}
                    >
                      <Sparkles className="w-3 h-3" /> Grad-CAM Heatmap
                    </button>
                  </div>
                )}
              </div>
            )}

            {/* Settings & Action Button */}
            <div className="mt-5 space-y-4 pt-4 border-t border-slate-100">
              <label className="flex items-center gap-2.5 cursor-pointer text-xs font-medium text-slate-700 select-none">
                <input
                  type="checkbox"
                  checked={isGradCamRequested}
                  onChange={(e) => setIsGradCamRequested(e.target.checked)}
                  className="rounded border-slate-300 text-emerald-600 focus:ring-emerald-500 w-4 h-4"
                />
                <span>Generate Grad-CAM Attention Heatmap (Explainability)</span>
              </label>

              <button
                onClick={executePrediction}
                disabled={!selectedFile || isPredicting}
                className="w-full py-3.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 disabled:bg-slate-200 text-white disabled:text-slate-400 font-bold text-sm transition shadow-md shadow-emerald-700/20 disabled:shadow-none flex items-center justify-center gap-2"
              >
                {isPredicting ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin" />
                    <span>Analyzing Image...</span>
                  </>
                ) : (
                  <>
                    <Zap className="w-4 h-4" />
                    <span>Run Deep Learning Classification</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Right Column: Prediction Results & Probabilities (7 cols) */}
        <div className="lg:col-span-7 space-y-6">
          {predictionResult ? (
            <div className="space-y-6">
              {/* Primary Prediction Result Card */}
              <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-sm">
                <div className="flex items-start justify-between">
                  <div>
                    <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                      Top Classification Result
                    </span>
                    <h3 className="text-3xl font-extrabold text-slate-900 capitalize mt-1">
                      {predictionResult.predicted_class}
                    </h3>
                  </div>
                  <div className="text-right">
                    <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                      Model Confidence
                    </span>
                    <div className="text-3xl font-extrabold text-emerald-600 font-mono mt-1">
                      {(predictionResult.confidence * 100).toFixed(2)}%
                    </div>
                  </div>
                </div>

                {/* Meta details bar */}
                <div className="mt-4 pt-4 border-t border-slate-100 flex flex-wrap items-center justify-between text-xs text-slate-500 gap-2">
                  <div className="flex items-center gap-1.5">
                    <Clock className="w-3.5 h-3.5 text-slate-400" />
                    <span>Inference: <strong className="text-slate-700">{predictionResult.inference_time_ms} ms</strong></span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                    <span>Logged to SQLite (ID: <strong className="font-mono text-slate-800">{predictionResult.prediction_id}</strong>)</span>
                  </div>
                  <div className="text-slate-400">Model: {predictionResult.model_version}</div>
                </div>
              </div>

              {/* Disposal Guideline Info Box */}
              {DISPOSAL_TIPS[predictionResult.predicted_class.toLowerCase()] && (
                <div className="bg-emerald-50/70 border border-emerald-200/80 rounded-2xl p-5 text-xs text-emerald-950">
                  <div className="flex items-center gap-2 font-bold text-sm text-emerald-900 mb-1">
                    <Info className="w-4 h-4 text-emerald-600" />
                    <span>Disposal Guide: {DISPOSAL_TIPS[predictionResult.predicted_class.toLowerCase()].title}</span>
                  </div>
                  <p className="text-emerald-800 leading-relaxed mb-2">
                    {DISPOSAL_TIPS[predictionResult.predicted_class.toLowerCase()].desc}
                  </p>
                  <div className="inline-block font-semibold bg-emerald-200/60 text-emerald-900 px-2.5 py-1 rounded-md">
                    Recommended Bin: {DISPOSAL_TIPS[predictionResult.predicted_class.toLowerCase()].bin}
                  </div>
                </div>
              )}

              {/* 6-Class Probability Distribution */}
              <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-sm space-y-4">
                <div className="flex items-center justify-between">
                  <h4 className="font-bold text-slate-900 text-sm">6-Class Probability Distribution</h4>
                  <span className="text-xs text-slate-400">Sum = 100%</span>
                </div>

                <div className="space-y-2.5">
                  {Object.entries(predictionResult.probabilities)
                    .sort(([, a], [, b]) => b - a)
                    .map(([clsName, prob]) => (
                      <ProbabilityBar
                        key={clsName}
                        classNameString={clsName}
                        probability={prob}
                        isTopClass={clsName.toLowerCase() === predictionResult.predicted_class.toLowerCase()}
                      />
                    ))}
                </div>
              </div>
            </div>
          ) : (
            /* Idle Placeholder State */
            <div className="bg-white rounded-2xl p-12 border border-slate-200/80 shadow-sm text-center flex flex-col items-center justify-center min-h-[380px] space-y-4">
              <div className="w-16 h-16 rounded-full bg-slate-100 flex items-center justify-center text-slate-400">
                <Eye className="w-8 h-8" />
              </div>
              <div className="max-w-sm">
                <h4 className="font-bold text-slate-800 text-base">Awaiting Image Input</h4>
                <p className="text-xs text-slate-400 mt-1 leading-relaxed">
                  Select or drag a waste photo on the left panel and click &quot;Run Deep Learning Classification&quot; to inspect class probabilities and Grad-CAM activations.
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
