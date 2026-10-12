import React, { useState, useMemo } from 'react';
import { VfsFile } from '../types';
import Markdown from 'react-markdown';
import {
  FileText,
  FileJson,
  Search,
  CheckCircle2,
  Copy,
  Check,
  Shield,
  Layers,
  Sparkles,
  BookOpen,
  FolderGit2,
  Tag,
  ExternalLink,
  Code
} from 'lucide-react';

interface VfsExplorerProps {
  files: VfsFile[];
  selectedFile: VfsFile | null;
  onSelectFile: (file: VfsFile) => void;
  onKineticTrigger: (trigger: string) => void;
}

export const VfsExplorer: React.FC<VfsExplorerProps> = ({
  files,
  selectedFile,
  onSelectFile,
  onKineticTrigger,
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [activeCategory, setActiveCategory] = useState<'all' | 'vfs-core' | 'docs' | 'contracts' | 'golden-receipts'>('vfs-core');
  const [copied, setCopied] = useState(false);
  const [viewRaw, setViewRaw] = useState(false);

  const filteredFiles = useMemo(() => {
    return files.filter(file => {
      const matchesCategory = activeCategory === 'all' || file.category === activeCategory;
      const matchesSearch =
        file.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        file.domain.toLowerCase().includes(searchTerm.toLowerCase()) ||
        file.path.toLowerCase().includes(searchTerm.toLowerCase());
      return matchesCategory && matchesSearch;
    });
  }, [files, activeCategory, searchTerm]);

  // Group files by domain
  const filesByDomain = useMemo(() => {
    const map = new Map<string, VfsFile[]>();
    filteredFiles.forEach(file => {
      const list = map.get(file.domain) || [];
      list.push(file);
      map.set(file.domain, list);
    });
    return map;
  }, [filteredFiles]);

  const handleCopyContent = () => {
    if (!selectedFile) return;
    navigator.clipboard.writeText(selectedFile.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="flex-1 flex flex-col md:flex-row h-full overflow-hidden bg-neutral-950 text-neutral-100">
      {/* VFS Sidebar Directory */}
      <aside className="w-full md:w-80 lg:w-96 bg-neutral-900 border-r border-neutral-800 flex flex-col h-full shrink-0">
        {/* Search & Category Filter */}
        <div className="p-4 border-b border-neutral-800 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-mono font-bold tracking-wider text-amber-400 uppercase flex items-center gap-1.5">
              <Layers className="w-3.5 h-3.5" />
              <span>VFS Topology Index</span>
            </span>
            <span className="text-[11px] font-mono text-neutral-400 bg-neutral-800 px-2 py-0.5 rounded">
              {filteredFiles.length} Nodes
            </span>
          </div>

          <div className="relative">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-neutral-500" />
            <input
              type="text"
              placeholder="Search manifest by name, domain, path..."
              value={searchTerm}
              onChange={e => setSearchTerm(e.target.value)}
              className="w-full pl-9 pr-3 py-2 bg-neutral-950 border border-neutral-800 rounded-lg text-xs font-mono text-neutral-200 placeholder:text-neutral-600 focus:outline-none focus:border-amber-500/60 focus:ring-1 focus:ring-amber-500/30 transition-all"
            />
          </div>

          {/* Category Tabs */}
          <div className="grid grid-cols-4 gap-1 p-1 bg-neutral-950 rounded-lg border border-neutral-800 text-[11px] font-medium">
            <button
              onClick={() => setActiveCategory('vfs-core')}
              className={`py-1.5 px-1 text-center rounded transition-colors ${
                activeCategory === 'vfs-core'
                  ? 'bg-amber-500/20 text-amber-300 font-bold border border-amber-500/40'
                  : 'text-neutral-400 hover:text-neutral-200'
              }`}
            >
              .agent (20)
            </button>
            <button
              onClick={() => setActiveCategory('docs')}
              className={`py-1.5 px-1 text-center rounded transition-colors ${
                activeCategory === 'docs'
                  ? 'bg-neutral-800 text-white font-bold'
                  : 'text-neutral-400 hover:text-neutral-200'
              }`}
            >
              Docs
            </button>
            <button
              onClick={() => setActiveCategory('contracts')}
              className={`py-1.5 px-1 text-center rounded transition-colors ${
                activeCategory === 'contracts'
                  ? 'bg-neutral-800 text-white font-bold'
                  : 'text-neutral-400 hover:text-neutral-200'
              }`}
            >
              Schemas
            </button>
            <button
              onClick={() => setActiveCategory('all')}
              className={`py-1.5 px-1 text-center rounded transition-colors ${
                activeCategory === 'all'
                  ? 'bg-neutral-800 text-white font-bold'
                  : 'text-neutral-400 hover:text-neutral-200'
              }`}
            >
              All
            </button>
          </div>
        </div>

        {/* Tree List */}
        <div className="flex-1 overflow-y-auto p-3 space-y-4 font-mono text-xs select-none">
          {Array.from(filesByDomain.entries()).map(([domain, domainFiles]) => (
            <div key={domain} className="space-y-1">
              <div className="px-2 py-1 flex items-center justify-between text-[11px] font-semibold tracking-wider text-neutral-400 uppercase bg-neutral-950/40 rounded border border-neutral-800/40">
                <span className="truncate">{domain.replace(/_/g, ' ')}</span>
                <span className="text-[10px] text-neutral-500">({domainFiles.length})</span>
              </div>

              <div className="space-y-0.5 pl-1">
                {domainFiles.map(file => {
                  const isSelected = selectedFile?.path === file.path;
                  const isSovereign = file.category === 'vfs-core';

                  return (
                    <button
                      key={file.path}
                      onClick={() => onSelectFile(file)}
                      className={`w-full text-left px-2.5 py-2 rounded-lg flex items-center justify-between transition-all group ${
                        isSelected
                          ? 'bg-amber-500/20 text-white border border-amber-500/40 shadow-sm'
                          : 'hover:bg-neutral-800/80 text-neutral-300 border border-transparent'
                      }`}
                    >
                      <div className="flex items-center space-x-2.5 min-w-0 truncate">
                        {isSovereign ? (
                          <Sparkles className={`w-3.5 h-3.5 shrink-0 ${isSelected ? 'text-amber-400' : 'text-amber-500/70'}`} />
                        ) : file.isMarkdown ? (
                          <FileText className={`w-3.5 h-3.5 shrink-0 ${isSelected ? 'text-sky-400' : 'text-neutral-500'}`} />
                        ) : (
                          <FileJson className={`w-3.5 h-3.5 shrink-0 ${isSelected ? 'text-emerald-400' : 'text-neutral-500'}`} />
                        )}
                        <span className="truncate font-sans text-xs font-medium">{file.name}</span>
                      </div>

                      {isSovereign && (
                        <span className="text-[9px] px-1.5 py-0.5 rounded bg-amber-950/80 text-amber-400 border border-amber-800/60 shrink-0 font-mono">
                          VFS
                        </span>
                      )}
                    </button>
                  );
                })}
              </div>
            </div>
          ))}

          {filteredFiles.length === 0 && (
            <div className="p-8 text-center text-neutral-500 text-xs">
              No files match your search criteria.
            </div>
          )}
        </div>
      </aside>

      {/* Main Content Workspace Viewer */}
      <main className="flex-1 flex flex-col h-full overflow-hidden bg-neutral-950">
        {selectedFile ? (
          <>
            {/* Header Details */}
            <div className="px-6 py-4 bg-neutral-900/90 border-b border-neutral-800 flex flex-wrap items-center justify-between gap-4">
              <div className="space-y-1">
                <div className="flex items-center space-x-3">
                  <h2 className="text-xl font-bold tracking-tight text-white font-sans flex items-center gap-2">
                    {selectedFile.name}
                  </h2>
                  {selectedFile.category === 'vfs-core' && (
                    <span className="px-2 py-0.5 bg-amber-500/20 text-amber-300 text-xs font-mono font-semibold rounded border border-amber-500/40">
                      Sovereign VFS Crystal
                    </span>
                  )}
                </div>
                <div className="flex flex-wrap items-center gap-2 text-xs font-mono text-neutral-400">
                  <span className="text-neutral-500">Path:</span>
                  <span className="text-neutral-300">{selectedFile.path}</span>
                  <span>•</span>
                  <span className="text-neutral-500">Domain:</span>
                  <span className="text-amber-400/90">{selectedFile.domain}</span>
                </div>
              </div>

              {/* View Toggles & Actions */}
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => setViewRaw(!viewRaw)}
                  className={`px-3 py-1.5 text-xs font-mono rounded-lg border transition-all flex items-center space-x-1.5 ${
                    viewRaw
                      ? 'bg-neutral-800 text-white border-neutral-700'
                      : 'bg-neutral-950 text-neutral-400 border-neutral-800 hover:text-neutral-200'
                  }`}
                >
                  <Code className="w-3.5 h-3.5" />
                  <span>{viewRaw ? 'Rendered View' : 'Raw Text'}</span>
                </button>

                <button
                  onClick={handleCopyContent}
                  className="px-3 py-1.5 bg-neutral-950 hover:bg-neutral-800 text-neutral-300 hover:text-white border border-neutral-800 rounded-lg text-xs font-mono transition-all flex items-center space-x-1.5"
                >
                  {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                  <span>{copied ? 'Copied' : 'Copy'}</span>
                </button>
              </div>
            </div>

            {/* Document Body */}
            <div className="flex-1 overflow-y-auto p-6 md:p-8 space-y-6">
              <div className="max-w-4xl mx-auto space-y-6">
                {/* Meta Attributes Panel */}
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 font-mono text-xs">
                  <div className="bg-neutral-900 p-3.5 rounded-xl border border-neutral-800">
                    <span className="text-[10px] text-neutral-500 uppercase tracking-wider block mb-1">Integrity Status</span>
                    <div className="flex items-center space-x-1.5 text-emerald-400 font-semibold">
                      <CheckCircle2 className="w-4 h-4" />
                      <span>ISOMORPHIC_SYNCED</span>
                    </div>
                  </div>
                  <div className="bg-neutral-900 p-3.5 rounded-xl border border-neutral-800">
                    <span className="text-[10px] text-neutral-500 uppercase tracking-wider block mb-1">Target Engine</span>
                    <span className="text-neutral-200 font-medium">DGM-H / QuickJS MicroVM</span>
                  </div>
                  <div className="bg-neutral-900 p-3.5 rounded-xl border border-neutral-800">
                    <span className="text-[10px] text-neutral-500 uppercase tracking-wider block mb-1">Security Seal</span>
                    <span className="text-amber-400 font-semibold">ANYA_LAST_LAW_VALIDATED</span>
                  </div>
                </div>

                {/* Content Render Pane */}
                {viewRaw ? (
                  <div className="bg-neutral-900 rounded-xl border border-neutral-800 p-5 overflow-x-auto shadow-2xl">
                    <pre className="text-xs font-mono text-neutral-300 whitespace-pre-wrap leading-relaxed">
                      {selectedFile.content}
                    </pre>
                  </div>
                ) : selectedFile.isMarkdown ? (
                  <div className="bg-neutral-900 rounded-xl border border-neutral-800 p-6 md:p-8 shadow-xl">
                    <div className="prose prose-invert prose-neutral max-w-none prose-headings:font-sans prose-headings:tracking-tight prose-a:text-amber-400 prose-code:text-amber-300 prose-code:font-mono prose-pre:bg-neutral-950 prose-pre:border prose-pre:border-neutral-800">
                      <Markdown>{selectedFile.content}</Markdown>
                    </div>
                  </div>
                ) : (
                  <div className="space-y-6">
                    {selectedFile.parsed && (
                      <div className="bg-neutral-900 rounded-xl border border-neutral-800 overflow-hidden shadow-xl">
                        <div className="px-5 py-3 border-b border-neutral-800 bg-neutral-950/60 flex items-center justify-between">
                          <span className="text-xs font-mono font-semibold text-neutral-400 uppercase tracking-wider">
                            JSON Schema Inspector
                          </span>
                          <span className="text-xs font-mono text-emerald-400">
                            {selectedFile.parsed.type || 'Object Contract'}
                          </span>
                        </div>
                        <div className="p-5">
                          {selectedFile.parsed.properties ? (
                            <div className="space-y-3">
                              <h4 className="text-xs font-mono text-neutral-400 uppercase tracking-wider">Declared Properties:</h4>
                              <div className="divide-y divide-neutral-800/80">
                                {Object.entries(selectedFile.parsed.properties).map(([key, val]: [string, any]) => (
                                  <div key={key} className="py-2.5 flex items-start justify-between">
                                    <div>
                                      <div className="flex items-center space-x-2">
                                        <span className="text-xs font-mono font-bold text-white">{key}</span>
                                        {selectedFile.parsed.required?.includes(key) && (
                                          <span className="text-[9px] bg-red-950 text-red-400 border border-red-800/60 px-1.5 py-0.5 rounded font-mono font-bold">
                                            REQUIRED
                                          </span>
                                        )}
                                      </div>
                                      <p className="text-xs text-neutral-400 mt-1">{val.description || 'No description specified.'}</p>
                                    </div>
                                    <span className="text-[11px] font-mono text-amber-400 bg-neutral-950 px-2 py-0.5 rounded border border-neutral-800 shrink-0">
                                      {val.type || 'any'}
                                    </span>
                                  </div>
                                ))}
                              </div>
                            </div>
                          ) : (
                            <p className="text-xs font-mono text-neutral-400">Standard JSON structure with no sub-properties declared.</p>
                          )}
                        </div>
                      </div>
                    )}

                    <div className="bg-neutral-900 rounded-xl border border-neutral-800 p-5 overflow-x-auto shadow-2xl">
                      <div className="text-xs font-mono text-neutral-400 mb-2 uppercase tracking-wider">Raw JSON Contract:</div>
                      <pre className="text-xs font-mono text-amber-300/90 whitespace-pre-wrap leading-relaxed">
                        {JSON.stringify(selectedFile.parsed || selectedFile.content, null, 2)}
                      </pre>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </>
        ) : (
          <div className="flex-1 flex flex-col items-center justify-center p-8 text-neutral-500 font-mono text-center">
            <Shield className="w-16 h-16 mb-4 text-neutral-800" />
            <h3 className="text-lg font-bold text-neutral-300 font-sans">Select a Sovereign Node</h3>
            <p className="text-xs text-neutral-500 mt-1 max-w-sm">
              Explore the 20 sovereign VFS crystals, architectural blueprints, or JSON contract schemas in the matrix.
            </p>
          </div>
        )}
      </main>
    </div>
  );
};
