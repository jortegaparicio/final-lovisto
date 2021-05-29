from django.db import models

# Create your models here.
class Input(models.Model):
    clave = models.CharField(max_length=128)
    valor = models.TextField()
