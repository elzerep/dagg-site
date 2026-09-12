from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.pdfmetrics import stringWidth
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "output" / "pdf" / "Dagg-Component-and-Interaction-Library.pdf"
W, H = 960, 540

PAPER = HexColor("#F4F1E9")
PAPER_LIGHT = HexColor("#FBFAF6")
LIFT = HexColor("#E8E5DB")
INK = HexColor("#171715")
INK_2 = HexColor("#66645E")
RULE = HexColor("#CAC6BA")
CORAL = HexColor("#D97757")
CORAL_DEEP = HexColor("#A64E32")
SAGE = HexColor("#8D9682")

SHOTS = ROOT / "evidence" / "COMPONENT-LIBRARY" / "screenshots"
AUDIT = ROOT / "evidence" / "COMPONENT-LIBRARY-AUDIT" / "2026-08-31"
CROPS = ROOT / "tmp" / "pdfs" / "component-v2-crops"
HERO = ROOT / "design" / "golden-standard" / "image-system" / "p4r6-candidates" / "a" / "a-home-hero-03-desktop.png"


def wrap(text, font, size, max_width):
    lines, current = [], ""
    for word in text.split():
        attempt = word if not current else f"{current} {word}"
        if stringWidth(attempt, font, size) <= max_width:
            current = attempt
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_text(c, text, x, y, width, font="Helvetica", size=11, leading=15,
              color=INK, max_lines=None):
    c.setFillColor(color)
    c.setFont(font, size)
    lines = wrap(text, font, size, width)
    if max_lines is not None:
        lines = lines[:max_lines]
    for line in lines:
        c.drawString(x, y, line)
        y -= leading
    return y


def label(c, text, x, y, color=CORAL_DEEP):
    c.setFillColor(color)
    c.setFont("Courier-Bold", 8.2)
    c.drawString(x, y, text.upper())


def footer(c, page_number, section, dark=False):
    line_color = HexColor("#4B4944") if dark else RULE
    text_color = HexColor("#A5A198") if dark else INK_2
    c.setStrokeColor(line_color)
    c.setLineWidth(0.6)
    c.line(48, 28, W - 48, 28)
    c.setFillColor(text_color)
    c.setFont("Courier", 7.4)
    c.drawString(48, 15, "DAGG DESIGN SYSTEM · DOCUMENT 03 · REVISION 02")
    c.drawRightString(W - 48, 15, f"{section.upper()}  /  {page_number:02d}")


def page(c, number, section, title, deck=None, dark=False):
    c.setFillColor(INK if dark else PAPER)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    label(c, section, 48, H - 42, CORAL if dark else CORAL_DEEP)
    c.setFillColor(PAPER if dark else INK)
    c.setFont("Helvetica-Bold", 28)
    c.drawString(48, H - 80, title)
    if deck:
        draw_text(c, deck, 48, H - 106, W - 96, "Times-Roman", 12.5, 16,
                  HexColor("#D3D0C7") if dark else INK_2, 2)
    footer(c, number, section, dark)


def round_box(c, x, y, width, height, fill=PAPER_LIGHT, stroke=RULE, radius=8):
    c.setFillColor(fill)
    c.setStrokeColor(stroke)
    c.setLineWidth(0.7)
    c.roundRect(x, y, width, height, radius, fill=1, stroke=1)


def image_cover(c, path, x, y, width, height):
    with Image.open(path) as image:
        iw, ih = image.size
    scale = max(width / iw, height / ih)
    dw, dh = iw * scale, ih * scale
    dx, dy = x + (width - dw) / 2, y + (height - dh) / 2
    c.saveState()
    clip = c.beginPath()
    clip.rect(x, y, width, height)
    c.clipPath(clip, stroke=0, fill=0)
    c.drawImage(ImageReader(str(path)), dx, dy, dw, dh, mask="auto")
    c.restoreState()


def image_contain(c, path, x, y, width, height, bg=PAPER_LIGHT, stroke=RULE, radius=8):
    with Image.open(path) as image:
        iw, ih = image.size
    scale = min(width / iw, height / ih)
    dw, dh = iw * scale, ih * scale
    dx, dy = x + (width - dw) / 2, y + (height - dh) / 2
    c.setFillColor(bg)
    c.roundRect(x, y, width, height, radius, fill=1, stroke=0)
    c.saveState()
    clip = c.beginPath()
    clip.roundRect(x, y, width, height, radius)
    c.clipPath(clip, stroke=0, fill=0)
    c.drawImage(ImageReader(str(path)), dx, dy, dw, dh, mask="auto")
    c.restoreState()
    c.setStrokeColor(stroke)
    c.setLineWidth(0.7)
    c.roundRect(x, y, width, height, radius, fill=0, stroke=1)


def bullet(c, title, body, x, y, width, accent=CORAL):
    c.setFillColor(accent)
    c.rect(x, y - 2, 8, 8, fill=1, stroke=0)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 10.5)
    c.drawString(x + 18, y, title)
    return draw_text(c, body, x + 18, y - 18, width - 18,
                     "Helvetica", 9.7, 13, INK_2, 3) - 10


def stat(c, value, title, body, x, y, width, accent=CORAL):
    round_box(c, x, y, width, 142, PAPER_LIGHT)
    c.setFillColor(accent)
    c.setFont("Helvetica-Bold", 34)
    c.drawString(x + 18, y + 89, value)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(x + 18, y + 62, title)
    draw_text(c, body, x + 18, y + 42, width - 36,
              "Helvetica", 9.3, 12, INK_2, 3)


def build():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(OUT), pagesize=(W, H))
    c.setTitle("Dagg Component & Interaction Library · Revision 02")
    c.setAuthor("Dagg")

    # 01 · cover
    c.setFillColor(INK)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    image_cover(c, HERO, 508, 0, 452, H)
    c.setFillColor(INK)
    c.rect(0, 0, 520, H, fill=1, stroke=0)
    label(c, "Dagg design system · document 03 · revision 02", 48, H - 52, CORAL)
    c.setFillColor(PAPER)
    c.setFont("Helvetica-Bold", 43)
    c.drawString(48, H - 134, "Component &")
    c.drawString(48, H - 183, "Interaction Library")
    draw_text(c, "A restrained operating grammar for strategic judgment, retained context and governed execution.",
              48, H - 229, 400, "Times-Roman", 17, 22, HexColor("#D3D0C7"), 4)
    c.setFillColor(CORAL)
    c.rect(48, 87, 177, 6, fill=1, stroke=0)
    c.setFillColor(SAGE)
    c.rect(225, 87, 88, 6, fill=1, stroke=0)
    c.setFillColor(PAPER)
    c.setFont("Courier", 8)
    c.drawString(48, 66, "BEHAVIOR / COMPONENTS / MOTION / RESPONSIVE / ACCESSIBILITY")
    footer(c, 1, "Cover", True)
    c.showPage()

    # 02 · thesis
    page(c, 2, "System thesis", "Intelligence is felt through behavior.",
         "The site earns modernity when context changes, permissions remain legible and every transition resolves — not when every heading receives an icon.")
    draw_text(c, "The image system carries the world. The component system makes that world usable.",
              48, 365, 520, "Times-Roman", 25, 31, INK, 3)
    y = 256
    y = bullet(c, "World", "Decision Field supplies warmth, strategic ambiguity and human judgment.", 48, y, 390, CORAL)
    y = bullet(c, "Instrument", "Operational Evidence makes WorkGraph, Factory, boundaries and proof inspectable.", 48, y, 390, SAGE)
    bullet(c, "Transition", "Machine Signal shows one causal resolution, then stops.", 48, y, 390, INK)
    round_box(c, 550, 112, 360, 268, INK, INK)
    label(c, "Binding rule", 578, 344, CORAL)
    draw_text(c, "Pictures explain the idea. Components expose the mechanism. Icons only clarify an action or a durable product concept.",
              578, 307, 302, "Helvetica-Bold", 19, 25, PAPER, 6)
    draw_text(c, "No icon walls. No decorative dashboards. No terminal theatre.",
              578, 162, 300, "Courier", 9, 13, HexColor("#BBB7AE"), 3)
    c.showPage()

    # 03 · peer audit
    page(c, 3, "Peer audit", "Four references point to restraint, not abundance.",
         "Official pages were inspected beside the Dagg specimen. Identity comes from composition and stateful behavior; icon density remains low.")
    references = [
        ("Anthropic", AUDIT / "anthropic-home-current.png", "Typography and material world"),
        ("OpenAI", AUDIT / "openai-api-current.png", "Product icons inside a mechanism"),
        ("xAI", AUDIT / "xai-build-current.png", "Sparse own marks beside evidence"),
        ("Dagg", AUDIT / "dagg-library-current.png", "Adaptive nav with governed proof"),
    ]
    for i, (name, path, note) in enumerate(references):
        x = 48 + (i % 2) * 444
        y = 246 if i < 2 else 54
        image_contain(c, path, x, y + 24, 420, 148, INK, RULE, 6)
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 10.5)
        c.drawString(x, y + 6, name)
        c.setFont("Helvetica", 9.2)
        c.setFillColor(INK_2)
        c.drawRightString(x + 420, y + 6, note)
    c.showPage()

    # 04 · shared architecture
    page(c, 4, "System architecture", "One substrate. Three visual directions.",
         "A, B and C vary rhythm, proof order and narrative emphasis. Navigation, controls, states and accessibility do not fork.")
    directions = [
        ("A", "Strategic editorial", "Conclusion-led. Decision Field frames the argument. Product proof arrives as evidence.", CORAL),
        ("B", "Product intelligence", "Mechanism-forward. State change and discovery carry the narrative.", SAGE),
        ("C", "Operational authority", "Consequence-forward. Ownership, boundary and provenance become prominent.", INK),
    ]
    for i, (code, title, body, accent) in enumerate(directions):
        x = 48 + i * 292
        round_box(c, x, 190, 268, 228, PAPER_LIGHT)
        c.setFillColor(accent)
        c.rect(x, 402, 268, 16, fill=1, stroke=0)
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 32)
        c.drawString(x + 20, 351, code)
        c.setFont("Helvetica-Bold", 13)
        c.drawString(x + 20, 317, title)
        draw_text(c, body, x + 20, 287, 224, "Times-Roman", 11.5, 16, INK_2, 5)
        c.setFont("Courier", 8)
        c.setFillColor(INK_2)
        c.drawString(x + 20, 214, "SAME TOKENS · BEHAVIOR · TRUTH")
    draw_text(c, "The director selects one coherent direction. The final site never becomes a compromise collage of all three.",
              48, 145, 810, "Times-Roman", 16, 21, INK, 3)
    c.showPage()

    # 05 · icon budget
    page(c, 5, "Icon grammar", "A library is not a usage quota.",
         "The internal collection supports product UI and presentations. The public site uses only what helps a reader act or understand one durable concept.")
    stat(c, "0", "Hero icons", "The thesis is carried by copy, imagery and motion — never an icon row.", 48, 270, 256, CORAL)
    stat(c, "1–2", "Icons per instrument", "Only when they clarify state, ownership, boundary or evidence.", 328, 270, 256, SAGE)
    stat(c, "8", "Semantic concepts", "Decision, context, boundary, build, verification, evidence, ownership and way back.", 608, 270, 256, INK)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(48, 210, "Two layers")
    y = 176
    y = bullet(c, "Utility", "Menu, close, disclosure, external destination and playback use familiar licensed symbols.", 48, y, 385, CORAL)
    bullet(c, "Semantic", "Dagg owns the concept mapping, carrier, tone and motion grammar; the pictogram remains replaceable.", 48, y, 385, SAGE)
    round_box(c, 500, 72, 364, 138, INK, INK)
    label(c, "Public-site restraint", 524, 181, CORAL)
    draw_text(c, "No icon before every headline. No capability-card constellation. No icon as a substitute for product proof.",
              524, 149, 312, "Helvetica-Bold", 13.5, 19, PAPER, 5)
    c.showPage()

    # 06 · adaptive navigation
    page(c, 6, "Component 01", "Adaptive navigation previews intent.",
         "The menu remains navigation. A single proof inset changes with the destination and carries context into the next page.")
    image_contain(c, SHOTS / "flyout-hover-open-1440-1440x900.png", 48, 116, 600, 322, PAPER_LIGHT)
    label(c, "State contract", 688, 420)
    y = 398
    y = bullet(c, "Open", "70–100 ms intent; 180–240 ms close grace.", 688, y, 224, CORAL)
    y = bullet(c, "Preview", "Four destinations change one inset; the panel stays stable.", 688, y, 224, SAGE)
    y = bullet(c, "Carry", "Selected context continues into the destination.", 688, y, 224, INK)
    bullet(c, "Fallback", "Every destination is a real link. Touch uses disclosure.", 688, y, 224, CORAL)
    c.showPage()

    # 07 · navigation devices
    page(c, 7, "Component 01B", "Desktop, tablet and mobile are authored modes.",
         "A compact desktop menu is not stretched mobile. Touch, keyboard and pointer all receive a deliberate path.")
    image_contain(c, SHOTS / "mobile-menu-open-390-390x844.png", 48, 78, 210, 370, PAPER_LIGHT)
    image_contain(c, SHOTS / "mobile-flyout-preview-trust-390-390x844.png", 278, 78, 210, 370, PAPER_LIGHT)
    label(c, "Binding behavior", 536, 422)
    y = 392
    for title, body, accent in [
        ("Desktop", "Pointer and keyboard expose the same proof states.", CORAL),
        ("Tablet landscape", "Pointer plus touch; flyout remains bounded.", SAGE),
        ("Tablet portrait", "Touch-first disclosure and editorial reflow.", SAGE),
        ("Mobile", "Full-canvas navigation, focus containment and body lock.", INK),
        ("All modes", "No critical meaning depends on hover or animation.", CORAL),
    ]:
        y = bullet(c, title, body, 536, y, 370, accent)
    c.showPage()

    # 08 · type and action
    page(c, 8, "Component 02", "Actions look like actions.",
         "Typography establishes hierarchy. Controls explain consequence. Metadata appears only where it carries real provenance or state.")
    image_contain(c, CROPS / "type-actions.jpg", 48, 82, 520, 360, PAPER_LIGHT)
    round_box(c, 604, 82, 308, 360, PAPER_LIGHT)
    label(c, "Type roles", 630, 406)
    type_roles = [
        ("Geist", "decisions, structure and controls"),
        ("Newsreader", "judgment, reflection and warmth"),
        ("JetBrains Mono", "record, state and provenance only"),
    ]
    y = 368
    for name, role in type_roles:
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(630, y, name)
        c.setFont("Helvetica", 9.5)
        c.setFillColor(INK_2)
        c.drawString(630, y - 17, role)
        c.setStrokeColor(RULE)
        c.line(630, y - 30, 884, y - 30)
        y -= 72
    label(c, "Control floor", 630, 163)
    draw_text(c, "44 px target · 48 px mobile navigation · 2 px visible focus ring · no pill theatre",
              630, 139, 250, "Courier", 8.8, 13, CORAL_DEEP, 4)
    c.showPage()

    # 09 · continuum
    page(c, 9, "Component 05", "The decision appears before the technology.",
         "Preserve, simplify, automate, rebuild or retire. One choice changes one explanation and one proof marker.")
    image_contain(c, CROPS / "continuum.jpg", 48, 70, 864, 382, PAPER_LIGHT)
    c.showPage()

    # 10 · WorkGraph
    page(c, 10, "Component 06", "One retained WorkGraph record.",
         "Sources can change while work, decision, owner, boundary and evidence remain part of the same company-specific context.")
    label(c, "Persistent invariants", 48, 418)
    y = 386
    y = bullet(c, "Context", "The company-specific record remains the source of working truth.", 48, y, 280, CORAL)
    y = bullet(c, "Decision", "A material judgment stays attached to the work it changed.", 48, y, 280, CORAL)
    y = bullet(c, "Boundary", "Authority and accountable ownership remain explicit.", 48, y, 280, SAGE)
    bullet(c, "Evidence", "The next intervention begins with retained learning.", 48, y, 280, INK)
    image_contain(c, CROPS / "workgraph-focus.jpg", 356, 54, 556, 350, PAPER_LIGHT)
    c.showPage()

    # 11 · Factory
    page(c, 11, "Component 07", "Finite Factory progression.",
         "Requirement resolves through decision, architecture, build, evaluation and review — with judgment and verification held visibly.")
    label(c, "The pass", 48, 418)
    y = 386
    y = bullet(c, "Finite", "One 6–8 second pass, then an inspectable resolved state.", 48, y, 280, CORAL)
    y = bullet(c, "Judgment hold", "The product decision is visible before the machine continues.", 48, y, 280, CORAL)
    y = bullet(c, "Verification hold", "Evaluation can withhold release and route the exception.", 48, y, 280, SAGE)
    bullet(c, "Way back", "Disable, remove the draft and return to the manual queue.", 48, y, 280, INK)
    image_contain(c, CROPS / "factory-focus.jpg", 356, 54, 556, 350, PAPER_LIGHT)
    c.showPage()

    # 12 · surfaces
    page(c, 12, "Component 08", "One capability. Two surfaces.",
         "The interface changes. The customer harness, permissions, accountable owner and retained record do not.")
    label(c, "What must change together", 48, 418)
    y = 386
    y = bullet(c, "Context", "The request resolves against approved company context.", 48, y, 280, CORAL)
    y = bullet(c, "Action", "The same capability can prepare, explain or execute.", 48, y, 280, CORAL)
    y = bullet(c, "Permission", "No external write or commitment without accountable approval.", 48, y, 280, SAGE)
    bullet(c, "Evidence", "The result returns to the same retained record.", 48, y, 280, INK)
    image_contain(c, CROPS / "surfaces-focus.jpg", 356, 54, 556, 350, PAPER_LIGHT)
    c.showPage()

    # 13 · motion
    page(c, 13, "Motion system", "Motion explains causality — then stops.",
         "The system never moves simply to announce that a page loaded. Every pass resolves, holds or returns control to the reader.", True)
    motion_rows = [
        ("Micro response", "120–180 ms", "hover, focus and selected state"),
        ("State change", "220–300 ms", "continuum, source and surface selection"),
        ("Machine Signal", "0.8–1.2 s", "one coarse-to-resolved causal change"),
        ("Factory pass", "6–8 s max", "pause, replay, judgment and verification holds"),
        ("Reduced motion", "immediate", "same end state without interpolation"),
    ]
    y = 400
    for name, timing, purpose in motion_rows:
        c.setStrokeColor(HexColor("#45433E"))
        c.line(48, y - 12, W - 48, y - 12)
        c.setFillColor(PAPER)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(48, y + 5, name)
        c.setFillColor(CORAL)
        c.setFont("Courier-Bold", 9)
        c.drawString(280, y + 5, timing)
        c.setFillColor(HexColor("#D3D0C7"))
        c.setFont("Helvetica", 10.5)
        c.drawString(442, y + 5, purpose)
        y -= 58
    c.showPage()

    # 14 · responsive
    page(c, 14, "Responsive system", "Six widths. Three interaction modes.",
         "Desktop, iPad landscape, iPad portrait and mobile are separate proofs. Orientation change and zoom remain part of acceptance.")
    profiles = [
        ("Desktop", "1440 / 1280", "full navigation · pointer · keyboard"),
        ("iPad Pro landscape", "1366 × 1024", "bounded flyout · pointer + touch"),
        ("iPad Air landscape", "1180 × 820", "editorial grid · pointer + touch"),
        ("iPad landscape", "1024 × 768", "boundary-aware composition"),
        ("iPad Pro portrait", "1024 × 1366", "touch-first disclosure"),
        ("iPad Air portrait", "820 × 1180", "recomposed editorial grid"),
        ("iPad portrait", "768 × 1024", "never stretched mobile"),
        ("Mobile", "390 / 360 / 320", "full-canvas navigation"),
    ]
    for i, (name, size, behavior) in enumerate(profiles):
        x = 48 + (i % 2) * 440
        y = 376 - (i // 2) * 83
        round_box(c, x, y, 416, 66, PAPER_LIGHT)
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 10.5)
        c.drawString(x + 16, y + 39, name)
        c.setFillColor(CORAL_DEEP)
        c.setFont("Courier-Bold", 8.6)
        c.drawString(x + 16, y + 20, size)
        c.setFillColor(INK_2)
        c.setFont("Helvetica", 8.8)
        c.drawRightString(x + 400, y + 28, behavior)
    c.showPage()

    # 15 · resilience
    page(c, 15, "Resilience", "Meaning survives different capabilities.",
         "Keyboard, touch, reduced motion and no JavaScript preserve the same story, routes and accountable end state.")
    image_contain(c, SHOTS / "focus-first-stop-1440-1440x900.png", 48, 208, 444, 194, PAPER_LIGHT)
    image_contain(c, CROPS / "no-js-first-viewport.jpg", 530, 182, 160, 220, PAPER_LIGHT)
    label(c, "No-JS truth", 724, 421)
    draw_text(c, "Core content is readable. Real destinations remain available. Inert enhanced controls disappear.",
              724, 388, 188, "Helvetica-Bold", 12.5, 18, INK, 7)
    draw_text(c, "The fallback is a complete reading path, not a warning screen.",
              724, 278, 188, "Times-Roman", 11.5, 16, INK_2, 5)
    rules = [
        "Visible focus and logical tab order",
        "Hidden states are never focusable",
        "No-JS exposes core content and real destinations",
        "Reduced motion resolves to the same end state",
        "AA text contrast, 200% zoom and minimum targets",
    ]
    x, y = 48, 176
    for i, rule in enumerate(rules):
        c.setFillColor(CORAL if i in (0, 3) else SAGE)
        c.rect(x, y - 2, 7, 7, fill=1, stroke=0)
        c.setFillColor(INK)
        c.setFont("Helvetica", 10.3)
        c.drawString(x + 16, y, rule)
        x += 290
        if x > 700:
            x = 48
            y -= 38
    c.showPage()

    # 16 · direction use
    page(c, 16, "Direction use", "A, B and C share the parts — not the rhythm.",
         "The system remains recognizable while each direction gives Christian a real choice about how Dagg enters the market.")
    direction_rows = [
        ("Hero", "bounded thesis", "mechanism forward", "consequence forward"),
        ("Decision", "editorial continuum", "interactive continuum", "control-led continuum"),
        ("WorkGraph", "context + judgment", "inspectable record", "owner + boundary"),
        ("Factory", "proof after strategy", "primary product moment", "governed execution"),
        ("Impact", "named consequence", "state change + evidence", "truth + provenance"),
    ]
    headers = ["COMPONENT", "A · STRATEGIC", "B · PRODUCT", "C · OPERATIONAL"]
    widths = [148, 244, 244, 244]
    x0, y0 = 48, 392
    x = x0
    for heading, width in zip(headers, widths):
        c.setFillColor(INK)
        c.rect(x, y0, width - 2, 34, fill=1, stroke=0)
        c.setFillColor(PAPER)
        c.setFont("Courier-Bold", 8.1)
        c.drawString(x + 12, y0 + 12, heading)
        x += width
    y = y0 - 48
    for row in direction_rows:
        x = x0
        for j, (value, width) in enumerate(zip(row, widths)):
            c.setFillColor(LIFT if j == 0 else PAPER_LIGHT)
            c.rect(x, y, width - 2, 45, fill=1, stroke=0)
            c.setFillColor(INK if j == 0 else INK_2)
            c.setFont("Helvetica-Bold" if j == 0 else "Helvetica", 9.1)
            c.drawString(x + 12, y + 18, value)
            x += width
        y -= 49
    draw_text(c, "Selection criterion: the strongest coherent narrative, not the most effects.",
              48, 83, 700, "Times-Roman", 15, 20, INK, 2)
    c.showPage()

    # 17 · acceptance
    page(c, 17, "Acceptance", "Functional substrate passed. Brand restraint revised.",
         "The 40 existing checks remain valid. This revision adds the peer-backed icon budget, adaptive-intelligence rules and repaired rendering.")
    round_box(c, 48, 226, 250, 190, INK, INK)
    c.setFillColor(CORAL)
    c.setFont("Helvetica-Bold", 48)
    c.drawString(72, 340, "40 / 40")
    c.setFillColor(PAPER)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(72, 309, "FUNCTIONAL CHECKS RETAINED")
    c.setFont("Courier", 8.2)
    c.setFillColor(HexColor("#BBB7AE"))
    c.drawString(72, 281, "DESKTOP · TABLET · MOBILE")
    c.drawString(72, 265, "KEYBOARD · TOUCH · NO-JS · REDUCED MOTION")
    label(c, "Revision closes", 342, 398)
    y = 368
    for title, body, accent in [
        ("Icon overreach", "Public-site usage is explicitly sparse; the larger set remains an internal resource.", CORAL),
        ("Adaptive behavior", "Navigation and instruments change meaningful state, not merely animate.", SAGE),
        ("Broken documentation", "Factory, WorkGraph and surface specimens are fully contained and legible.", INK),
        ("Shared authority", "The exact PDF and revision brief are pinned for Claude before A/B/C synthesis.", CORAL),
    ]:
        y = bullet(c, title, body, 342, y, 520, accent)
    label(c, "Next gate", 342, 140)
    draw_text(c, "Three complete, genuinely different and equally verified Home vertical slices: A1, B1 and C1.",
              342, 112, 520, "Times-Roman", 17, 22, INK, 3)
    c.showPage()

    c.save()
    print(OUT)


if __name__ == "__main__":
    build()
