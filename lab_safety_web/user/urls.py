from django.urls import path
from . import views

urlpatterns = [
    path('user/', views.user, name='user'),
    path('log/', views.log, name='log'),
    path('new/', views.new, name='new'),
    path('edit/', views.edit, name='edit'),
    path('delete/', views.delete, name='delete'),
    path('search/', views.search),
    path('log_search/', views.log_search),
]
