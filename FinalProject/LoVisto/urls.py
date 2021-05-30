from . import views
from django.urls import path

urlpatterns = [
    path('', views.index),
    path('login', views.loged_in),
    path('allcontent', views.all_content),
    path('information', views.information),
    path('logout', views.logout_view),
    path('<content>', views.get_content),
]
