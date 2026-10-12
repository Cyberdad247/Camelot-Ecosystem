# WAVE 0: Interface Freeze
**Target:** EVD-HTMX-SITE-001
**Date:** 2026-10-04
**Status:** ACTIVE DRAFT

This document defines the strict contracts for the HTMX documentation site. Work Packages A (Backend), B (Frontend), and C (Search) MUST build against these specifications to ensure parallel development without integration collisions.

---

## N001: HTTP Routes + Traits

The Go Backend (WP-A) will expose the following strictly defined routes. All UI-facing routes return **HTML Fragments** for HTMX to swap into the DOM, not full HTML documents (unless it is the root application shell).

### 1. Application Shell
*   **Route:** `GET /`
*   **Trait:** Full Page Render
*   **Output:** Returns `index.html` containing the base layout, `head` tags, CSS, HTMX scripts, and the empty `#content` div.

### 2. Document Content
*   **Route:** `GET /docs/:slug`
*   **Trait:** HTMX Fragment
*   **Expected Headers:** `HX-Request: true`
*   **Output:** Returns parsed Markdown as HTML. 
*   **Target:** `hx-target="#content"`

### 3. Search API
*   **Route:** `POST /api/search` (or `GET /api/search?q=`)
*   **Trait:** HTMX Fragment / Live Search
*   **Input:** Form data `q` (search query).
*   **Output:** Returns an HTML list (`<li>`) of search results.
*   **Target:** `hx-target="#search-results"`

### 4. System Health & Verification
*   **Route:** `GET /healthz`
*   **Trait:** JSON / Plaintext
*   **Output:** `200 OK` (Used by Caddy/systemd in WP-D).
*   **Route:** `GET /api/vcl`
*   **Trait:** JSON
*   **Output:** Verification Control List outputs for WP-E (Evidence).

---

## N002: Front Matter Schema

The Markdown Content Engine (Node C) will parse `.md` files. Every documentation file MUST contain the following YAML front matter. If a file violates this schema, the Doc Loader (N011) will throw a strict validation error.

```yaml
---
id: string          # Unique identifier (e.g., DOC-001)
title: string       # Human-readable title
author: string      # Author or Knight name
date: YYYY-MM-DD    # Publication date
status: string      # e.g., "draft", "active", "frozen", "deprecated"
tags: [string]      # Array of classification tags (used for Search N051)
---
```

### Validation Rules (DoD for N011)
1. `id` and `title` are REQUIRED.
2. `date` must be ISO-8601 formatted.
3. If front matter is missing or invalid, the loader must panic/fail during startup to prevent serving malformed documents.
