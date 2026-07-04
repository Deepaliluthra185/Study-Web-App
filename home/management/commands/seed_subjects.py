from django.core.management.base import BaseCommand
from django.db.models.signals import post_save
from home.models import Paper, Question
from home.signals import process_new_pdf


class Command(BaseCommand):
    help = 'Seeds past papers and questions for Maths, Chemistry, and CBSE Physics with signals disabled'

    def handle(self, *args, **options):
        # Disconnect signal to prevent process_pdf from running on dummy PDFs
        post_save.disconnect(process_new_pdf, sender=Paper)
        self.stdout.write("Disconnected post_save signal for Paper model.")

        try:
            # Clean up polluted data first (id > 4 are seeded papers)
            deleted_count, _ = Paper.objects.filter(id__gt=4).delete()
            self.stdout.write(f"Cleaned up {deleted_count} polluted papers (id > 4).")

            # Use an existing PDF from the workspace as placeholder
            dummy_pdf_path = 'papers/physics-02026.pdf'

            papers_data = [
                # Maths CBSE 10 2024
                {
                    'board': 'CBSE', 'class_name': '10', 'subject': 'Maths', 'year': 2024,
                    'questions': [
                        {
                            'chapter': 'Quadratic Equations',
                            'question_text': 'Find the roots of the quadratic equation 2x^2 - 7x + 3 = 0 using the quadratic formula.',
                            'marks': 3
                        },
                        {
                            'chapter': 'Arithmetic Progressions',
                            'question_text': 'In an AP, if the common difference (d) is -4, and the seventh term (a_7) is 4, find the first term (a).',
                            'marks': 2
                        },
                        {
                            'chapter': 'Trigonometry',
                            'question_text': 'If sin θ + cos θ = √2 cos θ, prove that cos θ - sin θ = √2 sin θ.',
                            'marks': 4
                        },
                        {
                            'chapter': 'Probability',
                            'question_text': 'Two dice are thrown together. Find the probability that the sum of the numbers on the two faces is a prime number.',
                            'marks': 3
                        }
                    ]
                },
                # Maths ICSE 10 2024
                {
                    'board': 'ICSE', 'class_name': '10', 'subject': 'Maths', 'year': 2024,
                    'questions': [
                        {
                            'chapter': 'Matrices',
                            'question_text': 'Given A = [[2, 1], [0, -2]] and B = [[4, 1], [-3, -2]], find the matrix C such that A + 2C = B.',
                            'marks': 3
                        },
                        {
                            'chapter': 'Coordinate Geometry',
                            'question_text': 'Find the equation of a line passing through the point (-2, 3) and perpendicular to the line 3x - 4y + 5 = 0.',
                            'marks': 4
                        },
                        {
                            'chapter': 'Statistics',
                            'question_text': 'The mean of the following numbers 10, 15, x, 25, 30 is 21. Find the value of x.',
                            'marks': 2
                        },
                        {
                            'chapter': 'Mensuration',
                            'question_text': 'A solid cone of height 24 cm and radius of base 6 cm is melted and recast into a sphere. Find the radius of the sphere.',
                            'marks': 4
                        }
                    ]
                },
                # Chemistry CBSE 10 2024
                {
                    'board': 'CBSE', 'class_name': '10', 'subject': 'Chemistry', 'year': 2024,
                    'questions': [
                        {
                            'chapter': 'Chemical Reactions and Equations',
                            'question_text': 'Why does the color of copper sulfate solution change when an iron nail is dipped in it? Write the balanced chemical equation.',
                            'marks': 3
                        },
                        {
                            'chapter': 'Acids, Bases and Salts',
                            'question_text': 'What is Plaster of Paris? How is it prepared from Gypsum? Write the chemical equation for the reaction.',
                            'marks': 4
                        },
                        {
                            'chapter': 'Metals and Non-metals',
                            'question_text': 'Explain the term thermite reaction. Write the chemical equation and mention one important application of it.',
                            'marks': 3
                        },
                        {
                            'chapter': 'Carbon and its Compounds',
                            'question_text': 'What is saponification? Write the chemical equation for the saponification reaction of ethyl ethanoate.',
                            'marks': 3
                        }
                    ]
                },
                # Chemistry ICSE 10 2024
                {
                    'board': 'ICSE', 'class_name': '10', 'subject': 'Chemistry', 'year': 2024,
                    'questions': [
                        {
                            'chapter': 'Periodic Properties',
                            'question_text': 'Explain why electron affinity decreases down a group in the periodic table.',
                            'marks': 3
                        },
                        {
                            'chapter': 'Chemical Bonding',
                            'question_text': 'Draw the electron dot structure for the formation of magnesium chloride (MgCl2) from magnesium and chlorine atoms.',
                            'marks': 3
                        },
                        {
                            'chapter': 'Electrolysis',
                            'question_text': 'State the reactions taking place at the anode and cathode during the electrolysis of acidulated water.',
                            'marks': 4
                        },
                        {
                            'chapter': 'Study of Compounds',
                            'question_text': 'Write a balanced chemical equation for the laboratory preparation of ammonia gas from ammonium chloride and calcium hydroxide.',
                            'marks': 4
                        }
                    ]
                },
                # Maths CBSE 12 2025
                {
                    'board': 'CBSE', 'class_name': '12', 'subject': 'Maths', 'year': 2025,
                    'questions': [
                        {
                            'chapter': 'Calculus',
                            'question_text': 'Evaluate the integral: ∫ (3x + 5) / (x^2 + 4x + 13) dx.',
                            'marks': 5
                        },
                        {
                            'chapter': 'Probability',
                            'question_text': "A and B throw a die alternatively till one of them gets a '6' and wins the game. Find their respective probabilities of winning, if A starts first.",
                            'marks': 4
                        },
                        {
                            'chapter': 'Matrices',
                            'question_text': 'Express the matrix A = [[2, -2, -4], [-1, 3, 4], [1, -2, -3]] as the sum of a symmetric and a skew-symmetric matrix.',
                            'marks': 5
                        }
                    ]
                },
                # Physics CBSE 10 2024
                {
                    'board': 'CBSE', 'class_name': '10', 'subject': 'Physics', 'year': 2024,
                    'questions': [
                        {
                            'chapter': 'Light',
                            'question_text': 'A convex lens has a focal length of 15 cm. At what distance should an object from the lens be placed so that it forms a real image at 30 cm on the other side of the lens?',
                            'marks': 4
                        },
                        {
                            'chapter': 'Electricity',
                            'question_text': 'An electric iron consumes energy at a rate of 840 W when heating is at the maximum rate. If the voltage is 220 V, calculate the current and the resistance.',
                            'marks': 3
                        },
                        {
                            'chapter': 'Magnetic Effects',
                            'question_text': "State Fleming's Left-Hand Rule. Explain its application in an electric motor.",
                            'marks': 4
                        }
                    ]
                },
                # Physics CBSE 12 2025
                {
                    'board': 'CBSE', 'class_name': '12', 'subject': 'Physics', 'year': 2025,
                    'questions': [
                        {
                            'chapter': 'Electrostatics',
                            'question_text': "State Gauss's Law in electrostatics. Using this law, derive an expression for the electric field intensity due to an infinitely long straight wire of linear charge density λ.",
                            'marks': 5
                        },
                        {
                            'chapter': 'Current Electricity',
                            'question_text': "State Kirchhoff's Rules. In a Wheatstone bridge, deduce the condition for balance using these rules.",
                            'marks': 5
                        },
                        {
                            'chapter': 'Optics',
                            'question_text': "Derive Lens Maker's Formula for a thin double convex lens.",
                            'marks': 5
                        }
                    ]
                }
            ]

            seeded_papers = 0
            seeded_questions = 0

            for p_data in papers_data:
                # Create paper
                paper = Paper.objects.create(
                    board=p_data['board'],
                    class_name=p_data['class_name'],
                    subject=p_data['subject'],
                    year=p_data['year'],
                    pdf=dummy_pdf_path
                )
                seeded_papers += 1

                for q_data in p_data['questions']:
                    Question.objects.create(
                        paper=paper,
                        board=paper.board,
                        class_name=paper.class_name,
                        subject=paper.subject,
                        chapter=q_data['chapter'],
                        question_text=q_data['question_text'],
                        year=paper.year,
                        marks=q_data['marks']
                    )
                    seeded_questions += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully seeded {seeded_papers} papers and {seeded_questions} questions for Maths, Chemistry, and CBSE Physics.'
                )
            )
        finally:
            # Reconnect signal
            post_save.connect(process_new_pdf, sender=Paper)
            self.stdout.write("Reconnected post_save signal for Paper model.")
