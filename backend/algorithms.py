from .models import Resume

def select_template_for_resume(resume: Resume) -> str:
    """
    Enhanced algorithm to choose a template name
    based on fresher/experienced and years of experience.
    """
    if resume.is_fresher or (resume.years_experience or 0) < 1:
        templates = ["fresher_modern", "fresher_classic", "fresher_minimal", "fresher_creative", "fresher_professional"]
        return templates[hash(resume.full_name) % len(templates)]  # Simple randomization
    if (resume.years_experience or 0) >= 5:
        templates = ["experienced_executive", "experienced_senior"]
    else:
        templates = ["experienced_modern", "experienced_classic", "experienced_minimal"]
    return templates[hash(resume.full_name) % len(templates)]