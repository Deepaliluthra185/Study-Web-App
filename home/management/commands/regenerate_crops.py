from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from home.models import Paper, Question
from home.utils import crop_questions_from_pdf


class Command(BaseCommand):
    help = 'Regenerate cropped question images from uploaded PDF papers'

    def add_arguments(self, parser):
        parser.add_argument(
            '--paper-id',
            type=int,
            help='Only process a single paper by ID',
        )

    def handle(self, *args, **options):
        papers = Paper.objects.all()
        if options['paper_id']:
            papers = papers.filter(id=options['paper_id'])

        if not papers.exists():
            self.stdout.write(self.style.WARNING('No papers found.'))
            return

        for paper in papers:
            questions = list(Question.objects.filter(paper=paper).order_by('id'))
            if not questions:
                self.stdout.write(f'Skipping {paper} — no questions.')
                continue

            crops = crop_questions_from_pdf(
                paper.pdf.path,
                [q.question_text for q in questions],
            )
            updated = 0
            for question, crop_bytes in zip(questions, crops):
                if not crop_bytes:
                    continue
                question.question_image.save(
                    f'paper_{paper.id}_q_{question.id}.png',
                    ContentFile(crop_bytes),
                    save=True,
                )
                updated += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f'{paper}: cropped images for {updated}/{len(questions)} questions'
                )
            )
