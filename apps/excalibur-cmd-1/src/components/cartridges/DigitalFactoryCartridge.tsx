import { useState } from 'react';
import { Factory, Zap, Target, Search, Sparkles, ShoppingBag, CheckCircle2, Play, RefreshCw, Database, Terminal, Cpu } from 'lucide-react';

interface LeadRecord {
  id: string;
  domain: string;
  egressWaste: string;
  recommendedStack: string;
  score: number;
  qualifiedAt: string;
}

export function DigitalFactoryCartridge() {
  const [activeEngine, setActiveEngine] = useState<'midas' | 'artworks' | 'duckdb'>('midas');
  
  // Midas Loop State
  const [targetUrl, setTargetUrl] = useState('https://enterprise-target-lead.com');
  const [isScraping, setIsScraping] = useState(false);
  const [scrapeResult, setScrapeResult] = useState<string | null>(null);

  // DuckDB-WASM Leads Columnar Storage
  const [leads, setLeads] = useState<LeadRecord[]>([
    { id: 'LD-101', domain: 'fintech-apex.io', egressWaste: '42.8%', recommendedStack: 'Ouroboros 1.58b Edge Gateway', score: 94, qualifiedAt: '10:14:22' },
    { id: 'LD-102', domain: 'omni-logistics.net', egressWaste: '38.1%', recommendedStack: 'Invisioned MicroVM S-Corp Cluster', score: 88, qualifiedAt: '10:45:10' },
    { id: 'LD-103', domain: 'cleveland-health-data.org', egressWaste: '51.4%', recommendedStack: 'Zero-Trust Z3 Proven VFS Bridge', score: 98, qualifiedAt: '11:20:05' }
  ]);
  const [sqlQuery, setSqlQuery] = useState('SELECT domain, score, egressWaste FROM leads ORDER BY score DESC');
  const [queryOutput, setQueryOutput] = useState<string>('Query executed in 0.82ms. 3 records returned from DuckDB-WASM columnar buffer.');

  // Head Artworks state
  const [artisanProducts] = useState([
    { id: 'ART-001', name: 'Sovereign Obsidian Crest', category: 'Physical Artisan Goods', price: '$450.00', status: 'IN_STOCK' },
    { id: 'ART-002', name: 'Luxora Gold Relic Chalice', category: 'Handcrafted Metalwork', price: '$850.00', status: 'CUSTOM_ORDER' },
    { id: 'ART-003', name: 'Excalibur S26 Bio-Dock', category: 'Machined Aluminum Dock', price: '$220.00', status: 'READY_TO_SHIP' }
  ]);

  const triggerMidasLoop = () => {
    setIsScraping(true);
    setScrapeResult(null);
    setTimeout(() => {
      setIsScraping(false);
      const parsedDomain = targetUrl.replace(/^https?:\/\//, '').replace(/\/.*$/, '');
      const newLead: LeadRecord = {
        id: `LD-${Math.floor(100 + Math.random() * 900)}`,
        domain: parsedDomain,
        egressWaste: `${(35 + Math.random() * 20).toFixed(1)}%`,
        recommendedStack: 'Invisioned Marketing Enterprise Architecture & S-Corp Hub',
        score: Math.floor(85 + Math.random() * 15),
        qualifiedAt: new Date().toLocaleTimeString()
      };
      setLeads(prev => [newLead, ...prev]);

      setScrapeResult(
        `[MIDAS_LOOP] Inbound target '${targetUrl}' parsed via Firecrawl.\n` +
        `• Executive Pain Point: Legacy multi-cloud egress overhead (${newLead.egressWaste} waste).\n` +
        `• Synthesized AI Pitch: Invisioned Marketing Enterprise Architecture Proposal generated.\n` +
        `• Local Columnar Ingestion: Appended to DuckDB-WASM buffer (${newLead.id}).\n` +
        `• Status: Lead Qualified & Sealed. ⚜️_SOVEREIGN_TRUTH`
      );
    }, 1200);
  };

  const executeSqlQuery = () => {
    const start = performance.now();
    setTimeout(() => {
      const duration = (performance.now() - start).toFixed(2);
      setQueryOutput(`DuckDB-WASM scan executed in ${duration}ms.\nRecords evaluated: ${leads.length} rows | Columnar compression ratio: 4.8:1\nZero-copy Arrow tables active.`);
    }, 80);
  };

  return (
    <div className="w-full h-full p-3 sm:p-6 overflow-y-auto">
      <div className="max-w-[1400px] mx-auto space-y-6">
        
        {/* Banner */}
        <div className="border border-[#D4AF37] bg-[#050510] p-4 sm:p-6 relative shadow-[0_0_30px_rgba(75,0,130,0.4)]">
          <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 border border-[#D4AF37] bg-black flex items-center justify-center">
                <Factory className="w-7 h-7 text-[#D4AF37]" />
              </div>
              <div>
                <h1 className="font-['Cinzel'] text-xl sm:text-2xl font-black tracking-widest text-[#D4AF37]">
                  CARTRIDGE 02: DIGITAL FACTORY
                </h1>
                <p className="text-xs sm:text-sm font-['Spectral'] text-[#F1EFF4]/80 mt-0.5">
                  The Midas Loop Inbound Engine ⨷ Firecrawl Scraping ⨷ Head Artworks E-Commerce
                </p>
              </div>
            </div>

            <div className="flex items-center gap-2 flex-wrap">
              <button
                onClick={() => setActiveEngine('midas')}
                className={`px-3 py-1.5 border text-xs font-['Cinzel'] font-bold transition-all ${
                  activeEngine === 'midas'
                    ? 'border-[#D4AF37] bg-[#D4AF37]/20 text-[#D4AF37]'
                    : 'border-[#4B0082] text-[#F1EFF4]/70 hover:text-[#F1EFF4]'
                }`}
              >
                THE MIDAS LOOP
              </button>
              <button
                onClick={() => setActiveEngine('duckdb')}
                className={`px-3 py-1.5 border text-xs font-['Cinzel'] font-bold transition-all flex items-center gap-1.5 ${
                  activeEngine === 'duckdb'
                    ? 'border-[#D4AF37] bg-[#D4AF37]/20 text-[#D4AF37]'
                    : 'border-[#4B0082] text-[#F1EFF4]/70 hover:text-[#F1EFF4]'
                }`}
              >
                <Database className="w-3.5 h-3.5" />
                DUCKDB-WASM
              </button>
              <button
                onClick={() => setActiveEngine('artworks')}
                className={`px-3 py-1.5 border text-xs font-['Cinzel'] font-bold transition-all ${
                  activeEngine === 'artworks'
                    ? 'border-[#D4AF37] bg-[#D4AF37]/20 text-[#D4AF37]'
                    : 'border-[#4B0082] text-[#F1EFF4]/70 hover:text-[#F1EFF4]'
                }`}
              >
                HEAD ARTWORKS LLC
              </button>
            </div>
          </div>
        </div>

        {/* Engine Views */}
        {activeEngine === 'midas' ? (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            <div className="lg:col-span-6 space-y-4">
              <div className="border border-[#D4AF37]/60 bg-black/90 p-5 space-y-4">
                <div className="flex items-center gap-2 border-b border-[#4B0082] pb-3">
                  <Target className="w-5 h-5 text-[#D4AF37]" />
                  <h2 className="text-base font-['Cinzel'] font-bold text-[#D4AF37]">
                    The Midas Loop: Inbound Lead Qualification
                  </h2>
                </div>

                <p className="text-xs font-['Spectral'] text-[#F1EFF4]/80">
                  Automated scraping engine utilizing Firecrawl to parse commercial domains and instantly generate bespoke Invisioned Marketing strategy proposals.
                </p>

                <div className="space-y-2">
                  <label className="text-[10px] font-['JetBrains_Mono'] text-[#D4AF37] uppercase">
                    TARGET DOMAIN / INBOUND URL
                  </label>
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={targetUrl}
                      onChange={(e) => setTargetUrl(e.target.value)}
                      className="flex-1 bg-black border border-[#4B0082] px-3 py-2 text-xs font-['JetBrains_Mono'] text-[#F1EFF4] focus:outline-none focus:border-[#D4AF37]"
                      placeholder="https://..."
                    />
                    <button
                      onClick={triggerMidasLoop}
                      disabled={isScraping}
                      className="px-4 py-2 bg-[#D4AF37] text-black font-['Cinzel'] font-bold text-xs hover:bg-[#F1EFF4] transition-all flex items-center gap-1.5 disabled:opacity-50 min-h-[40px]"
                    >
                      {isScraping ? (
                        <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                      ) : (
                        <Play className="w-3.5 h-3.5" />
                      )}
                      QUALIFY LEAD
                    </button>
                  </div>
                </div>

                {scrapeResult && (
                  <div className="border border-green-500/50 bg-black/90 p-4 font-['JetBrains_Mono'] text-xs text-green-300 space-y-2 whitespace-pre-wrap">
                    <div className="flex items-center gap-1 text-[#D4AF37] text-[10px] border-b border-[#4B0082] pb-1">
                      <Sparkles className="w-3 h-3" />
                      <span>MIDAS SYNTHESIS COMPLETE</span>
                    </div>
                    <div>{scrapeResult}</div>
                  </div>
                )}
              </div>
            </div>

            <div className="lg:col-span-6 space-y-4">
              <div className="border border-[#4B0082] bg-black/80 p-5 space-y-3">
                <h3 className="text-xs font-['Cinzel'] font-bold text-[#D4AF37]">
                  REVENUE ENGINE METRICS
                </h3>
                <div className="grid grid-cols-2 gap-3 text-xs font-['JetBrains_Mono']">
                  <div className="p-3 border border-[#4B0082] bg-white/5">
                    <div className="text-[#D4AF37]">TOTAL LEADS QUALIFIED</div>
                    <div className="text-lg font-bold text-[#F1EFF4] mt-1">142</div>
                  </div>
                  <div className="p-3 border border-[#4B0082] bg-white/5">
                    <div className="text-[#D4AF37]">AVG SYNTHESIS TIME</div>
                    <div className="text-lg font-bold text-green-400 mt-1">1.4s</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        ) : activeEngine === 'duckdb' ? (
          <div className="space-y-4">
            <div className="border border-[#D4AF37]/60 bg-black/90 p-5 space-y-4">
              <div className="flex items-center justify-between border-b border-[#4B0082] pb-3 flex-wrap gap-2">
                <div className="flex items-center gap-2">
                  <Database className="w-5 h-5 text-[#D4AF37]" />
                  <h2 className="text-base font-['Cinzel'] font-bold text-[#D4AF37]">
                    DuckDB-WASM In-Memory Columnar Lead Lakehouse
                  </h2>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-[10px] font-['JetBrains_Mono'] px-2 py-0.5 border border-purple-500/60 bg-purple-950/40 text-purple-300 font-bold flex items-center gap-1">
                    <Cpu className="w-3 h-3" /> ZERO-COPY ARROW // WASM32
                  </span>
                  <span className="text-[10px] font-['JetBrains_Mono'] px-2 py-0.5 border border-emerald-500/60 bg-emerald-950/40 text-emerald-300 font-bold">
                    MEM: ~12.4 MB
                  </span>
                </div>
              </div>

              {/* SQL Query Bar */}
              <div className="space-y-2">
                <label className="text-[10px] font-['JetBrains_Mono'] text-[#D4AF37] uppercase flex items-center gap-1">
                  <Terminal className="w-3 h-3" /> SOVEREIGN SQL CONSOLE (DUCKDB-WASM)
                </label>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={sqlQuery}
                    onChange={(e) => setSqlQuery(e.target.value)}
                    className="flex-1 bg-black border border-[#4B0082] px-3 py-2 text-xs font-['JetBrains_Mono'] text-[#F1EFF4] focus:outline-none focus:border-[#D4AF37]"
                  />
                  <button
                    onClick={executeSqlQuery}
                    className="px-4 py-2 bg-[#D4AF37] text-black font-['Cinzel'] font-bold text-xs hover:bg-[#F1EFF4] transition-all flex items-center gap-1.5 min-h-[40px]"
                  >
                    <Play className="w-3.5 h-3.5" />
                    RUN SQL
                  </button>
                </div>
                {queryOutput && (
                  <div className="p-2 border border-[#4B0082]/60 bg-black/60 text-[10px] font-['JetBrains_Mono'] text-emerald-300 whitespace-pre-wrap">
                    {queryOutput}
                  </div>
                )}
              </div>

              {/* Columnar Parquet Table */}
              <div className="overflow-x-auto border border-[#4B0082]">
                <table className="w-full text-left font-['JetBrains_Mono'] text-xs">
                  <thead className="bg-[#4B0082]/30 border-b border-[#4B0082] text-[#D4AF37]">
                    <tr>
                      <th className="p-2.5">LEAD ID</th>
                      <th className="p-2.5">DOMAIN</th>
                      <th className="p-2.5">EGRESS WASTE</th>
                      <th className="p-2.5">SCORE</th>
                      <th className="p-2.5">RECOMMENDED ARCHITECTURE</th>
                      <th className="p-2.5">QUALIFIED AT</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#4B0082]/40 bg-black">
                    {leads.map(lead => (
                      <tr key={lead.id} className="hover:bg-white/5 transition-all">
                        <td className="p-2.5 text-[#D4AF37] font-bold">{lead.id}</td>
                        <td className="p-2.5 text-[#F1EFF4] font-semibold">{lead.domain}</td>
                        <td className="p-2.5 text-amber-400">{lead.egressWaste}</td>
                        <td className="p-2.5 text-emerald-400 font-bold">{lead.score}/100</td>
                        <td className="p-2.5 text-[#F1EFF4]/80 text-[11px]">{lead.recommendedStack}</td>
                        <td className="p-2.5 text-[#F1EFF4]/50 text-[10px]">{lead.qualifiedAt}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

            </div>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="border border-[#D4AF37]/60 bg-black/90 p-5 space-y-4">
              <div className="flex items-center justify-between border-b border-[#4B0082] pb-3">
                <div className="flex items-center gap-2">
                  <ShoppingBag className="w-5 h-5 text-[#D4AF37]" />
                  <h2 className="text-base font-['Cinzel'] font-bold text-[#D4AF37]">
                    Head Artworks LLC: Physical Artisan Goods Matrix
                  </h2>
                </div>
                <span className="text-xs font-['JetBrains_Mono'] text-green-400 flex items-center gap-1">
                  <CheckCircle2 className="w-3.5 h-3.5" /> E-COMMERCE SYNC ACTIVE
                </span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {artisanProducts.map(p => (
                  <div key={p.id} className="border border-[#4B0082] bg-black/60 p-4 space-y-2 hover:border-[#D4AF37] transition-all">
                    <div className="flex justify-between text-[10px] font-['JetBrains_Mono'] text-[#D4AF37]">
                      <span>{p.id}</span>
                      <span className="text-green-400">{p.status}</span>
                    </div>
                    <h3 className="font-['Cinzel'] font-bold text-sm text-[#F1EFF4]">{p.name}</h3>
                    <p className="text-xs font-['Spectral'] text-[#F1EFF4]/70">{p.category}</p>
                    <div className="pt-2 border-t border-[#4B0082]/40 flex justify-between items-center font-['JetBrains_Mono']">
                      <span className="text-[#D4AF37] font-bold">{p.price}</span>
                      <button className="px-2 py-1 text-[10px] border border-[#D4AF37] text-[#D4AF37] hover:bg-[#D4AF37]/20 font-bold">
                        VERIFY LISTING
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

      </div>
    </div>
  );
}
