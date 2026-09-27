'use client';

export function TheArmory() {
  const items = Array.from({ length: 8 }, (_, i) => ({
    title: `Asset ${i + 1}`,
    detail: 'Video preview placeholder',
  }));

  return (
    <div className="rounded-2xl border border-zinc-800 bg-white/5 p-4 backdrop-blur">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-white">The Armory</h2>
        <p className="text-xs text-slate-400">8-slot grid</p>
      </div>
      <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
        {items.map((item) => (
          <div
            key={item.title}
            className="rounded-xl border border-zinc-800 bg-black/40 p-4 text-slate-200"
          >
            <div className="mb-2 h-20 rounded-lg bg-gradient-to-br from-purple-500/20 via-slate-800 to-black/60 border border-zinc-800" />
            <p className="text-sm font-semibold text-white">{item.title}</p>
            <p className="text-xs text-slate-400">{item.detail}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
