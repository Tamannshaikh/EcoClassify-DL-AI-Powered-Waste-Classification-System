import React from 'react';

interface ProbabilityBarProps {
  classNameString: string;
  probability: number; // 0.0 - 1.0
  isTopClass?: boolean;
}

const classColorStyles: Record<string, { bar: string; text: string; bg: string }> = {
  biodegradable: { bar: 'bg-lime-500', text: 'text-lime-700', bg: 'bg-lime-50' },
  cardboard: { bar: 'bg-amber-500', text: 'text-amber-700', bg: 'bg-amber-50' },
  e_waste: { bar: 'bg-purple-500', text: 'text-purple-700', bg: 'bg-purple-50' },
  glass: { bar: 'bg-cyan-500', text: 'text-cyan-700', bg: 'bg-cyan-50' },
  metal: { bar: 'bg-slate-500', text: 'text-slate-700', bg: 'bg-slate-50' },
  paper: { bar: 'bg-blue-500', text: 'text-blue-700', bg: 'bg-blue-50' },
  plastic: { bar: 'bg-emerald-500', text: 'text-emerald-700', bg: 'bg-emerald-50' },
  trash: { bar: 'bg-rose-500', text: 'text-rose-700', bg: 'bg-rose-50' },
};

export const ProbabilityBar: React.FC<ProbabilityBarProps> = ({
  classNameString,
  probability,
  isTopClass = false,
}) => {
  const percentage = Math.max(0, Math.min(100, probability * 100));
  const style = classColorStyles[classNameString.toLowerCase()] || {
    bar: 'bg-indigo-500',
    text: 'text-indigo-700',
    bg: 'bg-indigo-50',
  };

  return (
    <div
      className={`p-3 rounded-lg border transition-all ${
        isTopClass
          ? 'border-emerald-500/50 bg-emerald-50/40 shadow-sm ring-1 ring-emerald-500/20'
          : 'border-slate-100 bg-slate-50/50 hover:bg-slate-50'
      }`}
    >
      <div className="flex items-center justify-between text-xs mb-1.5">
        <div className="flex items-center gap-2">
          <span className="font-semibold text-slate-800 capitalize">{classNameString}</span>
          {isTopClass && (
            <span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-emerald-100 text-emerald-800 uppercase tracking-wider">
              Top Match
            </span>
          )}
        </div>
        <span className="font-mono font-bold text-slate-700">{percentage.toFixed(2)}%</span>
      </div>

      {/* Progress Bar Track */}
      <div className="w-full h-2 rounded-full bg-slate-200 overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-500 ease-out ${style.bar}`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
};
