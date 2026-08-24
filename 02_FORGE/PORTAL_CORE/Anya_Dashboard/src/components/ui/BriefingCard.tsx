import React from 'react';
import { LucideIcon } from 'lucide-react';

interface BriefingCardProps {
    title: string;
    value: string | number;
    trend?: string;
    trendType?: 'positive' | 'negative' | 'neutral';
    icon: LucideIcon;
    description?: string;
    color?: string;
}

export default function BriefingCard({
    title,
    value,
    trend,
    trendType = 'neutral',
    icon: Icon,
    description,
    color = '#d4af37' // Default Phoenix Gold
}: BriefingCardProps) {
    return (
        <div className="bg-slate-900/40 border border-slate-800 rounded-2xl p-4 font-mono shadow-lg relative overflow-hidden group hover:border-slate-700 transition-all">
            <div className="absolute top-0 right-0 p-3 opacity-10 group-hover:opacity-20 transition-opacity">
                <Icon size={40} style={{ color }} />
            </div>

            <div className="flex items-center gap-2 mb-3">
                <div className="p-1.5 rounded-lg bg-slate-800/50">
                    <Icon size={14} style={{ color }} />
                </div>
                <span className="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em]">{title}</span>
            </div>

            <div className="flex items-baseline gap-2 mb-1">
                <span className="text-2xl font-bold text-white tracking-tight">{value}</span>
                {trend && (
                    <span className={`text-[10px] font-bold ${
                        trendType === 'positive' ? 'text-emerald-500' :
                        trendType === 'negative' ? 'text-red-500' : 'text-slate-500'
                    }`}>
                        {trend}
                    </span>
                )}
            </div>

            {description && (
                <p className="text-[9px] text-slate-600 leading-tight uppercase tracking-tighter">
                    {description}
                </p>
            )}

            {/* Subtle bottom progress or accent */}
            <div className="absolute bottom-0 left-0 h-0.5 w-full bg-slate-800">
                <div
                    className="h-full transition-all duration-1000"
                    style={{ backgroundColor: color, width: '40%' }}
                />
            </div>
        </div>
    );
}
