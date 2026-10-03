import React from 'react';
import type { LucideIcon } from 'lucide-react';

interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: LucideIcon;
  trend?: string;
  color?: 'emerald' | 'blue' | 'indigo' | 'amber' | 'teal' | 'purple';
}

const colorMap = {
  emerald: {
    bg: 'bg-emerald-50',
    iconBg: 'bg-emerald-500',
    text: 'text-emerald-700',
    border: 'border-emerald-100',
  },
  blue: {
    bg: 'bg-blue-50',
    iconBg: 'bg-blue-500',
    text: 'text-blue-700',
    border: 'border-blue-100',
  },
  indigo: {
    bg: 'bg-indigo-50',
    iconBg: 'bg-indigo-500',
    text: 'text-indigo-700',
    border: 'border-indigo-100',
  },
  amber: {
    bg: 'bg-amber-50',
    iconBg: 'bg-amber-500',
    text: 'text-amber-700',
    border: 'border-amber-100',
  },
  teal: {
    bg: 'bg-teal-50',
    iconBg: 'bg-teal-500',
    text: 'text-teal-700',
    border: 'border-teal-100',
  },
  purple: {
    bg: 'bg-purple-50',
    iconBg: 'bg-purple-500',
    text: 'text-purple-700',
    border: 'border-purple-100',
  },
};

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  subtitle,
  icon: Icon,
  trend,
  color = 'emerald',
}) => {
  const styles = colorMap[color];

  return (
    <div className={`bg-white rounded-xl p-5 border ${styles.border} shadow-sm hover:shadow-md transition-shadow`}>
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">{title}</span>
        <div className={`w-9 h-9 rounded-lg ${styles.iconBg} flex items-center justify-center text-white shadow-sm`}>
          <Icon className="w-5 h-5" />
        </div>
      </div>
      <div className="mt-3">
        <div className="text-2xl font-bold text-slate-900 tracking-tight">{value}</div>
        {(subtitle || trend) && (
          <div className="mt-1 flex items-center gap-2 text-xs">
            {trend && <span className={`font-semibold ${styles.text}`}>{trend}</span>}
            {subtitle && <span className="text-slate-400">{subtitle}</span>}
          </div>
        )}
      </div>
    </div>
  );
};
