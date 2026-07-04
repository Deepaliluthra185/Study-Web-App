import re

import fitz


def extract_text(pdf_path):
    text = ""
    doc = fitz.open(pdf_path)
    for page in doc:
        text += page.get_text()
    doc.close()
    return text


def _search_snippets(question_text, max_len=80):
    clean = re.sub(r'\s+', ' ', question_text.strip())
    snippets = []

    if len(clean) >= 12:
        snippets.append(clean[:max_len])
        snippets.append(clean[:min(45, len(clean))])

    words = clean.split()
    if len(words) >= 4:
        snippets.append(' '.join(words[:6]))
    if len(words) >= 2:
        snippets.append(' '.join(words[:3]))

    seen = set()
    unique = []
    for snippet in snippets:
        if snippet and snippet not in seen:
            seen.add(snippet)
            unique.append(snippet)
    return unique


def _locate_question(page, question_text):
    for snippet in _search_snippets(question_text):
        rects = page.search_for(snippet)
        if rects:
            return rects[0]
    return None


def crop_questions_from_pdf(pdf_path, question_texts):
    """
    For each question text, locate it in the PDF and crop the vertical region
    containing the question (text + any diagrams below it until the next question).
    Returns a list of PNG bytes (or None when a crop cannot be made).
    """
    if not question_texts:
        return []

    doc = fitz.open(pdf_path)
    locations = []

    for question_text in question_texts:
        found = None
        for page_num in range(len(doc)):
            rect = _locate_question(doc[page_num], question_text)
            if rect:
                found = (page_num, rect.y0, rect.y1)
                break
        locations.append(found)

    crops = []
    render_scale = 2.0
    default_block_height = 320
    side_margin = 12

    for index, question_text in enumerate(question_texts):
        location = locations[index]
        if not location:
            crops.append(None)
            continue

        page_num, y0, _ = location
        page = doc[page_num]
        page_height = page.rect.height
        page_width = page.rect.width

        y1 = page_height
        for next_index in range(index + 1, len(question_texts)):
            next_location = locations[next_index]
            if not next_location:
                continue
            next_page_num, next_y0, _ = next_location
            if next_page_num == page_num:
                y1 = max(y0 + 60, next_y0 - 8)
                break
            if next_page_num > page_num:
                break

        if y1 - y0 < 80:
            y1 = min(y0 + default_block_height, page_height)

        clip = fitz.Rect(
            side_margin,
            max(0, y0 - 8),
            page_width - side_margin,
            min(page_height, y1),
        )

        if clip.height < 30 or clip.width < 30:
            crops.append(None)
            continue

        matrix = fitz.Matrix(render_scale, render_scale)
        pixmap = page.get_pixmap(matrix=matrix, clip=clip)
        crops.append(pixmap.tobytes('png'))

    doc.close()
    return crops
