import json
import re

from django.core.files.base import ContentFile

from .gemini_utils import classify_questions
from .models import Question
from .utils import crop_questions_from_pdf, extract_text


def _parse_gemini_json(raw):
    text = raw.strip()
    text = re.sub(r'^```(?:json)?\s*', '', text)
    text = re.sub(r'\s*```$', '', text)
    return json.loads(text)


def process_pdf(paper):
    text = extract_text(paper.pdf.path)
    result = classify_questions(text)
    data = _parse_gemini_json(result)

    question_texts = [item['question'] for item in data]
    crops = crop_questions_from_pdf(paper.pdf.path, question_texts)

    for item, crop_bytes in zip(data, crops):
        question = Question.objects.create(
            paper=paper,
            board=paper.board,
            class_name=paper.class_name,
            subject=paper.subject,
            chapter=item['chapter'],
            question_text=item['question'],
            year=paper.year,
            marks=item.get('marks'),
        )

        if crop_bytes:
            filename = f'paper_{paper.id}_q_{question.id}.png'
            question.question_image.save(
                filename,
                ContentFile(crop_bytes),
                save=True,
            )
