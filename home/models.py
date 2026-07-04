from django.db import models


class Paper(models.Model):
    board = models.CharField(max_length=20)
    class_name = models.CharField(max_length=10)
    subject = models.CharField(max_length=50)
    year = models.IntegerField()
    pdf = models.FileField(upload_to='papers/')

    def __str__(self):
        return f"{self.board} {self.subject} {self.year}"


class Question(models.Model):
    paper = models.ForeignKey(Paper, on_delete=models.CASCADE)
    board = models.CharField(max_length=20, default="ICSE")
    class_name = models.CharField(max_length=10, default="10")
    subject = models.CharField(max_length=50, default="Physics")
    chapter = models.CharField(max_length=100)
    question_text = models.TextField()
    year = models.IntegerField()
    marks = models.IntegerField(null=True, blank=True)
    question_image = models.ImageField(
        upload_to='question_crops/',
        blank=True,
        null=True,
        help_text='Cropped image of the question from the PDF (includes diagrams).',
    )

    def __str__(self):
        return f"{self.chapter} — {self.question_text[:60]}"


from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    board = models.CharField(max_length=20, default="ICSE")
    class_name = models.CharField(max_length=10, default="10")
    streak = models.IntegerField(default=12)

    def __str__(self):
        return f"{self.user.username}'s Profile"

