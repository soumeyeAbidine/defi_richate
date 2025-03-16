from django.db import models
from django.contrib.auth.hashers import make_password, check_password

class Utilisateur(models.Model):
    ADMIN = "ADMIN"
    MODERATEUR = "MODERATEUR"
    CONTRIBUTEUR = "CONTRIBUTEUR"

    ROLE_CHOICES = [
        (ADMIN, "Administrateur"),
        (MODERATEUR, "Modérateur"),
        (CONTRIBUTEUR, "Contributeur"),
    ]

    email = models.EmailField(unique=True, db_index=True)
    nom_complet = models.CharField(max_length=50)

    # Rôle stocké directement comme un champ CharField
    role = models.CharField(max_length=20, choices=ROLE_CHOICES,  default=CONTRIBUTEUR)

    date_inscription = models.DateTimeField(auto_now_add=True)
    actif = models.BooleanField(default=True)
    mot_de_passe = models.CharField(max_length=128,default="")  # Pour stocker le mot de passe hashé
    def set_password(self, raw_password):
        """Hash et stocke le mot de passe."""
        self.mot_de_passe = make_password(raw_password)

    def check_password(self, raw_password):
        """Vérifie si le mot de passe est correct."""
        return check_password(raw_password, self.mot_de_passe)
    def __str__(self):
        return self.nom_complet

    def est_administrateur(self):
        return self.role == Utilisateur.ADMIN

    def est_moderateur(self):
        return self.role == Utilisateur.MODERATEUR

    def est_contributeur(self):
        return self.role == Utilisateur.CONTRIBUTEUR
    @classmethod
    def create_default_admin(cls):
        if not cls.objects.filter(email="Richatt@gmail.com").exists():
            admin_user = cls(
                nom_complet="Admin",
                email="Richatt@gmail.com",
                mot_de_passe=make_password("Richatt2025@"),  # Mot de passe temporaire
                role=cls.ADMIN
            )
            admin_user.save()
            print("Utilisateur admin créé avec l'email: Richatt@gmail.com")


# Modèle pour les mots
class Mot(models.Model):
    nom = models.CharField(max_length=60, unique=True, db_index=True)
    cree_par = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name="mots")
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nom

# À ajouter dans models.py
class Notification(models.Model):
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name="notifications")
    message = models.TextField()
    lien = models.CharField(max_length=255, blank=True)  # URL vers la page concernée
    est_lue = models.BooleanField(default=False)
    date_creation = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Notification pour {self.utilisateur.nom_complet}"
    
    
# Modèle pour les définitions des mots
class Definition(models.Model):
    mot = models.ForeignKey(Mot, on_delete=models.CASCADE, related_name="definitions")
    texte = models.TextField()
    ajoute_par = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Définition de {self.mot.nom}"


# Modèle pour le statut de validation d'un mot
class StatutValidation(models.Model):
    STATUT_ATTENTE = "attente"
    STATUT_REVISION = "revision"
    STATUT_VALIDE = "valide"
    STATUT_REJETE = "rejete"  # Nouveau statut pour les mots rejetés

    STATUTS_CHOIX = [
        (STATUT_ATTENTE, "En attente"),
        (STATUT_REVISION, "En cours de révision"),
        (STATUT_VALIDE, "Validé"),
        (STATUT_REJETE, "Rejeté"),  # Ajout de l'option dans les choix
    ]

    mot = models.OneToOneField(Mot, on_delete=models.CASCADE, related_name="statut_validation")
    statut = models.CharField(max_length=10, choices=STATUTS_CHOIX, default=STATUT_ATTENTE)
    date_mise_a_jour = models.DateTimeField(auto_now=True)
    moderateur = models.ForeignKey('Utilisateur', on_delete=models.SET_NULL, null=True, blank=True, 
                                  related_name="statuts_moderes")  # Nouveau champ pour tracer le modérateur

    def __str__(self):
        return f"{self.mot.nom} - {self.get_statut_display()}"


# Modèle pour les commentaires
class Commentaire(models.Model):
    mot = models.ForeignKey(Mot, on_delete=models.CASCADE, related_name="commentaires")
    texte = models.TextField()
    auteur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Commentaire de {self.auteur.nom_complet} sur {self.mot.nom}"


# Modèle pour les contributions des utilisateurs
class Contribution(models.Model):
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name="contributions")
    action = models.CharField(max_length=50)  # Ex: "Ajout de mot", "Validation", etc.
    points = models.IntegerField(default=0)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.utilisateur.nom_complet} - {self.action} ({self.points} points)"





from django.db import models
from django.utils import timezone
from .models import Utilisateur

class Badge(models.Model):
    """Modèle pour les badges attribués aux utilisateurs"""
    
    COULEURS = [
        ('primary', 'Bleu'),
        ('success', 'Vert'),
        ('warning', 'Jaune'),
        ('danger', 'Rouge'),
        ('info', 'Bleu clair'),
        ('dark', 'Noir'),
    ]
    
    nom = models.CharField(max_length=100)
    description = models.TextField()
    icone = models.CharField(max_length=50, 
                            help_text="Classe d'icône Bootstrap, ex: bi-trophy")
    couleur = models.CharField(max_length=20, choices=COULEURS, default='primary')
    points_requis = models.IntegerField(default=0)
    mots_requis = models.IntegerField(default=0, 
                                    help_text="Nombre de mots requis pour obtenir ce badge")
    special = models.BooleanField(default=False, 
                               help_text="Badge spécial attribué manuellement")
    date_creation = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.nom
    
    class Meta:
        verbose_name = "Badge"
        verbose_name_plural = "Badges"

class BadgeUtilisateur(models.Model):
    """Relation entre un utilisateur et ses badges"""
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='badges')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    date_obtention = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('utilisateur', 'badge')
        verbose_name = "Badge d'utilisateur"
        verbose_name_plural = "Badges d'utilisateurs"
    
    def __str__(self):
        return f"{self.utilisateur.nom_complet} - {self.badge.nom}"

class Niveau(models.Model):
    """Définition des niveaux pour le système de progression"""
    niveau = models.IntegerField(unique=True)
    titre = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    points_requis = models.IntegerField()
    icone = models.CharField(max_length=50, blank=True, null=True)
    
    def __str__(self):
        return f"Niveau {self.niveau} - {self.titre}"
    
    class Meta:
        ordering = ['niveau']
        verbose_name = "Niveau"
        verbose_name_plural = "Niveaux"

