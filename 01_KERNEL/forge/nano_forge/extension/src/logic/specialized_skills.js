/**
 * SPECIALIZED SKILLS REGISTRY
 * Advanced logic for Round Table Personas
 */

export const SPECIALIZED_SKILLS = {
    
    // 🕷️ LADY APIS: Recursive Crawler Helper
    // Returns valid internal links for further exploration
    'RECURSIVE_CRAWL': () => {
        const links = Array.from(document.querySelectorAll('a[href]'))
            .map(a => a.href)
            .filter(href => href.startsWith(window.location.origin)) // Internal only
            .filter(href => !href.includes('#')) // No anchors
            .filter((v, i, a) => a.indexOf(v) === i); // Dedupe
        
        return {
            action: 'CRAWL_RESULT',
            links: links.slice(0, 50), // Cap at 50 to avoid overload
            count: links.length
        };
    },

    // 🏗️ SIR SYNTAX: Code Architect
    // Extracts code blocks with language detection
    'EXTRACT_CODE': () => {
        const blocks = Array.from(document.querySelectorAll('pre code, div.code-block, textarea.code'));
        const artifacts = blocks.map((b, i) => {
            let lang = b.className.match(/language-(\w+)/)?.[1] || 'text';
            return {
                id: `code_${i}`,
                language: lang,
                content: b.innerText.substring(0, 5000) // Cap size
            };
        });

        return {
            action: 'CODE_RESULT',
            artifacts: artifacts,
            count: artifacts.length
        };
    },

    // 🛡️ SIR ZENITH: Security Audit (Client-Side View)
    // Checks visible security features
    'AUDIT_SECURITY': () => {
        const metaCSP = document.querySelector('meta[http-equiv="Content-Security-Policy"]')?.content;
        const https = window.location.protocol === 'https:';
        const scripts = Array.from(document.querySelectorAll('script')).filter(s => !s.src && s.innerText.length > 0);
        
        return {
            action: 'AUDIT_RESULT',
            https: https,
            hasMetaCSP: !!metaCSP,
            inlineScripts: scripts.length,
            riskScore: (!https ? 50 : 0) + (scripts.length > 5 ? 20 : 0)
        };
    }
};
