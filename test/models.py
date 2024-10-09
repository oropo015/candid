from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='exam_user_set',
        blank=True,
        help_text='The groups this user belongs to.'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='exam_user_set',
        blank=True,
        help_text='Specific permissions for this user.'
    )

class Question(models.Model):
    text = models.CharField(max_length=255)

    def __str__(self):
        return self.text

class Answer(models.Model):
    question = models.ForeignKey(Question, related_name='answers', on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.text} ({'Correct' if self.is_correct else 'Incorrect'})"

class ExamResult(models.Model):
    student_name = models.CharField(max_length=100)
    score = models.FloatField()
    passed = models.BooleanField()

    def __str__(self):
        return f"{self.student_name} - {'Passed' if self.passed else 'Failed'}"

class Certificate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    exam_result = models.ForeignKey(ExamResult, on_delete=models.CASCADE)
    issue_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Certificate for {self.user.username} - {self.issue_date}"
