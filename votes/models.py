from django.db import models
from django.contrib.auth.models import User


class Decision(models.Model):
    subject = models.CharField(max_length=255)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    start = models.DateTimeField()
    end = models.DateTimeField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.subject}"

    class Meta:
        constraints = [
            # TODO check end_date > start_date
            # TODO check start_date >= created
        ]


class Option(models.Model):
    decision = models.ForeignKey(Decision, on_delete=models.CASCADE)
    text = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.text}"


class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    option = models.ForeignKey(Option, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.get_full_name()}"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'option'], name='unique_vote'),
        ]
