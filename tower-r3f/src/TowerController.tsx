import { useEffect, useMemo, useRef, useState } from 'react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { TowerScene, ScrollState } from './TowerScene';
import { FLOORS, PhaseId, phaseAt } from './tower-data';

gsap.registerPlugin(ScrollTrigger);

/**
 * TowerController — single owner of scroll orchestration.
 * ScrollTrigger writes into a mutable ref (read at 60fps by the scene, zero
 * re-renders); React state updates only on floor or phase boundaries, which
 * drives the overlay and fires phase transitions.
 */
export function TowerController() {
  const scroll = useRef<ScrollState>({ progress: 0, activeFloor: 0 });
  const [activeFloor, setActiveFloor] = useState(0);
  const [phase, setPhase] = useState<PhaseId>('arrival');
  const [descent, setDescent] = useState(0);
  const cardRef = useRef<HTMLElement>(null);
  const reducedMotion = useMemo(() => matchMedia('(prefers-reduced-motion: reduce)').matches, []);

  useEffect(() => {
    const trigger = ScrollTrigger.create({
      trigger: '#track',
      start: 'top top',
      end: 'bottom bottom',
      scrub: reducedMotion ? false : 0.6,
      onUpdate: self => {
        const p = self.progress;
        scroll.current.progress = p;
        const idx = Math.min(FLOORS.length - 1, Math.round(p * (FLOORS.length - 1)));
        scroll.current.activeFloor = idx;
        setActiveFloor(prev => (prev === idx ? prev : idx));
        setPhase(prev => {
          const next = phaseAt(p);
          return prev === next ? prev : next;
        });
        setDescent(Math.round(p * 100));
      }
    });
    return () => trigger.kill();
  }, [reducedMotion]);

  /** Phase transition: announce the new phase on the card. */
  useEffect(() => {
    if (reducedMotion || !cardRef.current) return;
    gsap.fromTo(cardRef.current, { opacity: 0, y: 12 }, { opacity: 1, y: 0, duration: 0.5, ease: 'power2.out' });
  }, [phase, activeFloor, reducedMotion]);

  const jumpTo = (i: number) => {
    const max = document.body.scrollHeight - innerHeight;
    window.scrollTo({ top: (i / (FLOORS.length - 1)) * max, behavior: 'smooth' });
  };

  const floor = FLOORS[activeFloor];

  return (
    <div data-phase={phase}>
      <div id="track" style={{ height: `${FLOORS.length * 100}vh` }} />

      <TowerScene scroll={scroll} reducedMotion={reducedMotion} />

      <header className="chrome">
        <span className="mark">BIFROST TOWER</span>
        <span className="realm">CAMELOT-OS · CYBERTRONIA REALM</span>
      </header>

      {phase === 'arrival' && (
        <div className="arrival-title">
          <h1>THE BIFROST TOWER</h1>
          <p>Eight floors of the trust plane. Descend.</p>
        </div>
      )}

      <aside className="floor-card" ref={cardRef} data-hidden={phase === 'arrival' || undefined}>
        <span className="numeral">{floor.numeral}</span>
        <h2>{floor.name}</h2>
        <p className="role">{floor.role}</p>
        <p className="data">{floor.data}</p>
      </aside>

      <nav className="elevator" aria-label="Floor index">
        {FLOORS.map((f, i) => (
          <button
            key={f.numeral}
            className={i === activeFloor ? 'active' : ''}
            aria-label={`Floor ${f.numeral}: ${f.name}`}
            onClick={() => jumpTo(i)}
          >
            {f.numeral}
          </button>
        ))}
      </nav>

      <div className="readout">
        DESCENT <b>{descent}%</b> · FLOOR <b>{floor.numeral}</b> · <b className="phase-label">{phase.toUpperCase()}</b>
      </div>
      {phase === 'arrival' && <div className="hint">SCROLL TO DESCEND</div>}
    </div>
  );
}
