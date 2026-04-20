"""
CAMELOT APEX OS v300.0 :: COPYRIGHT PDF GENERATOR
-------------------------------------------------------------------------
(c) 2024-2026 Invisioned Marketing Inc. | ALL RIGHTS RESERVED.
Generates comprehensive PDF documents for copyright protection.
"Made by Invisioned Marketing Inc."
-------------------------------------------------------------------------
"""

import os
import re
from fpdf import FPDF

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

# ─── PDF Builder ───────────────────────────────────────────────────────────

class CamelotPDF(FPDF):
    def __init__(self, title, subtitle=""):
        super().__init__()
        self.doc_title = title
        self.doc_subtitle = subtitle
        self.set_auto_page_break(auto=True, margin=20)

    def header(self):
        self.set_font("Helvetica", "B", 8)
        self.set_text_color(100, 100, 100)
        self.cell(0, 5, "(c) 2024-2026 Invisioned Marketing Inc. | ALL RIGHTS RESERVED.", align="L")
        self.ln(3)
        self.set_draw_color(180, 150, 50)
        self.set_line_width(0.5)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 7)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, f"CAMELOT APEX OS v300.0.0 | {self.doc_title} | Page {self.page_no()}/{{nb}}", align="C")

    def add_cover(self):
        self.add_page()
        self.ln(40)
        # Gold bar
        self.set_fill_color(180, 150, 50)
        self.rect(10, self.get_y(), 190, 2, "F")
        self.ln(10)
        # Title
        self.set_font("Helvetica", "B", 28)
        self.set_text_color(30, 30, 30)
        self.multi_cell(0, 12, self._safe(self.doc_title), align="C")
        self.ln(5)
        if self.doc_subtitle:
            self.set_font("Helvetica", "I", 14)
            self.set_text_color(80, 80, 80)
            self.multi_cell(0, 8, self._safe(self.doc_subtitle), align="C")
            self.ln(5)
        # Gold bar
        self.set_fill_color(180, 150, 50)
        self.rect(10, self.get_y(), 190, 2, "F")
        self.ln(15)
        # Meta
        self.set_font("Helvetica", "", 11)
        self.set_text_color(60, 60, 60)
        meta = [
            "Owner/Sovereign: VaShawn O. Head",
            "Entity: Invisioned Marketing Inc.",
            "Contact: InvisionedMarketing@hotmail.com",
            "Version: v300.0.0 (UNIVERSAL_SINGULARITY)",
            "Date: 2026-03-22",
            "",
            '"Made by Invisioned Marketing Inc."',
        ]
        for line in meta:
            self.cell(0, 7, line, align="C")
            self.ln()
        self.ln(20)
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(150, 30, 30)
        self.cell(0, 7, "CONFIDENTIAL - PROPRIETARY DOCUMENT", align="C")

    def _safe(self, text):
        """Make text safe for latin-1 encoding used by core fonts."""
        text = text.replace("\u2014", " -- ")
        text = text.replace("\u2013", " - ")
        text = text.replace("\u2018", "'").replace("\u2019", "'")
        text = text.replace("\u201c", '"').replace("\u201d", '"')
        text = text.replace("\u2026", "...").replace("\u2022", "*")
        text = text.replace("\u03a9", "Omega").replace("\u2122", "(TM)")
        text = text.replace("\u00ae", "(R)").replace("\u00a9", "(c)")
        text = text.replace("\u221e", "INF").replace("\u2248", "~")
        text = text.replace("\u00d7", "x")
        text = text.encode("latin-1", errors="replace").decode("latin-1")
        return text

    def add_md_content(self, md_text):
        self.add_page()
        lines = md_text.split("\n")
        in_table = False
        table_rows = []

        for line in lines:
            stripped = self._safe(line.strip())

            # Skip empty lines
            if not stripped:
                if in_table and table_rows:
                    self._render_table(table_rows)
                    table_rows = []
                    in_table = False
                self.ln(3)
                continue

            # Table rows
            if stripped.startswith("|") and stripped.endswith("|"):
                if re.match(r"^\|[\s\-:|]+\|$", stripped):
                    continue  # skip separator
                cells = [c.strip() for c in stripped.split("|")[1:-1]]
                table_rows.append(cells)
                in_table = True
                continue

            if in_table and table_rows:
                self._render_table(table_rows)
                table_rows = []
                in_table = False

            # Headings
            if stripped.startswith("# ") and not stripped.startswith("##"):
                self.ln(5)
                self.set_font("Helvetica", "B", 18)
                self.set_text_color(30, 30, 30)
                self.multi_cell(0, 9, stripped.lstrip("# ").strip())
                self.set_draw_color(180, 150, 50)
                self.line(10, self.get_y() + 1, 200, self.get_y() + 1)
                self.ln(4)
            elif stripped.startswith("## "):
                self.ln(4)
                self.set_font("Helvetica", "B", 14)
                self.set_text_color(40, 40, 40)
                self.multi_cell(0, 8, stripped.lstrip("# ").strip())
                self.ln(2)
            elif stripped.startswith("### "):
                self.ln(3)
                self.set_font("Helvetica", "B", 12)
                self.set_text_color(50, 50, 50)
                self.multi_cell(0, 7, stripped.lstrip("# ").strip())
                self.ln(2)
            elif stripped.startswith("#### "):
                self.ln(2)
                self.set_font("Helvetica", "BI", 11)
                self.set_text_color(60, 60, 60)
                self.multi_cell(0, 7, stripped.lstrip("# ").strip())
                self.ln(1)
            elif stripped.startswith("---"):
                self.set_draw_color(200, 200, 200)
                self.line(10, self.get_y(), 200, self.get_y())
                self.ln(3)
            elif stripped.startswith("- [") or stripped.startswith("- **"):
                self.set_font("Helvetica", "", 10)
                self.set_text_color(40, 40, 40)
                text = self._clean_md(stripped)
                self.cell(5)
                self.multi_cell(180, 5.5, text)
                self.ln(1)
            elif stripped.startswith("- "):
                self.set_font("Helvetica", "", 10)
                self.set_text_color(40, 40, 40)
                text = self._clean_md(stripped[2:])
                self.cell(8)
                self.multi_cell(177, 5.5, f"* {text}")
                self.ln(1)
            elif stripped.startswith("> "):
                self.set_font("Helvetica", "I", 10)
                self.set_text_color(80, 80, 80)
                self.set_fill_color(245, 245, 240)
                self.cell(5)
                self.multi_cell(180, 5.5, self._clean_md(stripped[2:]), fill=True)
                self.ln(2)
            elif stripped.startswith("```"):
                continue  # skip code fences
            elif re.match(r"^\d+\.", stripped):
                self.set_font("Helvetica", "", 10)
                self.set_text_color(40, 40, 40)
                text = self._clean_md(stripped)
                self.cell(5)
                self.multi_cell(180, 5.5, text)
                self.ln(1)
            else:
                self.set_font("Helvetica", "", 10)
                self.set_text_color(40, 40, 40)
                text = self._clean_md(stripped)
                self.multi_cell(0, 5.5, text)
                self.ln(1)

        # Flush remaining table
        if in_table and table_rows:
            self._render_table(table_rows)

    def _render_table(self, rows):
        if not rows:
            return
        num_cols = len(rows[0])
        page_w = 190
        col_w = page_w / max(num_cols, 1)

        # Header row
        self.set_font("Helvetica", "B", 8)
        self.set_fill_color(50, 50, 60)
        self.set_text_color(255, 255, 255)
        for i, cell in enumerate(rows[0]):
            w = col_w
            self.cell(w, 6, cell[:int(w/1.8)], border=1, fill=True, align="C")
        self.ln()

        # Data rows
        self.set_font("Helvetica", "", 8)
        self.set_text_color(40, 40, 40)
        fill = False
        for row in rows[1:]:
            if fill:
                self.set_fill_color(245, 245, 250)
            else:
                self.set_fill_color(255, 255, 255)
            for i, cell in enumerate(row):
                w = col_w
                text = self._clean_md(cell)[:int(w/1.8)]
                self.cell(w, 5.5, text, border=1, fill=True)
            self.ln()
            fill = not fill
        self.ln(3)

    def _clean_md(self, text):
        text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
        text = re.sub(r"\*(.*?)\*", r"\1", text)
        text = re.sub(r"`(.*?)`", r"\1", text)
        text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
        text = re.sub(r"<!--.*?-->", "", text)
        # Replace unicode with latin-1 safe equivalents
        text = text.replace("\u2014", " -- ")  # em dash
        text = text.replace("\u2013", " - ")   # en dash
        text = text.replace("\u2018", "'")      # left single quote
        text = text.replace("\u2019", "'")      # right single quote
        text = text.replace("\u201c", '"')      # left double quote
        text = text.replace("\u201d", '"')      # right double quote
        text = text.replace("\u2026", "...")     # ellipsis
        text = text.replace("\u2022", "*")       # bullet
        text = text.replace("\u00d7", "x")       # multiplication sign
        text = text.replace("\u2122", "(TM)")    # trademark
        text = text.replace("\u00ae", "(R)")     # registered
        text = text.replace("\u00a9", "(c)")     # copyright
        text = text.replace("(TM)", "(TM)")
        text = text.replace("(R)", "(R)")
        text = text.replace("(c)", "(c)")
        text = text.replace("\u03a9", "Omega")   # Greek Omega
        text = text.replace("\u2248", "~")       # approx
        text = text.replace("\u221e", "INF")     # infinity
        # Force latin-1 safe
        text = text.encode("latin-1", errors="replace").decode("latin-1")
        return text.strip()

    def save(self, filename):
        path = os.path.join(OUTPUT_DIR, filename)
        self.alias_nb_pages()
        self.output(path)
        print(f"  [SEALED] {filename}")
        return path


# ─── Document Definitions ─────────────────────────────────────────────────

def read_file(path):
    for p in [path, path.replace("/", "\\")]:
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8", errors="replace") as f:
                return f.read()
    print(f"  [WARN] File not found: {path}")
    return ""

BASE = "C:/Users/vizio/CAMELOT_OS"
CLI = "C:/Users/vizio/.camelot"

documents = [
    {
        "filename": "01_PROPRIETARY_LICENSE.pdf",
        "title": "PROPRIETARY SOFTWARE LICENSE",
        "subtitle": "Camelot Apex OS v300.0.0",
        "source": f"{BASE}/LICENSE",
    },
    {
        "filename": "02_COPYRIGHT_DECLARATION.pdf",
        "title": "COPYRIGHT DECLARATION",
        "subtitle": "Master IP Declaration & Protected Works Inventory",
        "source": f"{BASE}/COPYRIGHT.md",
    },
    {
        "filename": "03_IP_STRATEGY.pdf",
        "title": "IP STRATEGY",
        "subtitle": "The Split-Brain IP Fortress — Copyright, Trademark, Trade Secret, Patent",
        "source": f"{BASE}/docs/LEGAL/IP_STRATEGY.md",
    },
    {
        "filename": "04_TRADEMARK_REGISTER.pdf",
        "title": "TRADEMARK REGISTER",
        "subtitle": "Intent to Use Filings & Usage Guidelines",
        "source": f"{BASE}/docs/LEGAL/TRADEMARK_REGISTER.md",
    },
    {
        "filename": "05_TRADE_SECRET_MANIFEST.pdf",
        "title": "TRADE SECRET MANIFEST",
        "subtitle": "CONFIDENTIAL — Protected Algorithmic Cores",
        "source": f"{BASE}/docs/LEGAL/TRADE_SECRET_MANIFEST.md",
    },
    {
        "filename": "06_EULA.pdf",
        "title": "END USER LICENSE AGREEMENT",
        "subtitle": "Terms of Service & Usage Rights",
        "source": f"{BASE}/03_VAULT/LEGAL/IP_FORTRESS/EULA.md",
    },
    {
        "filename": "07_IP_DECLARATION.pdf",
        "title": "IP DECLARATION",
        "subtitle": "Master IP Strategy — Vault Level",
        "source": f"{BASE}/03_VAULT/LEGAL/IP_FORTRESS/CAMELOT_APEX_IP_DECLARATION.md",
    },
    {
        "filename": "08_CONSTITUTION.pdf",
        "title": "THE CAMELOT CONSTITUTION",
        "subtitle": "Sovereign Governance Framework",
        "source": f"{BASE}/docs/LAWS/CONSTITUTION.md",
    },
    {
        "filename": "09_TITANIUM_LAWS.pdf",
        "title": "THE TITANIUM LAWS",
        "subtitle": "Immutable Governance Rules",
        "source": f"{BASE}/docs/LAWS/TITANIUM_LAWS.md",
    },
    {
        "filename": "10_THIRD_PARTY_NOTICE.pdf",
        "title": "THIRD-PARTY NOTICE",
        "subtitle": "Open-Source Attributions & Dependencies",
        "source": f"{BASE}/NOTICE.md",
    },
    {
        "filename": "11_COPYRIGHT_HEADERS.pdf",
        "title": "COPYRIGHT HEADER TEMPLATES",
        "subtitle": "Mandatory Source File Headers",
        "source": f"{BASE}/docs/LEGAL/COPYRIGHT_HEADER.md",
    },
    {
        "filename": "12_PROVENANCE_LEDGER.pdf",
        "title": "PROVENANCE LEDGER",
        "subtitle": "Immutable Audit Trail — Camelot Apex OS v300.0.0",
        "source": f"{CLI}/PROVENANCE_LEDGER.md",
    },
    {
        "filename": "13_MASTER_GLOSSARY.pdf",
        "title": "MASTER GLOSSARY",
        "subtitle": "Comprehensive Terminology, Personas, Protocols & Trademarks",
        "source": f"{BASE}/docs/LEGAL/MASTER_GLOSSARY.md",
    },
]


# ─── Generate All PDFs ────────────────────────────────────────────────────

def main():
    print("=" * 70)
    print("CAMELOT APEX OS :: COPYRIGHT PDF GENERATION")
    print("(c) 2024-2026 Invisioned Marketing Inc. | ALL RIGHTS RESERVED.")
    print("=" * 70)
    print()

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for doc in documents:
        print(f"[FORGE] {doc['title']}...")
        content = read_file(doc["source"])
        if not content:
            continue

        pdf = CamelotPDF(doc["title"], doc.get("subtitle", ""))
        pdf.add_cover()
        pdf.add_md_content(content)
        pdf.save(doc["filename"])

    # ── Master Compilation ──
    print()
    print("[FORGE] MASTER COMPILATION (all-in-one)...")
    master = CamelotPDF(
        "CAMELOT APEX OS",
        "Complete Copyright & IP Protection Compilation"
    )
    master.add_cover()

    # Table of contents page
    master.add_page()
    master.set_font("Helvetica", "B", 18)
    master.set_text_color(30, 30, 30)
    master.cell(0, 12, "TABLE OF CONTENTS", align="C")
    master.ln(10)
    master.set_font("Helvetica", "", 11)
    master.set_text_color(50, 50, 50)
    for i, doc in enumerate(documents, 1):
        master.cell(0, 7, f"{i:02d}.  {doc['title']}")
        master.ln()
    master.ln(10)
    master.set_font("Helvetica", "I", 9)
    master.set_text_color(100, 100, 100)
    master.cell(0, 7, "This compilation constitutes a protected collective work under US Copyright Law.", align="C")

    for doc in documents:
        content = read_file(doc["source"])
        if not content:
            continue
        # Section divider page
        master.add_page()
        master.ln(50)
        master.set_fill_color(180, 150, 50)
        master.rect(10, master.get_y(), 190, 2, "F")
        master.ln(10)
        master.set_font("Helvetica", "B", 22)
        master.set_text_color(30, 30, 30)
        master.multi_cell(0, 10, master._safe(doc["title"]), align="C")
        master.ln(3)
        if doc.get("subtitle"):
            master.set_font("Helvetica", "I", 12)
            master.set_text_color(80, 80, 80)
            master.multi_cell(0, 7, master._safe(doc["subtitle"]), align="C")
        master.ln(5)
        master.set_fill_color(180, 150, 50)
        master.rect(10, master.get_y(), 190, 2, "F")

        master.add_md_content(content)

    master.save("00_MASTER_COPYRIGHT_COMPILATION.pdf")

    print()
    print("=" * 70)
    print(f"[COMPLETE] {len(documents) + 1} PDFs generated in:")
    print(f"  {OUTPUT_DIR}")
    print("=" * 70)


if __name__ == "__main__":
    main()
