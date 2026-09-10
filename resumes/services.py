"""
Resume parsing service.

Kept as plain functions (no Django request/view dependency) so this can be
unit-tested with a raw file path and reused later if we ever re-parse a
resume without going through the upload view again.
"""
import re
import pdfplumber
import docx


EMAIL_REGEX = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
PHONE_REGEX = re.compile(r'(\+?\d{1,3}[-.\s]?)?\d{10}')


def extract_text_from_pdf(file_path):
    text_parts = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    return "\n".join(text_parts)


def extract_text_from_docx(file_path):
    document = docx.Document(file_path)
    return "\n".join(p.text for p in document.paragraphs if p.text.strip())


def extract_email(text):
    match = EMAIL_REGEX.search(text)
    return match.group(0) if match else ""


def extract_phone(text):
    match = PHONE_REGEX.search(text)
    return match.group(0).strip() if match else ""


def extract_name(text):
    """
    Heuristic: the candidate's name is almost always the first non-empty
    line of a resume, and it's short (not a paragraph). This is
    intentionally simple and explainable rather than using an NLP model -
    matches the spec's "rule-based over AI-API where possible" requirement.
    """
    for line in text.splitlines():
        line = line.strip()
        if line and len(line.split()) <= 5 and not EMAIL_REGEX.search(line):
            return line
    return ""


def parse_resume_file(file_path, file_type):
    """
    Main entry point. Returns a dict of parsed fields plus the raw text.
    Raises on genuinely unreadable/corrupt files - caller is responsible
    for catching and marking the Resume as parsing_status=FAILED.
    """
    if file_type == 'pdf':
        text = extract_text_from_pdf(file_path)
    elif file_type == 'docx':
        text = extract_text_from_docx(file_path)
    else:
        raise ValueError(f"Unsupported file type for parsing: {file_type}")

    if not text.strip():
        raise ValueError("No extractable text found in file (possibly a scanned/image-only PDF).")

    return {
        'parsed_text': text,
        'parsed_name': extract_name(text),
        'parsed_email': extract_email(text),
        'parsed_phone': extract_phone(text),
    }
