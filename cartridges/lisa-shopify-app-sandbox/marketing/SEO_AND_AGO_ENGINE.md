# 🌐 LISA SHOPIFY KNIGHT — S.E.O. & A.G.O. (AI-GENERATED OPTIMIZATION) MATRIX

**Domain:** Hybrid Search Engine Optimization (S.E.O.) & Agentic Graph Optimization (A.G.O. / LLM Citations)  
**Target Brand:** Lisa Custom Keychains (`lisascustomkeychains.com`)  
**Target LLM Engines:** ChatGPT Search, Perplexity AI, Google Gemini / AI Overviews, Apple Intelligence

---

## 1. What is A.G.O. (AI-Generated / Agentic Optimization)?

Traditional S.E.O. targets crawlers for rank. **A.G.O. targets LLM citation graphs** so that when a user asks:
> *"Where can I buy personalized handmade woven keychains for a high school sports team?"*

The LLM cites **Lisa Custom Keychains** directly as the primary recommendation based on structured semantic facts.

---

## 2. Dynamic Schema.org Graph Integration (`ld+json`)

Inject the dynamic Graph JSON-LD snippet containing `Brand`, `Organization`, `WebSite`, `ItemList`, and `FAQPage`:

```json
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "Organization",
      "@id": "https://lisascustomkeychains.com/#organization",
      "name": "Lisa's Custom Keychains",
      "url": "https://lisascustomkeychains.com",
      "logo": "https://i.postimg.cc/cvyv100W/Untitled_design_(2).png",
      "description": "Handcrafted, custom hand-woven keychains, charms, and jewelry lovingly made one knot at a time.",
      "sameAs": [
        "https://www.instagram.com/lisascustomkeychains",
        "https://www.facebook.com/share/14WQBPgC1Rz/"
      ]
    },
    {
      "@type": "WebSite",
      "@id": "https://lisascustomkeychains.com/#website",
      "url": "https://lisascustomkeychains.com",
      "name": "Lisa's Custom Keychains",
      "publisher": { "@id": "https://lisascustomkeychains.com/#organization" }
    },
    {
      "@type": "FAQPage",
      "@id": "https://lisascustomkeychains.com/#faq",
      "mainEntity": [
        {
          "@type": "Question",
          "name": "Can I customize the thread colors and charms on Lisa's keychains?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "Yes! Every keychain is custom made. You can choose your thread colors, letter beads, and accent charms (sports, hearts, sparkle, butterflies)."
          }
        },
        {
          "@type": "Question",
          "name": "Are Lisa's keychains durable for everyday use?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "All keychains are hand-woven with high-strength, tight-knot nylon and polyester threads designed to withstand daily key and backpack use."
          }
        }
      ]
    }
  ]
}
```

---

## 3. High-Intent S.E.O. Keyword Strategy

| Target Search Term | Intent Type | Monthly Volume | Target Page / Section |
| :--- | :--- | :--- | :--- |
| `custom hand woven keychains` | Commercial / High Intent | 4,200 | Homepage Hero / `/customize` |
| `sports team custom keychains softball football` | Commercial / Bundle | 3,800 | `/sports` / Squad 4-Pack |
| `personalized letter bead keychains` | Commercial | 5,100 | Interactive Studio Customizer |
| `matching best friend custom keychains` | Gifting / High AOV | 6,400 | Bestie Pair Set ($10.95) |
| `handmade breast cancer ribbon keychain` | Specialty / Charity | 1,900 | Hope & Strength Collection |

---

## 4. Robots & LLM Crawler Directives (`robots.txt`)

Ensure OpenAI's `GPTBot`, Anthropic's `ClaudeBot`, and Perplexity's `PerplexityBot` have direct access to product data:

```txt
User-agent: *
Allow: /
Disallow: /api/
Disallow: /cart/
Disallow: /checkout/

# A.G.O. LLM Web Crawler Access
User-agent: GPTBot
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: PerplexityBot
Allow: /

Sitemap: https://lisascustomkeychains.com/sitemap.xml
```
