from django.db import models
from django.utils import timezone

from django.contrib.auth.models import User
# Create your models here.

# HAY QUE AÑADIR EL USUARIO CON EL QUE SE RELACIONA

class User(models.Model):
    user_name = models.CharField(max_length=128, default='')
    password = models.CharField(max_length=128, default='')


class Content(models.Model):
    title = models.CharField(max_length=512, default='')
    link = models.CharField(max_length=1024, default='')
    description = models.TextField(default='')
    positive = models.IntegerField(default=0)
    negative = models.IntegerField(default=0)
    date = models.DateField(default=timezone.now)
    num_comment = models.IntegerField(default=0)
    extended_info = models.TextField(default='')
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=User)
    def __str__(self):
        return self.title

class Comment(models.Model):
    content = models.ForeignKey(Content, on_delete=models.CASCADE)
    body = models.TextField()
    date = models.DateField()
    #user = models.CharField(max_length=128)
    def __str__(self):
        return self.user + " : " + str(self.date)

