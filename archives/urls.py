from django.urls import path
from . import views

urlpatterns = [
    # Auth — page d'entrée
    path('', views.auth_page, name='auth_page'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('inscription/', views.inscription, name='inscription'),

    # App principale
    path('accueil/', views.home, name='home'),
    path('projets/', views.liste_projets, name='liste_projets'),
    path('projets/<int:pk>/', views.detail_projet, name='detail_projet'),
    path('projets/<int:pk>/telecharger/', views.telecharger_projet, name='telecharger'),
    path('projets/<int:pk>/valider/', views.valider_projet, name='valider_projet'),
    path('projets/<int:pk>/rejeter/', views.rejeter_projet, name='rejeter_projet'),
    path('soumettre/', views.soumettre_projet, name='soumettre'),
    path('profil/', views.mon_profil, name='profil'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('statistiques/', views.statistiques, name='statistiques'),
    path('export/excel/', views.export_excel, name='export_excel'),
    path('export/pdf/', views.export_pdf, name='export_pdf'),
    path('api/recherche/', views.api_recherche, name='api_recherche'),
    path('notifications/lire/', views.marquer_notifs_lues, name='marquer_notifs_lues'),
]