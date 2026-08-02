# 🎨 HeadArtworks

> **STATUS:** Active · Shopify Theme

HeadArtworks is a custom Shopify theme for the HeadArtworks e-commerce storefront. Built with Shopify's Liquid templating engine using the standard theme structure (assets, config, layout, sections, snippets, templates).

## Stack

| Layer | Technology |
|-------|-----------|
| Platform | Shopify (Liquid) |
| Structure | Standard Shopify theme layout |
| Assets | CSS, JavaScript, images |

## Structure

```
headartworks/
├── assets/      # Static assets (JS, CSS, images)
├── config/      # Theme settings schema
├── layout/      # Base layout templates
├── sections/    # Reusable section blocks
├── snippets/    # Reusable snippet partials
├── templates/   # Page type templates
└── .phoenix-portal/  # Phoenix Portal deployment config
```

## Setup

```bash
# Use Shopify CLI to develop locally
shopify theme dev --path 02_FORGE/apps/headartworks

# Or upload directly
shopify theme push --path 02_FORGE/apps/headartworks
```

## Scripts

This is a Shopify Liquid theme with no JS/TS build pipeline. Standard Shopify CLI commands apply.
