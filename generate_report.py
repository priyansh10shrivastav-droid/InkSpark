"""Script to generate a 2-page Project Report PDF for InkSpark."""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    KeepTogether,
    HRFlowable,
)
from reportlab.pdfgen import canvas


class NumberedCanvas(canvas.Canvas):
    """Canvas to add running header and 'Page X of Y' footer."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#787166"))

        # Running header (only on page 2)
        if self._pageNumber > 1:
            self.drawString(54, 755, "InkSpark: AI-Powered Blog Post Generator — Project Report")
            self.setStrokeColor(colors.HexColor("#E6DFD3"))
            self.setLineWidth(0.5)
            self.line(54, 748, letter[0] - 54, 748)

        # Running footer
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(letter[0] - 54, 34, page_text)
        self.drawString(54, 34, "Confidential — Student Project Submission")
        self.setStrokeColor(colors.HexColor("#E6DFD3"))
        self.setLineWidth(0.5)
        self.line(54, 45, letter[0] - 54, 45)
        self.restoreState()


def build_pdf(filename="InkSpark_Project_Report.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54,
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#201C18"),
        spaceAfter=4,
    )

    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#6E675D"),
        spaceAfter=10,
    )

    h1_style = ParagraphStyle(
        "SectionH1",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#201C18"),
        spaceBefore=10,
        spaceAfter=4,
    )

    h2_style = ParagraphStyle(
        "SectionH2",
        parent=styles["Heading3"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#38332D"),
        spaceBefore=6,
        spaceAfter=2,
    )

    body_style = ParagraphStyle(
        "ReportBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor("#2C2824"),
        spaceAfter=6,
    )

    bullet_style = ParagraphStyle(
        "ReportBullet",
        parent=body_style,
        leftIndent=12,
        firstLineIndent=-8,
        spaceAfter=3,
    )

    meta_table_style = TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FAF7F2")),
        ("BOX", (0, 0), (-1, -1), 0.75, colors.HexColor("#E6DFD3")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#EFE8DC")),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#2C2824")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
        ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
        ("FONTNAME", (3, 0), (3, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
    ])

    story = []

    # ================= PAGE 1 =================
    story.append(Paragraph("INKSPARK — AI BLOG WRITER", title_style))
    story.append(Paragraph("Project Report: Architecture, Prompt Engineering & User Interface Implementation", subtitle_style))

    # Meta Info Table
    meta_data = [
        ["Project Name:", "InkSpark", "Framework:", "Streamlit 1.64 + Python 3.13"],
        ["LLM Provider:", "Google Gemini API (gemini-2.5-flash)", "Architecture:", "Client-Side Decoupled MVC"],
        ["Deliverables:", "Web App, Prompts Module, Report, Code ZIP", "Target Audience:", "Students, Educators & Creators"],
    ]
    t = Table(meta_data, colWidths=[90, 160, 90, 164])
    t.setStyle(meta_table_style)
    story.append(t)
    story.append(Spacer(1, 10))

    # 1. Executive Summary
    story.append(Paragraph("1. Executive Summary & Objective", h1_style))
    story.append(Paragraph(
        "<b>InkSpark</b> is an end-to-end Python web application that transforms user-defined topics into fully structured, "
        "production-ready blog posts in seconds. Designed with a minimal, warm editorial aesthetic inspired by modern publishing "
        "studios, the app allows users to configure the desired subject, narrative tone (Friendly, Formal, Humorous, Motivational, "
        "Educational), and target word count (300–1000 words). The output is rendered in formatted Markdown with real-time "
        "download, regeneration, and state persistence capabilities.",
        body_style,
    ))

    # 2. System Architecture
    story.append(Paragraph("2. System Architecture & Tech Stack", h1_style))
    story.append(Paragraph(
        "The codebase strictly decouples application business logic from the user interface across modular components:",
        body_style,
    ))
    story.append(Paragraph("• <b>Presentation Layer (app.py):</b> Built on Streamlit, managing dynamic rendering, reactive session states, high-contrast editorial styling, and container-based card layouts.", bullet_style))
    story.append(Paragraph("• <b>Prompt Engineering Engine (prompts.py):</b> Standalone template factory isolating prompt semantics from UI code.", bullet_style))
    story.append(Paragraph("• <b>Inference Client (google-generativeai):</b> Secure SDK integration communicating with Google Gemini API endpoints.", bullet_style))
    story.append(Paragraph("• <b>Configuration & Environment (.env / python-dotenv):</b> Complete separation of secrets from repository tracking.", bullet_style))

    # 3. Prompt Engineering
    story.append(Paragraph("3. Prompt Engineering & Structural Constraints", h1_style))
    story.append(Paragraph(
        "To ensure predictable, high-quality blog structures, the prompt implements precise compositional directives:",
        body_style,
    ))
    story.append(Paragraph("• <b>Mandatory Markdown Hierarchy:</b> Strict title formatting (# Title), followed by a 2-3 paragraph introduction, 3 to 4 distinct thematic sections (## Section), and a conclusive wrap-up (## Conclusion).", bullet_style))
    story.append(Paragraph("• <b>Negative Constraints:</b> Explicit rules prohibiting fluff ('in today's fast-paced world'), conversational preambles, introductory filler, and trailing source lists.", bullet_style))
    story.append(Paragraph("• <b>Dynamic Context Injection:</b> Programmatic binding of target word counts and selected tone profiles to align semantic density.", bullet_style))

    # 4. Security & API Handling
    story.append(Paragraph("4. Security, Credentials & Error Resilience", h1_style))
    story.append(Paragraph(
        "API authentication is governed by robust fail-safe protocols:",
        body_style,
    ))
    story.append(Paragraph("• <b>Zero Credential Leakage:</b> The GEMINI_API_KEY is loaded exclusively via environment variables and excluded via .gitignore.", bullet_style))
    story.append(Paragraph("• <b>Graceful Inactive States:</b> If the API key is missing or blank, an actionable warning banner informs the user, and the primary 'Generate Blog' button is disabled.", bullet_style))
    story.append(Paragraph("• <b>Granular Exception Trapping:</b> Differentiated user notifications for HTTP 429 rate limiting, HTTP 401/403 credential invalidation, safety blocking, and network failures with terminal traceback logging.", bullet_style))

    # ================= PAGE 2 =================
    story.append(PageBreak())

    # 5. User Interface
    story.append(Paragraph("5. Editorial User Interface & Publishing Aesthetic", h1_style))
    story.append(Paragraph(
        "InkSpark moves away from high-saturation neon gradients and glassmorphism in favor of a timeless, tactile publishing aesthetic:",
        body_style,
    ))
    story.append(Paragraph("• <b>Palette & Contrast:</b> Warm ivory canvas (#FAF7F2), paper card white (#FDFBF7), deep charcoal typography (#201C18), and soft beige dividing borders (#E6DFD3).", bullet_style))
    story.append(Paragraph("• <b>Typography Pairing:</b> Elegant serif display font (Newsreader) for editorial titles and headers, combined with clean geometric sans-serif (Plus Jakarta Sans) for effortless readability.", bullet_style))
    story.append(Paragraph("• <b>Editorial Workspace:</b> Spacious topic input with real-time character limit (28/200), slider controls, and clean pill buttons with zero distracting emojis.", bullet_style))
    story.append(Paragraph("• <b>Editorial Sidecards:</b> Contextual 'Writing Tips' alongside an interactive 'Recent Drafts' drawer where students can reload previous articles into the editor with a single click.", bullet_style))

    # 6. Functional Workflow
    story.append(Paragraph("6. Functional Workflow & User Journey", h1_style))

    workflow_data = [
        ["Step", "Action", "System Response"],
        ["1. Input", "User enters topic, selects tone, sets word count.", "Validates non-empty input; activates Generate button."],
        ["2. Generation", "User clicks 'Generate Blog'.", "Displays loading spinner, invokes Gemini API via prompts.py."],
        ["3. Output", "Blog post appears in editorial paper card.", "Renders Markdown hierarchy, metadata badge, and action bar."],
        ["4. Export", "User clicks 'Download as Markdown'.", "Serves sanitized slug file (e.g., how-to-start-learning-python.md)."],
        ["5. Iterate", "User clicks 'Regenerate' or 'Clear'.", "Re-synthesizes with identical parameters or resets workspace."],
    ]
    wt = Table(workflow_data, colWidths=[55, 185, 264])
    wt.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#221F1B")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#FAF7F2")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#FFFFFF")),
        ("BOX", (0, 0), (-1, -1), 0.75, colors.HexColor("#E6DFD3")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#EFE8DC")),
        ("TOPPADDING", (0, 0), (-1, -1), 3.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
    ]))
    story.append(wt)
    story.append(Spacer(1, 10))

    # 7. Testing & Verification
    story.append(Paragraph("7. Automated Testing & Verification Suite", h1_style))
    story.append(Paragraph(
        "The project was verified against an extensive automated unit test suite using Streamlit's official AppTest framework:",
        body_style,
    ))
    story.append(Paragraph("• <b>Test Case 1 (Missing Key):</b> Verified that lack of GEMINI_API_KEY renders the required error notice and disables the action trigger without crashing.", bullet_style))
    story.append(Paragraph("• <b>Test Case 2 (Input Validation):</b> Verified that blank or whitespace-only inputs trigger a warning halting execution before invoking the API.", bullet_style))
    story.append(Paragraph("• <b>Test Case 3 (Slugification):</b> Verified string normalization stripping special characters, collapsing spaces, and lowercasing for clean .md downloads.", bullet_style))
    story.append(Paragraph("• <b>Test Case 4 (Error Handling):</b> Validated mapped exception handling for HTTP 429 quota exhaustion, HTTP 403 authorization failures, and safety blocking.", bullet_style))
    story.append(Paragraph("• <b>Test Case 5 (Regeneration & Clear):</b> Verified session state persistence across reruns and reliable teardown upon clearing.", bullet_style))

    # 8. Conclusion
    story.append(Paragraph("8. Conclusion", h1_style))
    story.append(Paragraph(
        "InkSpark fulfills all requirements of a modern AI-assisted publishing workflow. By marrying modular Python code "
        "architecture, defensive API engineering, and a calm, bookish design system, it delivers an intuitive, reliable writing "
        "environment suitable for classroom, academic, and creative publishing applications.",
        body_style,
    ))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated 2-page PDF: {filename}")


if __name__ == "__main__":
    build_pdf()
