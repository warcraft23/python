from django.db import models
from django.core.validators import MaxLengthValidator

# Create your models here.

class Character(models.Model):
    name=models.CharField(max_length=200)
    def __unicode__(self):
        return self.name