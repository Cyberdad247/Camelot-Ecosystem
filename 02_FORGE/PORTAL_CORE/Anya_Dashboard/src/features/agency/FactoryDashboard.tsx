import React from 'react';
import { Card } from '@/components/ui/Card';
import { Activity, Target, Factory, FileText } from 'lucide-react';

const productionLines = [1, 2, 3];

export default function FactoryDashboard() {
  return (
    <div className="min-h-screen space-y-6 bg-slate-950 p-6 text-white">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold tracking-tight">Agency Factory Command</h1>
        <span className="rounded-full border border-emerald-400 px-3 py-1 text-xs font-semibold uppercase tracking-widest text-emerald-400">
          STATUS: RADIANT
        </span>
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-4">
        <Card
          className="border-slate-800 bg-slate-900 text-white"
          title="Scouted Leads"
          actions={<Target className="h-4 w-4 text-emerald-400" />}
        >
          <div className="text-2xl font-bold">142</div>
          <p className="text-xs text-slate-500">+12% from yesterday</p>
        </Card>

        <Card
          className="border-slate-800 bg-slate-900 text-white"
          title="In Production"
          actions={<Factory className="h-4 w-4 text-blue-400" />}
        >
          <div className="text-2xl font-bold">8</div>
          <p className="text-xs text-slate-500">3 Audits, 5 Content Packs</p>
        </Card>

        <Card
          className="border-slate-800 bg-slate-900 text-white"
          title="Deliverables"
          actions={<FileText className="h-4 w-4 text-purple-400" />}
        >
          <div className="text-2xl font-bold">42</div>
          <p className="text-xs text-slate-500">Ready for review</p>
        </Card>

        <Card
          className="border-slate-800 bg-slate-900 text-white"
          title="Factory Health"
          actions={<Activity className="h-4 w-4 text-orange-400" />}
        >
          <div className="text-2xl font-bold">98.2%</div>
          <p className="text-xs text-slate-500">Agent uptime: 100%</p>
        </Card>
      </div>

      <Card className="border-slate-800 bg-slate-900 text-white" title="Active Production Line">
        <div className="space-y-4">
          {productionLines.map((line) => (
            <div key={line} className="flex items-center justify-between rounded-lg bg-slate-800 p-4">
              <div className="flex items-center space-x-4">
                <div className="h-2 w-2 animate-pulse rounded-full bg-emerald-500" />
                <div>
                  <p className="font-medium">Client_{line} - SEO Audit</p>
                  <p className="text-xs text-slate-400">Agent: SIR_ORACLE | Progress: 75%</p>
                </div>
              </div>
              <button className="rounded-md px-3 py-2 text-sm text-slate-400 transition hover:bg-slate-700 hover:text-white">
                View Output
              </button>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
