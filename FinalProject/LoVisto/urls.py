from . import views
from django.urls import path

urlpatterns = [
    path('', views.index),
    path('login', views.logedIn),
    path('logout', views.logout_view),
    path('<aportation>', views.get_content),
    path('num/<int:num>', views.say_number)
]
