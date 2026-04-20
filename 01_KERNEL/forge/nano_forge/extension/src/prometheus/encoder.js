/**
 * TOON (Token-Optimized Object Notation) Encoder
 * JS Port for Nano-Knights
 */

export class TOONEncoder {
  /**
   * Encode a code file into TOON format
   */
  static encodeCodeFile(filePath, content, language) {
    const lines = content.split('\n');
    const summary = this.generateCodeSummary(content, language);
    const entities = this.extractCodeEntities(content, language);

    return {
      '@type': 'CODE_FILE',
      id: this.generateId('code', filePath),
      summary,
      entities,
      metadata: {
        language,
        path: filePath,
        lines: lines.length,
        chars: content.length
      },
      raw_ref: `file://${filePath}`,
      timestamp: new Date().toISOString()
    };
  }

  /**
   * Encode a note/document into TOON format
   */
  static encodeNote(title, content, tags = []) {
    const summary = this.generateNoteSummary(content);
    const entities = this.extractNoteEntities(content);

    return {
      '@type': 'NOTE',
      id: this.generateId('note', title),
      summary,
      entities,
      metadata: {
        title,
        wordCount: content.split(/\s+/).length
      },
      tags,
      timestamp: new Date().toISOString()
    };
  }

  /**
   * Encode web article into TOON format
   */
  static encodeWebArticle(url, title, content, author) {
    const cleanContent = this.scrubPII(content);
    const summary = this.generateArticleSummary(cleanContent);
    const entities = this.extractArticleEntities(cleanContent);

    return {
      '@type': 'WEB_ARTICLE',
      id: this.generateId('article', url),
      summary,
      entities,
      metadata: {
        url,
        title,
        author: author || 'Unknown',
        domain: new URL(url).hostname
      },
      raw_ref: url,
      timestamp: new Date().toISOString()
    };
  }

  // ===== PRIVATE HELPERS =====

  static scrubPII(text) {
      if (!text) return "";
      // Redact Email
      text = text.replace(/[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g, '[REDACTED_EMAIL]');
      // Redact Phone (Simple US/Intl format)
      text = text.replace(/(?:\+?1[-.]?)?\(?([0-9]{3})\)?[-. ]?([0-9]{3})[-. ]?([0-9]{4})/g, '[REDACTED_PHONE]');
      return text;
  }

  static generateCodeSummary(content, language) {
    // For now, extract first meaningful comment or generate from structure
    const lines = content.split('\n').slice(0, 10);
    const comments = lines
      .filter(l => l.trim().startsWith('//') || l.trim().startsWith('#'))
      .map(l => l.replace(/^[#/\s]+/, ''))
      .join(' ');
    
    return comments || `${language} file with ${content.split('\n').length} lines`;
  }

  static extractCodeEntities(content, language) {
    const entities = new Set();
    const patterns = {
      'python': [/def\s+(\w+)/g, /class\s+(\w+)/g],
      'javascript': [/function\s+(\w+)/g, /class\s+(\w+)/g, /const\s+(\w+)\s*=/g],
      'typescript': [/function\s+(\w+)/g, /class\s+(\w+)/g, /interface\s+(\w+)/g]
    };

    const langPatterns = patterns[language] || [];
    for (const pattern of langPatterns) {
      const matches = [...content.matchAll(pattern)];
      for (const match of matches) {
        if (match[1]) entities.add(match[1]);
      }
    }

    return Array.from(entities);
  }

  static generateNoteSummary(content) {
    const firstPara = content.split('\n\n')[0];
    return firstPara.length > 200 
      ? firstPara.slice(0, 197) + '...'
      : firstPara;
  }

  static extractNoteEntities(content) {
    const entities = new Set();
    const hashtags = content.match(/#\w+/g) || [];
    hashtags.forEach(tag => entities.add(tag.slice(1)));
    
    const wikiLinks = content.match(/\[\[([\w\s]+)\]\]/g) || [];
    wikiLinks.forEach(link => {
      const term = link.slice(2, -2);
      entities.add(term);
    });

    return Array.from(entities);
  }

  static generateArticleSummary(content) {
    const sentences = content.match(/[^.!?]+[.!?]+/g) || [];
    return sentences.slice(0, 3).join(' ');
  }

  static extractArticleEntities(content) {
    const entities = new Set();
    const matches = [...content.matchAll(/\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b/g)];
    
    for (const match of matches) {
      if (match[0].length > 3) { 
        entities.add(match[0]);
      }
    }

    return Array.from(entities).slice(0, 20); 
  }

  static generateId(prefix, identifier) {
    const hash = this.simpleHash(identifier);
    return `${prefix}_${hash}`;
  }

  static simpleHash(str) {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; 
    }
    return Math.abs(hash).toString(36);
  }
}
