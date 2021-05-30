from django.db import models

# Create your models here.

# HAY QUE AÑADIR EL USUARIO CON EL QUE SE RELACIONA


class Content(models.Model):
    source = models.CharField(max_length=512)
    title = models.CharField(max_length=512)
    link = models.CharField(max_length=1024)
    description = models.TextField()
    positive = models.IntegerField()
    negative = models.IntegerField()
    date = models.DateField()
    num_comment = models.IntegerField()
    extended_info = models.TextField()
    def __str__(self):
        return self.title

class Comment(models.Model):
    content = models.ForeignKey(Content, on_delete=models.CASCADE)
    body = models.TextField()
    date = models.DateField()
    user = models.CharField(max_length=512)
    def __str__(self):
        return self.user + " : "  + str(self.date)

