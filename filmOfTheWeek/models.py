from django.db import models

from core.models import Film

from django.utils import timezone
from datetime import timedelta

class FilmOfTheWeek(models.Model):
    film = models.ForeignKey(Film, on_delete=models.CASCADE)
    comment = models.TextField(blank=True)
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(blank=True)
    backdrop_path = models.TextField(blank=True)

    def __str__(self):
        return f'{self.film.title} ({self.film.release_date.year})'
    
    def save(self, *args, **kwargs):
        if not self.end_date:
            self.end_date = self.start_date + timedelta(days=7)
        super().save(*args, **kwargs)