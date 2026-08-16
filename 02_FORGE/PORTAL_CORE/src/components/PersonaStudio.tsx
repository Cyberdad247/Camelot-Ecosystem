import React, { useState, useEffect } from 'react';

interface PersonaTAL {
  root: { id: string; mandate: string; alignment?: string };
  branch: { tone: string; symbols: string; lexicon?: string };
  leaf: string[];
}

const PersonaStudio: React.FC = () => {
  const [experts, setExperts] = useState<string[]>([]);
  const [selectedExpert, setSelectedExpert] = useState<string | null>(null);
  const [manifest, setManifest] = useState<PersonaTAL | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [message, setMessage] = useState('');

  const API_URL = 'http://localhost:18788';

  useEffect(() => {
    fetchExperts();
  }, []);

  const fetchExperts = async () => {
    const res = await fetch(`${API_URL}/vault/personas`);
    const data = await res.json();
    setExperts(data.library_experts);
  };

  const loadPersona = async (name: string) => {
    const res = await fetch(`${API_URL}/vault/persona/${name}`);
    if (res.ok) {
      const data = await res.json();
      setManifest(data);
      setSelectedExpert(name);
      setMessage('');
    }
  };

  const handleSave = async () => {
    if (!manifest) return;
    setIsSaving(true);
    try {
      const res = await fetch(`${API_URL}/vault/persona/save`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(manifest),
      });
      if (res.ok) {
        setMessage('✅ PERSONA_COMMITTED_TO_VAULT');
        setTimeout(() => setMessage(''), 3000);
      }
    } catch {
      setMessage('❌ SAVE_FAILURE');
    } finally {
      setIsSaving(false);
    }
  };

  const updateLeaf = (index: number, value: string) => {
    if (!manifest) return;
    const newLeaf = [...manifest.leaf];
    newLeaf[index] = value;
    setManifest({ ...manifest, leaf: newLeaf });
  };

  return (
    <div className="flex flex-col h-full bg-black border border-purple-900 rounded-lg overflow-hidden shadow-[0_0_20px_rgba(50,0,50,0.5)]">
      <div className="bg-purple-900/20 px-4 py-2 border-b border-purple-900 flex justify-between items-center">
        <h2 className="text-xs font-black tracking-widest text-purple-400 uppercase">
          🧙‍♂️ Merlin Persona Studio
        </h2>
        <div className="text-[10px] text-purple-700 font-mono">v2.0_TAL_EDITOR</div>
      </div>

      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar: Expert List */}
        <div className="w-48 border-r border-purple-900 overflow-y-auto p-2 space-y-1">
          <span className="text-[9px] text-purple-800 uppercase px-2">Library</span>
          {experts.map((e) => (
            <button
              key={e}
              onClick={() => loadPersona(e.replace(' ', '_'))}
              className={`w-full text-left px-2 py-1 text-[10px] uppercase truncate ${selectedExpert === e.replace(' ', '_') ? 'bg-purple-900/50 text-purple-300 border-l-2 border-purple-400' : 'text-purple-700 hover:text-purple-500'}`}
            >
              {e}
            </button>
          ))}
        </div>

        {/* Main: Editor */}
        <div className="flex-1 p-6 overflow-y-auto">
          {manifest ? (
            <div className="space-y-6">
              {/* ROOT SECTION */}
              <section className="space-y-3">
                <div className="flex items-center gap-2">
                  <div className="h-[1px] flex-1 bg-purple-900" />
                  <span className="text-[10px] text-purple-400 font-bold uppercase tracking-widest">
                    ROOT_IDENTITY
                  </span>
                  <div className="h-[1px] flex-1 bg-purple-900" />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-1">
                    <label className="text-[9px] text-purple-900 uppercase">ID</label>
                    <input
                      value={manifest.root.id}
                      onChange={(e) =>
                        setManifest({ ...manifest, root: { ...manifest.root, id: e.target.value } })
                      }
                      className="w-full bg-black border border-purple-900 p-2 text-xs text-purple-300 focus:outline-none focus:border-purple-400"
                    />
                  </div>
                  <div className="space-y-1">
                    <label className="text-[9px] text-purple-900 uppercase">Mandate</label>
                    <input
                      value={manifest.root.mandate}
                      onChange={(e) =>
                        setManifest({
                          ...manifest,
                          root: { ...manifest.root, mandate: e.target.value },
                        })
                      }
                      className="w-full bg-black border border-purple-900 p-2 text-xs text-purple-300 focus:outline-none focus:border-purple-400"
                    />
                  </div>
                </div>
              </section>

              {/* BRANCH SECTION */}
              <section className="space-y-3">
                <div className="flex items-center gap-2">
                  <div className="h-[1px] flex-1 bg-purple-900" />
                  <span className="text-[10px] text-purple-400 font-bold uppercase tracking-widest">
                    COGNITIVE_BRANCH
                  </span>
                  <div className="h-[1px] flex-1 bg-purple-900" />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-1">
                    <label className="text-[9px] text-purple-900 uppercase">Tone</label>
                    <input
                      value={manifest.branch.tone}
                      onChange={(e) =>
                        setManifest({
                          ...manifest,
                          branch: { ...manifest.branch, tone: e.target.value },
                        })
                      }
                      className="w-full bg-black border border-purple-900 p-2 text-xs text-purple-300 focus:outline-none focus:border-purple-400"
                    />
                  </div>
                  <div className="space-y-1">
                    <label className="text-[9px] text-purple-900 uppercase">Symbol</label>
                    <input
                      value={manifest.branch.symbols}
                      onChange={(e) =>
                        setManifest({
                          ...manifest,
                          branch: { ...manifest.branch, symbols: e.target.value },
                        })
                      }
                      className="w-full bg-black border border-purple-900 p-2 text-center text-xl"
                    />
                  </div>
                </div>
              </section>

              {/* LEAF SECTION */}
              <section className="space-y-3">
                <div className="flex items-center gap-2">
                  <div className="h-[1px] flex-1 bg-purple-900" />
                  <span className="text-[10px] text-purple-400 font-bold uppercase tracking-widest">
                    LEAF_STRATEGIES
                  </span>
                  <div className="h-[1px] flex-1 bg-purple-900" />
                </div>
                <div className="space-y-2">
                  {manifest.leaf.map((l, i) => (
                    <div key={i} className="flex gap-2">
                      <span className="text-[9px] text-purple-900 flex items-center">{i + 1}.</span>
                      <input
                        value={l}
                        onChange={(e) => updateLeaf(i, e.target.value)}
                        className="flex-1 bg-black border-b border-purple-900/50 p-1 text-xs text-purple-500 focus:outline-none focus:border-purple-400"
                      />
                    </div>
                  ))}
                </div>
              </section>

              <div className="pt-4 flex items-center justify-between">
                <span
                  className={`text-[10px] font-bold ${message.includes('✅') ? 'text-green-500' : 'text-purple-700'}`}
                >
                  {message}
                </span>
                <button
                  onClick={handleSave}
                  disabled={isSaving}
                  className="px-6 py-2 bg-purple-900 text-black text-xs font-black uppercase tracking-tighter hover:bg-purple-400 transition-all disabled:opacity-50"
                >
                  {isSaving ? 'COMMITTING...' : 'FORGE_CHANGES'}
                </button>
              </div>
            </div>
          ) : (
            <div className="h-full flex flex-col items-center justify-center text-purple-900 space-y-4">
              <span className="text-6xl animate-pulse">🧙‍♂️</span>
              <p className="text-[10px] uppercase tracking-widest">
                Select an expert to begin synthesis
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default PersonaStudio;
