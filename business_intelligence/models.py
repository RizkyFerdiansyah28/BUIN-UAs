from django.db import models

# Create your models here.
class Movie(models.Model):
    title = models.CharField(max_length=255)
    genre = models.CharField(max_length=255)
    director = models.CharField(max_length=255)
    year = models.IntegerField()
    country = models.CharField(max_length=255)
    
    def __str__(self):
        return self.title