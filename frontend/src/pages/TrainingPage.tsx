import {
  BrainCircuit,
  CheckCircle2,
  Cpu,
  Layers
} from 'lucide-react';

export const TrainingPage: React.FC = () => {
  return (
    <div className="space-y-8 max-w-6xl mx-auto">
      {/* Header */}
      <div className="border-b border-slate-200 pb-4">
        <h2 className="text-2xl font-bold text-slate-900 tracking-tight">Model Architectures & Training Lab</h2>
        <p className="text-sm text-slate-500 mt-1">
          Comparative empirical study of Baseline Custom CNN vs. MobileNetV2 Transfer Learning on the TrashNet benchmark.
        </p>
      </div>

      {/* Selected Winner Banner */}
      <div className="bg-gradient-to-r from-emerald-900 to-slate-900 rounded-2xl p-6 md:p-8 text-white shadow-md border border-emerald-500/30 flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
        <div className="space-y-2">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-500/20 text-emerald-300 text-xs font-bold border border-emerald-500/30">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" /> Selected Production Architecture
          </div>
          <h3 className="text-2xl font-bold">MobileNetV2 (Transfer Learning + Fine-Tuning)</h3>
          <p className="text-slate-300 text-sm max-w-2xl leading-relaxed">
            Outperformed the baseline Custom CNN across all evaluation dimensions with an impressive <strong>87.07% test accuracy</strong> and <strong>85.14% Macro F1-Score</strong>, demonstrating superior feature extraction on complex recyclable textures.
          </p>
        </div>
        <div className="bg-emerald-950/80 rounded-xl p-4 border border-emerald-500/30 text-center shrink-0 min-w-[170px]">
          <span className="text-[10px] uppercase font-bold text-emerald-300 tracking-wider block">Accuracy Delta</span>
          <span className="text-3xl font-extrabold text-white font-mono mt-1 block">+18.47%</span>
          <span className="text-xs text-emerald-400 font-medium">Over Baseline CNN</span>
        </div>
      </div>

      {/* Side-by-Side Model Architecture Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Baseline CNN Card */}
        <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-9 h-9 rounded-lg bg-slate-100 flex items-center justify-center text-slate-700 font-bold">
                <Layers className="w-5 h-5" />
              </div>
              <div>
                <h4 className="font-bold text-slate-900 text-base">Custom CNN (Baseline)</h4>
                <p className="text-xs text-slate-400">Trained from Scratch</p>
              </div>
            </div>
            <span className="px-2.5 py-1 rounded-md text-xs font-semibold bg-slate-100 text-slate-600">
              Baseline
            </span>
          </div>

          <p className="text-xs text-slate-600 leading-relaxed">
            4-block convolutional architecture (32 &rarr; 64 &rarr; 128 &rarr; 256 filters) with Batch Normalization, MaxPooling2D, Dropout regularization, and a 256-unit dense classification head.
          </p>

          <div className="grid grid-cols-2 gap-3 text-xs pt-2">
            <div className="p-3 rounded-lg bg-slate-50 border border-slate-100">
              <span className="text-slate-400 block">Total Parameters</span>
              <span className="font-mono font-bold text-slate-800 text-sm">259,526</span>
            </div>
            <div className="p-3 rounded-lg bg-slate-50 border border-slate-100">
              <span className="text-slate-400 block">Test Accuracy</span>
              <span className="font-mono font-bold text-slate-800 text-sm">68.60%</span>
            </div>
            <div className="p-3 rounded-lg bg-slate-50 border border-slate-100">
              <span className="text-slate-400 block">Macro F1</span>
              <span className="font-mono font-bold text-slate-800 text-sm">65.61%</span>
            </div>
            <div className="p-3 rounded-lg bg-slate-50 border border-slate-100">
              <span className="text-slate-400 block">Weighted F1</span>
              <span className="font-mono font-bold text-slate-800 text-sm">68.94%</span>
            </div>
          </div>

          <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-500">
            <span>Training Time: ~25.91 min</span>
            <span>Inference: ~42.1 ms</span>
          </div>
        </div>

        {/* MobileNetV2 Card */}
        <div className="bg-white rounded-2xl p-6 border-2 border-emerald-500/40 shadow-sm space-y-4 ring-1 ring-emerald-500/20">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-9 h-9 rounded-lg bg-emerald-100 flex items-center justify-center text-emerald-700 font-bold">
                <Cpu className="w-5 h-5" />
              </div>
              <div>
                <h4 className="font-bold text-slate-900 text-base">MobileNetV2 (Transfer Learning)</h4>
                <p className="text-xs text-emerald-600 font-semibold">ImageNet Pretrained Weights</p>
              </div>
            </div>
            <span className="px-2.5 py-1 rounded-md text-xs font-bold bg-emerald-100 text-emerald-800">
              Top Performer
            </span>
          </div>

          <p className="text-xs text-slate-600 leading-relaxed">
            Inverted residual bottleneck backbone leveraging pre-trained ImageNet feature representations, GlobalAveragePooling2D, Dropout (0.3 & 0.2), Dense (128 units), and fine-tuned top layers.
          </p>

          <div className="grid grid-cols-2 gap-3 text-xs pt-2">
            <div className="p-3 rounded-lg bg-emerald-50/50 border border-emerald-100">
              <span className="text-emerald-700 block font-medium">Total Parameters</span>
              <span className="font-mono font-bold text-emerald-950 text-sm">2,422,726</span>
            </div>
            <div className="p-3 rounded-lg bg-emerald-50/50 border border-emerald-100">
              <span className="text-emerald-700 block font-medium">Test Accuracy</span>
              <span className="font-mono font-bold text-emerald-950 text-sm">87.07%</span>
            </div>
            <div className="p-3 rounded-lg bg-emerald-50/50 border border-emerald-100">
              <span className="text-emerald-700 block font-medium">Macro F1</span>
              <span className="font-mono font-bold text-emerald-950 text-sm">85.14%</span>
            </div>
            <div className="p-3 rounded-lg bg-emerald-50/50 border border-emerald-100">
              <span className="text-emerald-700 block font-medium">Weighted F1</span>
              <span className="font-mono font-bold text-emerald-950 text-sm">87.00%</span>
            </div>
          </div>

          <div className="pt-2 border-t border-emerald-100/60 flex items-center justify-between text-[11px] text-emerald-800 font-medium">
            <span>Training Time: ~8.36 min (3.1x faster)</span>
            <span>Inference: ~61.15 ms</span>
          </div>
        </div>
      </div>

      {/* Comprehensive Architectural Comparison Table */}
      <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-sm space-y-4">
        <h3 className="font-bold text-slate-900 text-base">Detailed Model Comparison Matrix</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-500 font-semibold uppercase tracking-wider border-y border-slate-200">
              <tr>
                <th className="py-3 px-4">Evaluation Dimension</th>
                <th className="py-3 px-4">Custom CNN (Baseline)</th>
                <th className="py-3 px-4">MobileNetV2 (Selected Final)</th>
                <th className="py-3 px-4">Winner / Delta</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-700">
              <tr className="hover:bg-slate-50/70">
                <td className="py-3 px-4 font-semibold text-slate-900">Pretrained Backbone</td>
                <td className="py-3 px-4">None (Random Init)</td>
                <td className="py-3 px-4 font-bold text-emerald-700">ImageNet Pretrained</td>
                <td className="py-3 px-4 font-semibold text-emerald-600">MobileNetV2</td>
              </tr>
              <tr className="hover:bg-slate-50/70">
                <td className="py-3 px-4 font-semibold text-slate-900">Test Accuracy</td>
                <td className="py-3 px-4 font-mono">68.60%</td>
                <td className="py-3 px-4 font-mono font-bold text-emerald-700">87.07%</td>
                <td className="py-3 px-4 font-semibold text-emerald-600 font-bold">+18.47%</td>
              </tr>
              <tr className="hover:bg-slate-50/70">
                <td className="py-3 px-4 font-semibold text-slate-900">Macro Precision</td>
                <td className="py-3 px-4 font-mono">68.00%</td>
                <td className="py-3 px-4 font-mono font-bold text-emerald-700">86.23%</td>
                <td className="py-3 px-4 font-semibold text-emerald-600">+18.23%</td>
              </tr>
              <tr className="hover:bg-slate-50/70">
                <td className="py-3 px-4 font-semibold text-slate-900">Macro Recall</td>
                <td className="py-3 px-4 font-mono">69.23%</td>
                <td className="py-3 px-4 font-mono font-bold text-emerald-700">84.44%</td>
                <td className="py-3 px-4 font-semibold text-emerald-600">+15.21%</td>
              </tr>
              <tr className="hover:bg-slate-50/70">
                <td className="py-3 px-4 font-semibold text-slate-900">Macro F1-Score</td>
                <td className="py-3 px-4 font-mono">65.61%</td>
                <td className="py-3 px-4 font-mono font-bold text-emerald-700">85.14%</td>
                <td className="py-3 px-4 font-semibold text-emerald-600 font-bold">+19.53%</td>
              </tr>
              <tr className="hover:bg-slate-50/70">
                <td className="py-3 px-4 font-semibold text-slate-900">Weighted F1-Score</td>
                <td className="py-3 px-4 font-mono">68.94%</td>
                <td className="py-3 px-4 font-mono font-bold text-emerald-700">87.00%</td>
                <td className="py-3 px-4 font-semibold text-emerald-600 font-bold">+18.06%</td>
              </tr>
              <tr className="hover:bg-slate-50/70">
                <td className="py-3 px-4 font-semibold text-slate-900">Total Parameters</td>
                <td className="py-3 px-4 font-mono">259,526</td>
                <td className="py-3 px-4 font-mono">2,422,726</td>
                <td className="py-3 px-4 text-slate-500">9.3x parameters</td>
              </tr>
              <tr className="hover:bg-slate-50/70">
                <td className="py-3 px-4 font-semibold text-slate-900">CPU Training Duration</td>
                <td className="py-3 px-4 font-mono">~25.91 min</td>
                <td className="py-3 px-4 font-mono font-bold text-emerald-700">~8.36 min</td>
                <td className="py-3 px-4 font-semibold text-emerald-600">~3.1x Shorter Training Time</td>
              </tr>
              <tr className="hover:bg-slate-50/70">
                <td className="py-3 px-4 font-semibold text-slate-900">Avg CPU Inference Latency</td>
                <td className="py-3 px-4 font-mono">~42.1 ms</td>
                <td className="py-3 px-4 font-mono font-bold">~61.15 ms</td>
                <td className="py-3 px-4 text-slate-500">Both Real-time (&lt;100ms)</td>
              </tr>
              <tr className="hover:bg-slate-50/70">
                <td className="py-3 px-4 font-semibold text-slate-900">Grad-CAM Interpretability</td>
                <td className="py-3 px-4 text-slate-500">Standard conv4</td>
                <td className="py-3 px-4 font-bold text-emerald-700">out_relu (High resolution)</td>
                <td className="py-3 px-4 font-semibold text-emerald-600">MobileNetV2</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* Training Hyperparameters & Pipeline */}
      <div className="bg-slate-900 rounded-2xl p-6 text-white border border-slate-800 shadow-md space-y-4">
        <h3 className="font-bold text-emerald-400 text-sm flex items-center gap-2">
          <BrainCircuit className="w-4 h-4" />
          <span>Training Pipeline Configuration</span>
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 text-xs text-slate-300">
          <div className="p-3 rounded-xl bg-slate-800/80 border border-slate-700/60">
            <span className="text-slate-400 block mb-0.5">Optimizer</span>
            <span className="font-bold text-white text-sm">Adam (lr=1e-3, fine-tune lr=1e-4)</span>
          </div>
          <div className="p-3 rounded-xl bg-slate-800/80 border border-slate-700/60">
            <span className="text-slate-400 block mb-0.5">Loss Function</span>
            <span className="font-bold text-white text-sm">Categorical Crossentropy</span>
          </div>
          <div className="p-3 rounded-xl bg-slate-800/80 border border-slate-700/60">
            <span className="text-slate-400 block mb-0.5">Batch Size</span>
            <span className="font-bold text-white text-sm">32 samples / batch</span>
          </div>
          <div className="p-3 rounded-xl bg-slate-800/80 border border-slate-700/60">
            <span className="text-slate-400 block mb-0.5">Callbacks</span>
            <span className="font-bold text-white text-sm">EarlyStopping + ReduceLROnPlateau</span>
          </div>
        </div>
      </div>
    </div>
  );
};
