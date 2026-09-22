"""
Generates a crisp, professional high-resolution architecture diagram for DocuPilot.
Outputs to docs/architecture.png.
"""

from pathlib import Path
import pymupdf as fitz


def generate_architecture_diagram():
    out_dir = Path(__file__).resolve().parent.parent / "docs"
    out_dir.mkdir(parents=True, exist_ok=True)
    png_path = out_dir / "architecture.png"

    # Dimensions: 1200 x 750 pt (landscape)
    width, height = 1200, 750
    doc = fitz.open()
    page = doc.new_page(width=width, height=height)

    # Background
    bg_rect = fitz.Rect(0, 0, width, height)
    page.draw_rect(bg_rect, color=None, fill=(0.97, 0.98, 0.99))

    # Top Header Banner
    header_rect = fitz.Rect(40, 30, width - 40, 100)
    page.draw_rect(header_rect, color=(0.88, 0.91, 0.94), fill=(1.0, 1.0, 1.0))
    page.insert_text((60, 62), "DOCUPILOT - SYSTEM ARCHITECTURE & DATA FLOW", fontsize=18, fontname="helv", color=(0.06, 0.09, 0.16))
    page.insert_text((60, 84), "Evidence-First Document Intelligence with Local Vector Embeddings (MiniLM) and Grounded Groq Generation", fontsize=11, fontname="helv", color=(0.39, 0.45, 0.55))

    # Helper function to draw cards
    def draw_card(rect, title, subtitle, items, color_scheme):
        border, bg, title_col, badge = color_scheme
        page.draw_rect(rect, color=border, fill=bg)
        # Badge
        if badge:
            badge_rect = fitz.Rect(rect.x1 - 110, rect.y0 + 10, rect.x1 - 12, rect.y0 + 26)
            page.draw_rect(badge_rect, color=None, fill=border)
            page.insert_text((rect.x1 - 104, rect.y0 + 22), badge, fontsize=8, fontname="helv", color=(1.0, 1.0, 1.0))

        page.insert_text((rect.x0 + 16, rect.y0 + 26), title, fontsize=12, fontname="helv", color=title_col)
        page.insert_text((rect.x0 + 16, rect.y0 + 42), subtitle, fontsize=9, fontname="helv", color=(0.4, 0.45, 0.5))
        page.draw_line(fitz.Point(rect.x0 + 16, rect.y0 + 50), fitz.Point(rect.x1 - 16, rect.y0 + 50), color=(0.88, 0.9, 0.94))

        y_offset = rect.y0 + 68
        for item in items:
            page.insert_text((rect.x0 + 18, y_offset), f"* {item}", fontsize=9, fontname="helv", color=(0.15, 0.2, 0.28))
            y_offset += 16

    # 1. Frontend Layer
    c_blue = ((0.15, 0.39, 0.92), (0.94, 0.97, 1.0), (0.1, 0.25, 0.6), "React + TS")
    draw_card(
        fitz.Rect(50, 120, 310, 300),
        "1. USER & FRONTEND",
        "Linear / Notion-Style SaaS Workspace",
        [
            "Vite + React 18 + TypeScript",
            "Tailwind CSS Enterprise Tokens",
            "3-Column Desktop SaaS Layout",
            "Drag & Drop PDF/TXT Ingestion",
            "Evidence Drawer & Highlight Audit",
            "Smart Suggested Questions Chips"
        ],
        c_blue
    )

    # 2. Ingestion & Document Processing
    c_emerald = ((0.09, 0.64, 0.29), (0.95, 0.99, 0.96), (0.05, 0.4, 0.18), "Document Parser")
    draw_card(
        fitz.Rect(350, 120, 610, 300),
        "2. DOCUMENT PIPELINE",
        "Page-Aware Ingestion & Chunking",
        [
            "PyMuPDF Text & Layout Extraction",
            "SHA-256 File Deduplication Gate",
            "Page Number Tracking (1-Indexed)",
            "Section Heading Detection",
            "Semantic Paragraph Chunking",
            "Zero Token Overhead Question Gen"
        ],
        c_emerald
    )

    # 3. Local Embeddings & Vector DB
    c_purple = ((0.49, 0.23, 0.93), (0.97, 0.95, 1.0), (0.35, 0.12, 0.7), "Local Rs 0 Cost")
    draw_card(
        fitz.Rect(650, 120, 910, 300),
        "3. VECTOR KNOWLEDGE BASE",
        "Zero-Cost Local MiniLM + ChromaDB",
        [
            "all-MiniLM-L6-v2 (Local 384-dim)",
            "Persistent ChromaDB Engine",
            "Cosine Similarity Distance Space",
            "Chunk Metadata Indexing",
            "Document Hash Registry",
            "100% On-Premise / Local Compute"
        ],
        c_purple
    )

    # 4. Anti-Hallucination & Retrieval Gate
    c_amber = ((0.85, 0.47, 0.02), (1.0, 0.98, 0.92), (0.6, 0.3, 0.0), "Gatekeeper")
    draw_card(
        fitz.Rect(950, 120, 1150, 300),
        "4. RELEVANCE GATE",
        "Anti-Hallucination Thresholding",
        [
            "Top-K Retrieval (Default 5)",
            "Similarity Cutoff Gate (0.45)",
            "Drops Low-Relevance Chunks",
            "Deterministic NOT_FOUND Exit",
            "Zero Wasted Groq API Tokens",
            "Evidence Confidence: HIGH/MED"
        ],
        c_amber
    )

    # 5. Grounded Prompt & Context Constructor
    c_slate = ((0.3, 0.4, 0.5), (0.95, 0.96, 0.98), (0.1, 0.15, 0.25), "Token Optimizer")
    draw_card(
        fitz.Rect(50, 340, 420, 520),
        "5. COMPACT CONTEXT BUILDER",
        "Strict Source-ID Tagged Context",
        [
            "System Prompt: Strict Grounding Only",
            "Context with [SOURCE_ID=doc-p-c] Tags",
            "Compact Conversation History (Last 4)",
            "Target: 2-4 Verified Chunks Sent to LLM",
            "No Raw Document Bloat Sent to API",
            "Enforced JSON Schema Output"
        ],
        c_slate
    )

    # 6. Groq LLM Provider
    c_rose = ((0.88, 0.15, 0.25), (1.0, 0.95, 0.96), (0.65, 0.08, 0.15), "LLM Provider")
    draw_card(
        fitz.Rect(460, 340, 780, 520),
        "6. LLM SERVICE LAYER",
        "Groq Provider (Llama 3.3 70B)",
        [
            "Abstract LLMProvider Base Interface",
            "GroqProvider API Client",
            "Low Temperature (0.1) Determinism",
            "Structured JSON Response Format",
            "Returns Answer + Verified Source IDs",
            "Safe Fallback / Local Parser Guard"
        ],
        c_rose
    )

    # 7. Verifiable Attribution & UI Evidence Trail
    c_teal = ((0.05, 0.55, 0.55), (0.93, 0.99, 0.99), (0.02, 0.38, 0.38), "Verified Citations")
    draw_card(
        fitz.Rect(820, 340, 1150, 520),
        "7. EVIDENCE TRAIL & VERIFICATION",
        "Traceable Source Attribution",
        [
            "Source-ID to Metadata Resolver",
            "LLM Cannot Fabricate Citations",
            "Page & Section Verification Badge",
            "Click-to-Inspect Evidence Drawer",
            "Confidence Pill: High / Med / Low",
            "Full Audit Trail for Enterprise Users"
        ],
        c_teal
    )

    # Bottom Architecture Summary Callout
    summary_rect = fitz.Rect(50, 550, width - 50, 700)
    page.draw_rect(summary_rect, color=(0.85, 0.88, 0.92), fill=(1.0, 1.0, 1.0))
    page.insert_text((70, 580), "KEY ARCHITECTURAL HIGHLIGHTS & ZERO-COST DESIGN", fontsize=12, fontname="helv", color=(0.1, 0.15, 0.25))

    highlights = [
        "1. Zero Ingestion Cost: Embeddings (all-MiniLM-L6-v2) and Vector Storage (ChromaDB) run 100% locally with zero subscription or cloud cost.",
        "2. Maximum Token Efficiency: Only 2-4 top-scoring filtered chunks sent to Groq. Entire documents are never sent across the network.",
        "3. Deterministic Anti-Hallucination: If retrieval relevance falls below threshold, the system halts and returns NOT_FOUND without calling LLM.",
        "4. Tamper-Proof Source Attribution: LLM only receives and emits Source IDs ([SOURCE_ID=...]); backend resolves IDs to verified metadata."
    ]
    y_h = 605
    for h in highlights:
        page.insert_text((70, y_h), h, fontsize=9.5, fontname="helv", color=(0.25, 0.3, 0.4))
        y_h += 22

    # Export to high-res PNG (2x scale for retina crispness)
    pix = page.get_pixmap(dpi=150)
    pix.save(str(png_path))
    doc.close()
    print(f"Architecture diagram generated: {png_path}")


if __name__ == "__main__":
    generate_architecture_diagram()
