from . import views
from django.urls import path

urlpatterns = {
    path('', views.index),
    path('hello/<name>', views.say_hello_to),
    path('num/<int:num>', views.say_number)
}
