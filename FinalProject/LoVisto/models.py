from django.db import models
from datetime import datetime
from django.contrib.auth.models import User
# Create your models here.

# HAY QUE AÑADIR EL USUARIO CON EL QUE SE RELACIONA


class User(models.Model):
    user_name = models.CharField(max_length=128, default='')
    password = models.CharField(max_length=128, default='')


    def __str__(self):
        return self.user_name

class Content(models.Model):
    title = models.CharField(max_length=512, default='')
    link = models.CharField(max_length=1024, default='')
    description = models.TextField(default='')
    positive = models.IntegerField(default=0)
    negative = models.IntegerField(default=0)
    date = models.DateField(default=datetime.now)
    num_comment = models.IntegerField(default=0)
    extended_info = models.TextField(default='')
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=User)


    def __str__(self):
        return self.title


class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=User)
    content = models.ForeignKey(Content, on_delete=models.CASCADE)
    vote = models.IntegerField(default=0)   # Si mayor que 0 entonces positivo, si menor que cero negativo else no se ha votado


    def __str__(self):
        return str(self.user) + ' : ' + str(self.vote)

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=User)
    content = models.ForeignKey(Content, on_delete=models.CASCADE)
    body = models.TextField()
    date = models.DateField(default=datetime.now)


    def __str__(self):
        return self.body

