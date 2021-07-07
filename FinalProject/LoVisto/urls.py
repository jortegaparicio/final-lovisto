from . import views
from django.urls import path

urlpatterns = [
    path('', views.index),
    path('allcontent', views.all_content),  # Nos muestra todas las aportaciones
    path('information', views.information),    # Pagina de información de la practica
    path('user', views.user_view),  # Pagina del usuario
    path('<int:content_id>', views.get_content),   # Pagina de cada aportación
]
