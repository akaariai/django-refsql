from django.db import models

class Author(models.Model):
    name = models.CharField(max_length=100)
    height = models.IntegerField()
    weight = models.IntegerField()

class Book(models.Model):
    name = models.CharField(max_length=100)
    author = models.ForeignKey(Author)
