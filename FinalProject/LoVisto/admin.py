from django.contrib import admin
from .models import Content, Comment, User, Vote
# Register your models here.
admin.site.register(Content)
admin.site.register(Comment)
admin.site.register(User)
admin.site.register(Vote)
