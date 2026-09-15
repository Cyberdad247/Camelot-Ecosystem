import { useEffect, useRef } from 'react';

export function HolographicGlobe() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animationFrameId: number;
    let rotation = 0;
    
    const handleResize = () => {
      const parent = canvas.parentElement;
      if (parent) {
        canvas.width = parent.clientWidth;
        canvas.height = parent.clientHeight;
      }
    };
    
    handleResize();
    window.addEventListener('resize', handleResize);

    const render = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      
      const cx = canvas.width / 2;
      const cy = canvas.height / 2;
      const radius = Math.min(cx, cy) * 0.75;

      // Draw Royal Purple backdrop glow
      const grad = ctx.createRadialGradient(cx, cy, radius * 0.1, cx, cy, radius * 1.2);
      grad.addColorStop(0, 'rgba(75, 0, 130, 0.4)'); // Royal Purple
      grad.addColorStop(1, 'rgba(5, 5, 16, 0)'); // Obsidian fade
      ctx.fillStyle = grad;
      ctx.beginPath();
      ctx.arc(cx, cy, radius * 1.2, 0, Math.PI * 2);
      ctx.fill();

      // Gold Wireframe
      ctx.strokeStyle = 'rgba(212, 175, 55, 0.4)'; // Luxora Gold
      ctx.lineWidth = 1;

      for (let i = 0; i < 12; i++) {
        ctx.beginPath();
        ctx.ellipse(
          cx, 
          cy, 
          Math.abs(Math.cos(rotation + (i * Math.PI / 12)) * radius), 
          radius, 
          0, 
          0, 
          Math.PI * 2
        );
        ctx.stroke();
      }

      for (let i = 0; i < 8; i++) {
        ctx.beginPath();
        const yOffset = Math.sin((i - 4) * Math.PI / 8) * radius;
        const xRad = Math.cos((i - 4) * Math.PI / 8) * radius;
        ctx.ellipse(cx, cy + yOffset, xRad, Math.abs(Math.sin(rotation) * xRad * 0.2), 0, 0, Math.PI * 2);
        ctx.stroke();
      }
      
      // Plot VPS Hub (Center)
      ctx.fillStyle = '#D4AF37';
      const nodePos = [
        { lat: 0, lon: 0 }, // Center
        { lat: -0.3, lon: 1.5 },
      ];
      
      nodePos.forEach(np => {
        const x = cx + Math.cos(np.lon + rotation) * Math.cos(np.lat) * radius;
        const y = cy + Math.sin(np.lat) * radius;
        
        if (Math.sin(np.lon + rotation) > -0.2) { // visible hemisphere
           ctx.beginPath();
           ctx.arc(x, y, 4, 0, Math.PI * 2);
           ctx.fill();
           ctx.shadowColor = '#D4AF37';
           ctx.shadowBlur = 15;
           
           // Crosshair for node
           ctx.strokeStyle = '#D4AF37';
           ctx.beginPath();
           ctx.moveTo(x - 8, y);
           ctx.lineTo(x + 8, y);
           ctx.moveTo(x, y - 8);
           ctx.lineTo(x, y + 8);
           ctx.stroke();
        }
      });

      ctx.shadowBlur = 0;
      rotation += 0.003;
      animationFrameId = requestAnimationFrame(render);
    };

    render();

    return () => {
      window.removeEventListener('resize', handleResize);
      cancelAnimationFrame(animationFrameId);
    };
  }, []);

  return (
    <div className="relative w-full h-full min-h-[300px] border border-[#D4AF37]/50 bg-[#050510] rounded-none overflow-hidden shadow-[0_0_40px_rgba(75,0,130,0.2)]">
      <div className="absolute top-0 left-0 w-6 h-6 border-t-2 border-l-2 border-[#D4AF37]" />
      <div className="absolute bottom-0 right-0 w-6 h-6 border-b-2 border-r-2 border-[#D4AF37]" />
      
      <div className="absolute top-4 left-4 z-10 text-[10px] font-['JetBrains_Mono'] text-[#D4AF37] bg-black/60 px-2 py-1 border border-[#D4AF37]/30 tracking-widest backdrop-blur-sm">
        [ HOLO-GRID // ACTIVE ]
      </div>
      <canvas ref={canvasRef} className="w-full h-full block touch-none" />
    </div>
  );
}
