import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import black, blue, green, red, orange
from .models import Resume

PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN_LEFT = 20 * mm
MARGIN_RIGHT = PAGE_WIDTH - 20 * mm
MARGIN_BOTTOM = 25 * mm
BOTTOM_LIMIT = MARGIN_BOTTOM + 15 * mm
PHOTO_SIZE = 35 * mm  # Approx 1.4 inches for passport size (2x2 is 51mm, but scaled for resume)

def _check_new_page(c, y, is_experienced):
    if not is_experienced:
        return y
    if y < BOTTOM_LIMIT:
        c.showPage()
        return PAGE_HEIGHT - 20 * mm
    return y

def _draw_heading(c, text, y, font_size=14, color=black):
    c.setFont("Helvetica-Bold", font_size)
    c.setFillColor(color)
    c.drawString(MARGIN_LEFT, y, text)
    c.setFillColor(black)
    return y - 8 * mm

def _draw_block(c, title, body, y_start, is_experienced, template_type):
    if not body or not body.strip():
        return y_start
    y = _draw_heading(c, title, y_start, color=get_template_color(template_type))
    c.setFont("Helvetica", 10)
    text_object = c.beginText(MARGIN_LEFT + 2 * mm, y)
    for line in body.splitlines():
        if not line.strip():
            text_object.textLine("")
        else:
            text_object.textLine(line[:90])
    c.drawText(text_object)
    new_y = text_object.getY() - 6 * mm
    return _check_new_page(c, new_y, is_experienced)

def _draw_photo(c, image_path, y_top, template_type):
    if not image_path or not os.path.exists(image_path):
        return None
    try:
        img = ImageReader(image_path)
        # Resize to passport size
        c.drawImage(img, PAGE_WIDTH - MARGIN_LEFT - PHOTO_SIZE, y_top - PHOTO_SIZE, width=PHOTO_SIZE, height=PHOTO_SIZE, preserveAspectRatio=True)
        # Add border based on template
        if "modern" in template_type:
            c.setStrokeColor(blue)
        elif "classic" in template_type:
            c.setStrokeColor(black)
        c.setLineWidth(1)
        c.rect(PAGE_WIDTH - MARGIN_LEFT - PHOTO_SIZE, y_top - PHOTO_SIZE, PHOTO_SIZE, PHOTO_SIZE)
    except Exception:
        pass

def get_template_color(template_type):
    colors = {
        "google": blue, "microsoft": green, "amazon": orange, "apple": black, "meta": red
    }
    for key, color in colors.items():
        if key in template_type.lower():
            return color
    return black

def generate_resume_pdf(resume: Resume, output_dir: str, base_dir: str, template_type: str) -> str:
    """
    Generate PDF with passport size profile image and template-specific designs.
    Supports enhanced templates with colors and layouts.
    """
    os.makedirs(output_dir, exist_ok=True)
    filename = f"resume_{resume.id}.pdf"
    pdf_path = os.path.join(output_dir, filename)
    is_experienced = template_type.startswith("experienced")
    image_path = None
    if resume.profile_image:
        image_path = os.path.join(base_dir, "uploads", resume.profile_image)
    c = canvas.Canvas(pdf_path, pagesize=A4)
    margin_top = PAGE_HEIGHT - 20 * mm
    y = margin_top

    # Draw photo with template style
    _draw_photo(c, image_path, y, template_type)

    # Header with template-specific font/size
    font_size = 22 if "modern" in template_type else 20
    c.setFont("Helvetica-Bold" if "classic" in template_type else "Helvetica", font_size)
    c.setFillColor(get_template_color(template_type))
    c.drawString(MARGIN_LEFT, y, resume.full_name[:50])
    c.setFillColor(black)
    y -= 10 * mm

    c.setFont("Helvetica", 11)
    contact_parts = [resume.role_title]
    if resume.email:
        contact_parts.append(resume.email)
    if resume.phone:
        contact_parts.append(resume.phone)
    if resume.location:
        contact_parts.append(resume.location)
    contact_line = " | ".join(str(p) for p in contact_parts)
    c.drawString(MARGIN_LEFT, y, contact_line[:95])
    y -= 12 * mm

    sections = []
    if template_type.startswith("fresher"):
        sections = [
            ("Professional Summary", resume.summary),
            ("Technical Skills", resume.skills),
            ("Soft Skills", resume.soft_skills),
            ("Experience / Projects", resume.projects or resume.experience),
            ("Education", resume.education),
            ("Certificates", resume.certificates),
        ]
    else:
        sections = [
            ("Professional Summary", resume.summary),
            ("Technical Skills", resume.skills),
            ("Soft Skills", resume.soft_skills),
            ("Experience", resume.experience),
            ("Projects", resume.projects),
            ("Education", resume.education),
            ("Certificates", resume.certificates),
        ]

    for title, body in sections:
        if body and body.strip():
            y = _draw_block(c, title, body, y, is_experienced, template_type)

    # Template-specific footer or extras
    if "executive" in template_type:
        y = 20 * mm
        c.setFont("Helvetica-Oblique", 9)
        c.drawString(MARGIN_LEFT, y, "Template: Executive Style - Optimized for Senior Roles")

    c.save()
    return os.path.join("generated_pdfs", filename)