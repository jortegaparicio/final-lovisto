from . import views
from django.urls import path

urlpatterns = [
    path('', views.index),
    path('login', views.loged_in),  # Nos indica si estamos logeados o no
    path('allcontent', views.all_content),  # Nos muestra todas las aportaciones
    path('information', views.information),    # Pagina de información de la practica
    path('logout', views.logout_view),  # Nos sirve para hacer el logout de un usuario
    path('user', views.user_view),  # Pagina del usuario
    path('<int:content_id>', views.get_content),   # Pagina de cada aportación
]
