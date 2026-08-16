import React, { useMemo, useState } from 'react';
import { useParams } from 'react-router-dom';
import { KeyRound, ShieldCheck } from 'lucide-react';

interface ValidationResult {
  valid: boolean;
  reason?: string;
  session_id?: string;
  expires_utc?: string;
  permissions?: string[];
}

function fmtDate(value?: string) {
  if (!value) return 'unknown';
  const date = new Date(value);
  return Number.isNaN(date.valueOf()) ? 'unknown' : date.toLocaleString();
}

export default function SupportPortal() {
  const { sessionId = '' } = useParams();
  const [token, setToken] = useState('');
  const [result, setResult] = useState<ValidationResult | null>(null);
  const [loading, setLoading] = useState(false);
  const active = Boolean(result?.valid);

  const displaySession = useMemo(() => sessionId.replace(/^support_/, 'support_'), [sessionId]);

  async function validate() {
    setLoading(true);
    try {
      const response = await fetch('/api/camelot-os/support/validate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId, token }),
      });
      setResult(await response.json());
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="grid min-h-full place-items-center bg-[#050208] p-6 text-slate-100">
      <section className="w-full max-w-xl rounded-lg border border-slate-800 bg-slate-900/70 p-6 shadow-2xl shadow-black/40">
        <div className="flex items-center gap-3">
          <div className="grid h-11 w-11 place-items-center rounded-lg border border-amber-500/30 bg-amber-950/30">
            <KeyRound className="h-5 w-5 text-amber-300" />
          </div>
          <div>
            <h1 className="text-xl font-black">Break-Glass Support</h1>
            <p className="mt-1 font-mono text-xs text-slate-500">{displaySession}</p>
          </div>
        </div>

        <div className="mt-6 space-y-3">
          <label
            className="block text-xs font-bold uppercase tracking-widest text-slate-500"
            htmlFor="support-token"
          >
            Temporary token
          </label>
          <input
            id="support-token"
            value={token}
            onChange={(event) => setToken(event.target.value)}
            className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 font-mono text-sm text-slate-100 outline-none focus:border-amber-400"
            placeholder="Paste support token"
          />
          <button
            onClick={() => void validate()}
            disabled={!token || loading}
            className="w-full rounded-lg border border-amber-500/30 bg-amber-950/30 px-4 py-2 text-sm font-bold text-amber-100 hover:bg-amber-900/30 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {loading ? 'Validating' : 'Unlock Support Session'}
          </button>
        </div>

        {result && (
          <div
            className={`mt-5 rounded-lg border p-4 ${active ? 'border-emerald-500/30 bg-emerald-950/20' : 'border-red-500/30 bg-red-950/20'}`}
          >
            <div className="flex items-center gap-2">
              <ShieldCheck className={`h-4 w-4 ${active ? 'text-emerald-300' : 'text-red-300'}`} />
              <p className={`text-sm font-black ${active ? 'text-emerald-200' : 'text-red-200'}`}>
                {active ? 'Support session unlocked' : 'Support session blocked'}
              </p>
            </div>
            {active ? (
              <div className="mt-3 space-y-2 text-xs text-slate-300">
                <p>Expires: {fmtDate(result.expires_utc)}</p>
                <p>Permissions: {(result.permissions ?? []).join(' / ')}</p>
              </div>
            ) : (
              <p className="mt-3 text-xs text-red-200/80">
                {result.reason ?? 'Token could not be validated.'}
              </p>
            )}
          </div>
        )}
      </section>
    </div>
  );
}
