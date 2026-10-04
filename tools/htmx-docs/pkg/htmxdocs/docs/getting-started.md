---
id: DOC-001
title: Getting Started
author: Anya
date: 2026-10-04
status: active
tags: [intro, htmx]
---

# Getting Started

Welcome to the **HTMX Docs system**. 

If you are reading this, the Markdown Content Engine (N011 & N012) is successfully parsing markdown from the filesystem, validating the YAML front matter, converting the Abstract Syntax Tree (AST) into an HTML fragment, and injecting it directly into the DOM via HTMX.

## How it works

1. You clicked the link in the sidebar.
2. HTMX intercepted the click and sent an `hx-get` to the Go backend.
3. The Go backend read `getting-started.md`.
4. It enforced the Wave 0 Interface Freeze (validating that `DOC-001` and the Title exist).
5. It rendered this HTML fragment and sent it back.
6. HTMX swapped it into the `#content` div seamlessly.
