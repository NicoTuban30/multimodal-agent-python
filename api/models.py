from django.db import models

class Transcript(models.Model):
    user = models.CharField(max_length=100)
    message = models.TextField()
    timestamp = models.BigIntegerField()

    def __str__(self):
        return f"{self.user}: {self.message[:50]}"
