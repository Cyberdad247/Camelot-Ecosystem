// Pure client+server HTML generator — no Node.js imports.
// Used by deploy.ts (server) and preview-frame.tsx (client).

import type { ASTNode }    from './parse-ast';
import { deriveTheme }     from './parse-ast';
import type { ThemeTokens } from './parse-ast';

export const TAG_ORDER: Record<string, number> = {
  nav: 0, hero: 1, features: 2, gallery: 3,
  testimonial: 4, pricing: 5, cta: 6, contact: 7, footer: 8,
};

export function esc(s: string): string {
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

export function renderTagHTML(node: ASTNode, t: ThemeTokens): string {
  const intent = esc(String(node.props.intent ?? ''));
  const { bg, fg, surface, surfaceFg, border, focusRing } = t;

  switch (node.tag) {
    case 'nav': return `
  <nav style="position:sticky;top:0;z-index:100;display:flex;align-items:center;justify-content:space-between;padding:1rem 2rem;background:${surface};border-bottom:1px solid ${border};color:${surfaceFg};">
    <span style="font-weight:700;font-size:1.25rem;">Brand</span>
    <ul style="display:flex;gap:2rem;list-style:none;margin:0;padding:0;">
      <li><a href="#features" style="color:${surfaceFg};text-decoration:none;">Features</a></li>
      <li><a href="#pricing"  style="color:${surfaceFg};text-decoration:none;">Pricing</a></li>
      <li><a href="#contact"  style="color:${surfaceFg};text-decoration:none;">Contact</a></li>
    </ul>
  </nav>`;

    case 'hero': return `
  <section style="min-height:60vh;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:4rem 2rem;background:${bg};color:${fg};text-align:center;">
    <h1 style="font-size:clamp(1.75rem,5vw,3.5rem);font-weight:800;line-height:1.1;margin-bottom:1rem;">${intent || 'Welcome'}</h1>
    <p style="font-size:1.1rem;max-width:520px;opacity:0.75;margin-bottom:2rem;">Powered by Camelot-OS Ouroboros SSM engine.</p>
    <a href="#contact" style="padding:0.8rem 1.75rem;background:${focusRing};color:#fff;border-radius:0.5rem;text-decoration:none;font-weight:600;">Get Started</a>
  </section>`;

    case 'features': return `
  <section id="features" style="padding:4rem 2rem;background:${surface};color:${surfaceFg};">
    <h2 style="text-align:center;font-size:1.75rem;font-weight:700;margin-bottom:2.5rem;">${intent || 'Features'}</h2>
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:1.5rem;max-width:800px;margin:0 auto;">
      <div style="padding:1.5rem;background:${bg};border:1px solid ${border};border-radius:0.75rem;text-align:center;color:${fg};"><div style="font-size:1.75rem;margin-bottom:0.5rem;">&#9889;</div><h3 style="font-weight:600;margin-bottom:0.25rem;">Fast</h3><p style="opacity:0.7;font-size:0.875rem;">Lightning performance.</p></div>
      <div style="padding:1.5rem;background:${bg};border:1px solid ${border};border-radius:0.75rem;text-align:center;color:${fg};"><div style="font-size:1.75rem;margin-bottom:0.5rem;">&#128295;</div><h3 style="font-weight:600;margin-bottom:0.25rem;">Flexible</h3><p style="opacity:0.7;font-size:0.875rem;">Adapts to your workflow.</p></div>
      <div style="padding:1.5rem;background:${bg};border:1px solid ${border};border-radius:0.75rem;text-align:center;color:${fg};"><div style="font-size:1.75rem;margin-bottom:0.5rem;">&#9989;</div><h3 style="font-weight:600;margin-bottom:0.25rem;">Reliable</h3><p style="opacity:0.7;font-size:0.875rem;">Always available.</p></div>
    </div>
  </section>`;

    case 'testimonial': return `
  <section style="padding:4rem 2rem;background:${bg};color:${fg};text-align:center;">
    <h2 style="font-size:1.75rem;font-weight:700;margin-bottom:2.5rem;">${intent || 'What People Say'}</h2>
    <blockquote style="max-width:560px;margin:0 auto;padding:1.75rem;background:${surface};border:1px solid ${border};border-radius:0.75rem;font-style:italic;font-size:1rem;color:${surfaceFg};">
      &ldquo;${intent || 'This product changed everything for us.'}&rdquo;
      <footer style="margin-top:0.75rem;font-weight:600;font-style:normal;opacity:0.7;">&mdash; Happy Customer</footer>
    </blockquote>
  </section>`;

    case 'pricing': return `
  <section id="pricing" style="padding:4rem 2rem;background:${surface};color:${surfaceFg};">
    <h2 style="text-align:center;font-size:1.75rem;font-weight:700;margin-bottom:2.5rem;">${intent || 'Pricing'}</h2>
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:1.5rem;max-width:760px;margin:0 auto;">
      <div style="padding:1.5rem;background:${bg};border:1px solid ${border};border-radius:0.75rem;text-align:center;color:${fg};"><h3 style="font-weight:700;margin-bottom:0.25rem;">Starter</h3><p style="font-size:2rem;font-weight:800;margin:0.75rem 0;">$9</p><p style="opacity:0.6;font-size:0.8rem;margin-bottom:1rem;">per month</p><a href="#contact" style="display:block;padding:0.6rem;background:${focusRing};color:#fff;border-radius:0.5rem;text-decoration:none;font-weight:600;font-size:0.875rem;">Choose</a></div>
      <div style="padding:1.5rem;background:${focusRing};border-radius:0.75rem;text-align:center;color:#fff;"><h3 style="font-weight:700;margin-bottom:0.25rem;">Pro</h3><p style="font-size:2rem;font-weight:800;margin:0.75rem 0;">$29</p><p style="opacity:0.75;font-size:0.8rem;margin-bottom:1rem;">per month</p><a href="#contact" style="display:block;padding:0.6rem;background:rgba(255,255,255,0.2);color:#fff;border-radius:0.5rem;text-decoration:none;font-weight:600;font-size:0.875rem;">Choose</a></div>
      <div style="padding:1.5rem;background:${bg};border:1px solid ${border};border-radius:0.75rem;text-align:center;color:${fg};"><h3 style="font-weight:700;margin-bottom:0.25rem;">Enterprise</h3><p style="font-size:2rem;font-weight:800;margin:0.75rem 0;">Custom</p><p style="opacity:0.6;font-size:0.8rem;margin-bottom:1rem;">per month</p><a href="#contact" style="display:block;padding:0.6rem;background:${focusRing};color:#fff;border-radius:0.5rem;text-decoration:none;font-weight:600;font-size:0.875rem;">Choose</a></div>
    </div>
  </section>`;

    case 'gallery': return `
  <section style="padding:4rem 2rem;background:${bg};color:${fg};">
    <h2 style="text-align:center;font-size:1.75rem;font-weight:700;margin-bottom:2.5rem;">${intent || 'Gallery'}</h2>
    <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:0.75rem;max-width:760px;margin:0 auto;">
      <div style="height:140px;background:${border};border-radius:0.5rem;display:flex;align-items:center;justify-content:center;opacity:0.5;font-size:0.875rem;">Image 1</div>
      <div style="height:140px;background:${border};border-radius:0.5rem;display:flex;align-items:center;justify-content:center;opacity:0.5;font-size:0.875rem;">Image 2</div>
      <div style="height:140px;background:${border};border-radius:0.5rem;display:flex;align-items:center;justify-content:center;opacity:0.5;font-size:0.875rem;">Image 3</div>
      <div style="height:140px;background:${border};border-radius:0.5rem;display:flex;align-items:center;justify-content:center;opacity:0.5;font-size:0.875rem;">Image 4</div>
    </div>
  </section>`;

    case 'cta': return `
  <section style="padding:4rem 2rem;background:${focusRing};color:#fff;text-align:center;">
    <h2 style="font-size:2rem;font-weight:800;margin-bottom:0.75rem;">${intent || 'Ready to Get Started?'}</h2>
    <p style="font-size:1rem;opacity:0.85;max-width:440px;margin:0 auto 1.75rem;">Join thousands of users who love our product.</p>
    <a href="#contact" style="display:inline-block;padding:0.875rem 2rem;background:#fff;color:${focusRing};border-radius:0.5rem;text-decoration:none;font-weight:700;">Start Free Trial</a>
  </section>`;

    case 'contact': return `
  <section id="contact" style="padding:4rem 2rem;background:${surface};color:${surfaceFg};">
    <h2 style="text-align:center;font-size:1.75rem;font-weight:700;margin-bottom:2.5rem;">${intent || 'Contact Us'}</h2>
    <form style="max-width:420px;margin:0 auto;display:flex;flex-direction:column;gap:0.875rem;" onsubmit="return false;">
      <input placeholder="Your name" style="padding:0.65rem 0.75rem;border:1px solid ${border};border-radius:0.5rem;background:${bg};color:${fg};font-size:0.9rem;" />
      <input type="email" placeholder="Email address" style="padding:0.65rem 0.75rem;border:1px solid ${border};border-radius:0.5rem;background:${bg};color:${fg};font-size:0.9rem;" />
      <textarea rows="3" placeholder="Your message" style="padding:0.65rem 0.75rem;border:1px solid ${border};border-radius:0.5rem;background:${bg};color:${fg};font-size:0.9rem;resize:vertical;font-family:inherit;"></textarea>
      <button type="submit" style="padding:0.8rem;background:${focusRing};color:#fff;border:none;border-radius:0.5rem;font-weight:600;cursor:pointer;">Send Message</button>
    </form>
  </section>`;

    case 'footer': return `
  <footer style="padding:2.5rem 2rem;background:${surface};color:${surfaceFg};border-top:1px solid ${border};text-align:center;">
    <p style="opacity:0.7;margin-bottom:0.75rem;">${intent || '&copy; 2025 Brand. All rights reserved.'}</p>
    <ul style="display:flex;gap:1.5rem;list-style:none;justify-content:center;margin:0;padding:0;">
      <li><a href="#" style="color:${surfaceFg};opacity:0.6;text-decoration:none;font-size:0.875rem;">Privacy</a></li>
      <li><a href="#" style="color:${surfaceFg};opacity:0.6;text-decoration:none;font-size:0.875rem;">Terms</a></li>
      <li><a href="#" style="color:${surfaceFg};opacity:0.6;text-decoration:none;font-size:0.875rem;">Support</a></li>
    </ul>
  </footer>`;

    default: return `
  <div style="padding:1.5rem;background:${surface};border:1px solid ${border};border-radius:0.75rem;color:${surfaceFg};max-width:420px;margin:1.5rem auto;">
    <h3 style="font-weight:600;margin-bottom:0.375rem;">${intent || node.tag}</h3>
    <p style="opacity:0.7;font-size:0.875rem;">Component: ${node.tag}</p>
  </div>`;
  }
}

export function generateSiteHTML(nodes: ASTNode[], bg: string, siteName: string): string {
  const theme = deriveTheme(bg);
  const sorted = [...nodes].sort((a, b) =>
    (TAG_ORDER[a.tag] ?? 3) - (TAG_ORDER[b.tag] ?? 3),
  );
  const sections = sorted.map(n => renderTagHTML(n, theme)).join('\n');

  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>${esc(siteName)}</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: system-ui, -apple-system, sans-serif; background: ${theme.bg}; color: ${theme.fg}; line-height: 1.6; }
    a { transition: opacity 0.15s; }
    a:hover { opacity: 0.8; }
  </style>
</head>
<body>
${sections}
</body>
</html>`;
}
