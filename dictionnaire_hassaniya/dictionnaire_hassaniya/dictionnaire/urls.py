from django.urls import path
from . import views

urlpatterns = [
    # Page d'accueil
    path('', views.index, name='accueil'),
    
    # Gestion des mots
    path('mot/soumettre/', views.soumettre_mot, name='soumettre_mot'),
    path('mot/<int:mot_id>/', views.detail_mot, name='detail_mot'),
    path('mot/<int:mot_id>/examiner/', views.examiner_mot, name='examiner_mot'),
    path('mot/<int:mot_id>/commentaire/', views.ajouter_commentaire, name='ajouter_commentaire'),
    
    # Pages de modération
    path('moderateur/tableau-bord/', views.tableau_bord_moderateur, name='tableau_bord_moderateur'),
    path('moderateur/filtrer-mots/', views.filtrer_mots, name='filtrer_mots'),
    
    # Authentification
    path('inscription/', views.inscription, name='inscription'),
    path('connexion/', views.connexion, name='connexion'),
    path('deconnexion/', views.deconnexion, name='deconnexion'),
    
    # Profil utilisateur et mots personnels
    path('mes-mots/', views.details_mot, name='details_mot'),
    
    # Notifications
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/marquer_comme_lue/<int:notification_id>/', views.marquer_comme_lue, name='marquer_comme_lue'),
    
    # Administration personnalisée
    path('admin/', views.accueil_admin, name='accueil_admin'),
    path('interface_admin/', views.interface_admin, name='interface_admin'),
    path('admin/gestion-utilisateurs/', views.gestion_utilisateurs, name='gestion_utilisateurs'),
    path('admin/modifier-role/', views.modifier_role, name='modifier_role'),
    # Ajouter cette ligne dans le fichier urls.py
    path('mot/<int:mot_id>/modifier/', views.modifier_mot, name='modifier_mot'),
    path('mot/<int:mot_id>/modifier/', views.modifier_mot, name='modifier_mot'),
    



    # Badges et contributions
    path('badges/', views.liste_badges, name='liste_badges'),
    path('contributeurs/', views.meilleurs_contributeurs, name='meilleurs_contributeurs'),
    
    # Profil utilisateur
    path('profil/', views.profil_utilisateur, name='profil_utilisateur'),
    path('profil/<int:utilisateur_id>/', views.profil_utilisateur, name='profil_utilisateur'),
    
    # Vérification des badges
    path('verifier-badges/', views.verifier_badges, name='verifier_badges'),

        path("mots-racines/", views.liste_mots_racines, name="mots_racines"),

            
        ]