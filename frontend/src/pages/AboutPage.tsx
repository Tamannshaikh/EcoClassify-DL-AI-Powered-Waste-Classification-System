import React from 'react';
import {
  Info,
  BookOpen,
  Code2,
  Cpu,
  Layers,
  ShieldCheck,
  Award,
  Globe
} from 'lucide-react';

export const AboutPage: React.FC = () => {
  return (
    <div className="space-y-8 max-w-5xl mx-auto">
      {/* Header */}
      <div className="border-b border-slate-200 pb-4">
        <h2 className="text-2xl font-bold text-slate-900 tracking-tight">About EcoClassify DL</h2>
        <p className="text-sm text-slate-500 mt-1">
          An AI-Powered Waste Classification System built with Deep Learning, Transfer Learning, and Explainability.
        </p>
      </div>

      {/* Project Overview Card */}
      <div className="bg-white rounded-2xl p-6 md:p-8 border border-slate-200/80 shadow-sm space-y-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-emerald-100 flex items-center justify-center text-emerald-700 font-bold">
            <Info className="w-6 h-6" />
          </div>
          <div>
            <h3 className="font-bold text-slate-900 text-lg">System Objective & Scope</h3>
            <p className="text-xs text-slate-500">Autonomous Ecological Waste Recognition</p>
          </div>
        </div>

        <p className="text-sm text-slate-700 leading-relaxed">
          Municipal recycling facilities and automated sorting plants face significant contamination challenges due to manual sorting errors. <strong>EcoClassify DL</strong> demonstrates how state-of-the-art Convolutional Neural Networks (CNNs) and Transfer Learning provide real-time, deterministic, and explainable waste item categorization into eight unified classes: <strong>Biodegradable</strong>, <strong>Cardboard</strong>, <strong>E-Waste</strong>, <strong>Glass</strong>, <strong>Metal</strong>, <strong>Paper</strong>, <strong>Plastic</strong>, and <strong>Trash</strong>.
        </p>
      </div>

      {/* Technology Stack Grid */}
      <div className="space-y-4">
        <h3 className="font-bold text-slate-900 text-base">Full-Stack Deep Learning Architecture</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-sm space-y-2">
            <div className="flex items-center gap-2 text-emerald-700 font-bold text-sm">
              <Cpu className="w-4 h-4" />
              <span>Deep Learning Engine</span>
            </div>
            <p className="text-xs text-slate-600 leading-relaxed">
              TensorFlow 2.x & Keras, MobileNetV2 with inverted residuals, fine-tuned dense classification head, and deterministic 224x224 RGB image normalization.
            </p>
          </div>

          <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-sm space-y-2">
            <div className="flex items-center gap-2 text-teal-700 font-bold text-sm">
              <Layers className="w-4 h-4" />
              <span>Model Explainability</span>
            </div>
            <p className="text-xs text-slate-600 leading-relaxed">
              Gradient-weighted Class Activation Mapping (Grad-CAM) targeting feature gradients from the final <code className="bg-slate-100 px-1 py-0.5 rounded text-[11px]">out_relu</code> layer.
            </p>
          </div>

          <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-sm space-y-2">
            <div className="flex items-center gap-2 text-indigo-700 font-bold text-sm">
              <Code2 className="w-4 h-4" />
              <span>FastAPI Backend</span>
            </div>
            <p className="text-xs text-slate-600 leading-relaxed">
              High-throughput asynchronous REST API, single-instance in-memory model lifecycle caching, and strict image payload validation.
            </p>
          </div>

          <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-sm space-y-2">
            <div className="flex items-center gap-2 text-amber-700 font-bold text-sm">
              <ShieldCheck className="w-4 h-4" />
              <span>SQLite Persistence</span>
            </div>
            <p className="text-xs text-slate-600 leading-relaxed">
              Local embedded SQLite database tracking every inference request, confidence score, full 6-class probability distribution, and audit timestamp.
            </p>
          </div>

          <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-sm space-y-2">
            <div className="flex items-center gap-2 text-blue-700 font-bold text-sm">
              <Globe className="w-4 h-4" />
              <span>React & TypeScript</span>
            </div>
            <p className="text-xs text-slate-600 leading-relaxed">
              Vite-powered React single-page application, Tailwind CSS responsive design system, strict TypeScript interfaces, and Recharts analytics.
            </p>
          </div>

          <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-sm space-y-2">
            <div className="flex items-center gap-2 text-rose-700 font-bold text-sm">
              <Award className="w-4 h-4" />
              <span>Local-First Design</span>
            </div>
            <p className="text-xs text-slate-600 leading-relaxed">
              100% self-contained on Windows workstation. Zero reliance on third-party cloud APIs, paid tokens, or external data transmission.
            </p>
          </div>
        </div>
      </div>

      {/* Dataset Citation & Acknowledgement */}
      <div className="bg-slate-900 rounded-2xl p-6 md:p-8 text-white border border-slate-800 shadow-md space-y-4">
        <div className="flex items-center gap-2.5 text-emerald-400 font-bold text-base">
          <BookOpen className="w-5 h-5" />
          <span>Academic Dataset Citation</span>
        </div>
        <p className="text-xs text-slate-300 leading-relaxed">
          The models in this application were trained and evaluated on the benchmark <strong>TrashNet</strong> dataset, collected and curated by Gary Thung and Mindy Yang at Stanford University for the CS 229 Machine Learning course.
        </p>
        <div className="bg-slate-950/80 rounded-xl p-4 border border-slate-800 font-mono text-xs text-emerald-300 leading-relaxed select-all">
          Thung, G., & Yang, M. (2016). Classification of Trash for Recyclability Status. CS 229 Project Report, Stanford University. Dataset containing 2,527 images across 6 classes: Cardboard, Glass, Metal, Paper, Plastic, Trash.
        </div>
      </div>
    </div>
  );
};
