from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.db import models 
from django.urls import reverse
from functools import wraps
from django.utils import timezone
from datetime import timedelta
from .models import Utilisateur, Mot, Definition, StatutValidation, Commentaire, Contribution, Notification, Badge, BadgeUtilisateur, Niveau



# Decorateurs pour les permissions
def login_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if 'utilisateur_id' not in request.session:
            return redirect('connexion')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if 'utilisateur_id' not in request.session:
            return redirect('connexion')
        try:
            utilisateur = Utilisateur.objects.get(id=request.session['utilisateur_id'])
            if not utilisateur.est_administrateur():
                return redirect('accueil')
            return view_func(request, *args, **kwargs)
        except Utilisateur.DoesNotExist:
            return redirect('connexion')
    return _wrapped_view

# Page d'accueil
# def index(request):
#     # Vérifier si l'utilisateur est connecté
#     if 'utilisateur_id' in request.session:
#         try:
#             utilisateur = Utilisateur.objects.get(id=request.session['utilisateur_id'])
            
#             # Rediriger les administrateurs vers l'interface admin
#             if utilisateur.est_administrateur():
#                 return redirect('accueil_admin')
            
#             # Récupérer les 10 derniers mots validés
#             mots_valides = Mot.objects.filter(
#                 statut_validation__statut=StatutValidation.STATUT_VALIDE
#             ).order_by('-statut_validation__date_mise_a_jour')[:10]
            
#             # Récupérer les 5 meilleurs contributeurs
#             top_contributeurs = Utilisateur.objects.annotate(
#                 total_points=models.Sum('contributions__points')
#             ).filter(total_points__gt=0).order_by('-total_points')[:5]
            
#             contexte = {
#                 'mots_valides': mots_valides,
#                 'top_contributeurs': top_contributeurs,
#             }
            
#             return render(request, 'dictionnaire/index.html', contexte)
        
#         except Utilisateur.DoesNotExist:
#             # Si l'utilisateur n'existe plus, supprimer l'ID de la session
#             del request.session['utilisateur_id']
    
#     # Récupérer les 10 derniers mots validés
#     mots_valides = Mot.objects.filter(
#         statut_validation__statut=StatutValidation.STATUT_VALIDE
#     ).order_by('-statut_validation__date_mise_a_jour')[:10]
    
#     # Récupérer les 5 meilleurs contributeurs
#     top_contributeurs = Utilisateur.objects.annotate(
#         total_points=models.Sum('contributions__points')
#     ).filter(total_points__gt=0).order_by('-total_points')[:5]
    
#     contexte = {
#         'mots_valides': mots_valides,
#         'top_contributeurs': top_contributeurs,
#     }
    
#     return render(request, 'dictionnaire/index.html', contexte)
def index(request):
    # Récupérer les 10 derniers mots validés
    mots_valides = Mot.objects.filter(
        statut_validation__statut=StatutValidation.STATUT_VALIDE
    ).order_by('-statut_validation__date_mise_a_jour')[:10]
    
    # Récupérer les meilleurs contributeurs avec leurs points
    top_contributeurs = Utilisateur.objects.annotate(
        total_points=models.Sum('contributions__points')
    ).filter(total_points__gt=0).order_by('-total_points')[:5]
    
    contexte = {
        'mots_valides': mots_valides,
        'top_contributeurs': top_contributeurs,
    }
    
    return render(request, 'dictionnaire/index.html', contexte)
# Authentification
def inscription(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        nom_complet = request.POST.get('nom_complet')
        mot_de_passe = request.POST.get('mot_de_passe')
        
        # Création d'un utilisateur avec le rôle contributeur par défaut
        utilisateur = Utilisateur(
            email=email,
            nom_complet=nom_complet,
            role=Utilisateur.CONTRIBUTEUR  # Toujours contributeur
        )
        utilisateur.set_password(mot_de_passe)
        utilisateur.save()
        
        # Connecter l'utilisateur
        request.session['utilisateur_id'] = utilisateur.id
        
        return redirect('accueil')
        
    return render(request, 'dictionnaire/inscription.html')

def connexion(request):
    # Vérifier si l'utilisateur est déjà connecté
    if 'utilisateur_id' in request.session:
        # Récupérer l'utilisateur
        utilisateur_id = request.session['utilisateur_id']
        try:
            utilisateur = Utilisateur.objects.get(id=utilisateur_id)
            
            # Rediriger selon le rôle
            if utilisateur.est_administrateur():
                return redirect('accueil_admin')
            elif utilisateur.est_moderateur():
                return redirect('tableau_bord_moderateur')
            else:
                return redirect('accueil')
        except Utilisateur.DoesNotExist:
            # Si l'utilisateur n'existe plus, supprimer l'ID de la session
            del request.session['utilisateur_id']
    
    # Traiter la soumission du formulaire de connexion
    if request.method == 'POST':
        email = request.POST.get('email')
        mot_de_passe = request.POST.get('mot_de_passe')
        
        if not email or not mot_de_passe:
            messages.error(request, 'Veuillez remplir tous les champs.')
            return render(request, 'dictionnaire/connexion.html', {'erreur': 'Veuillez remplir tous les champs.'})
        
        try:
            utilisateur = Utilisateur.objects.get(email=email)
            
            # Vérifier le mot de passe
            if utilisateur.check_password(mot_de_passe):
                # Enregistrer l'ID de l'utilisateur dans la session
                request.session['utilisateur_id'] = utilisateur.id
                
                # Rediriger selon le rôle
                if utilisateur.est_administrateur():
                    return redirect('accueil_admin')
                elif utilisateur.est_moderateur():
                    return redirect('tableau_bord_moderateur')
                else:
                    return redirect('accueil')
            else:
                messages.error(request, 'Mot de passe incorrect.')
                return render(request, 'dictionnaire/connexion.html', {'erreur': 'Mot de passe incorrect.'})
        
        except Utilisateur.DoesNotExist:
            messages.error(request, 'Aucun compte trouvé avec cet email.')
            return render(request, 'dictionnaire/connexion.html', {'erreur': 'Aucun compte trouvé avec cet email.'})
    
    # Afficher le formulaire de connexion
    return render(request, 'dictionnaire/connexion.html')

def deconnexion(request):
    if 'utilisateur_id' in request.session:
        del request.session['utilisateur_id']  # Supprimer l'ID de l'utilisateur de la session
    return redirect('accueil')

# Gestion des mots
def soumettre_mot(request):
    if 'utilisateur_id' not in request.session:
        return redirect('connexion')  # Rediriger vers la page de connexion si l'utilisateur n'est pas connecté

    utilisateur_id = request.session['utilisateur_id']
    utilisateur = Utilisateur.objects.get(id=utilisateur_id)

    if request.method == 'POST':
        nom_mot = request.POST.get('nom')
        definition_texte = request.POST.get('definition')
        
        if not nom_mot or not definition_texte:
            return render(request, 'dictionnaire/soumettre_mot.html', {
                'erreur': 'Le nom du mot et la définition sont obligatoires.'
            })
        
        # Créer le mot et sa définition
        mot = Mot.objects.create(
            nom=nom_mot,
            cree_par=utilisateur
        )
        
        Definition.objects.create(
            mot=mot,
            texte=definition_texte,
            ajoute_par=utilisateur
        )
        
        StatutValidation.objects.create(
            mot=mot,
            statut=StatutValidation.STATUT_ATTENTE
        )
        
        Contribution.objects.create(
            utilisateur=utilisateur,
            action="Ajout de mot",
            points=5
        )
        
        # Notifier les modérateurs du nouveau mot
        moderateurs = Utilisateur.objects.filter(role__in=[Utilisateur.ADMIN, Utilisateur.MODERATEUR])
        for moderateur in moderateurs:
            Notification.objects.create(
                utilisateur=moderateur,
                message=f"Nouveau mot '{mot.nom}' soumis par {utilisateur.nom_complet}.",
                lien=f"/mot/{mot.id}/examiner/"
            )
        
        return redirect('detail_mot', mot_id=mot.id)
    
    return render(request, 'dictionnaire/soumettre_mot.html')

def detail_mot(request, mot_id):
    mot = get_object_or_404(Mot, id=mot_id)
    definitions = mot.definitions.all()
    commentaires = mot.commentaires.all().order_by('-date_creation')
    
    # Vérifier si l'utilisateur peut examiner ce mot (modérateur ou admin)
    peut_examiner = False
    if 'utilisateur_id' in request.session:
        try:
            utilisateur = Utilisateur.objects.get(id=request.session['utilisateur_id'])
            peut_examiner = utilisateur.est_moderateur() or utilisateur.est_administrateur()
        except Utilisateur.DoesNotExist:
            pass
    
    return render(request, 'dictionnaire/detail_mot.html', {
        'mot': mot,
        'definitions': definitions,
        'commentaires': commentaires,
        'peut_examiner': peut_examiner
    })

def modifier_mot(request, mot_id):
    # Vérifier si l'utilisateur est connecté
    if 'utilisateur_id' not in request.session:
        return redirect('connexion')
        
    # Récupérer l'utilisateur
    utilisateur_id = request.session['utilisateur_id']
    utilisateur = get_object_or_404(Utilisateur, id=utilisateur_id)
    
    # Récupérer le mot
    mot = get_object_or_404(Mot, id=mot_id)
    
    # Vérifier si le mot est déjà validé et que l'utilisateur est juste un contributeur
    if mot.statut_validation.statut == StatutValidation.STATUT_VALIDE and not (utilisateur.est_moderateur() or utilisateur.est_administrateur()):
       
        return redirect('detail_mot', mot_id=mot.id)
    
    # Vérifier que l'utilisateur est le créateur du mot ou un modérateur/admin
    if mot.cree_par.id != utilisateur.id and not (utilisateur.est_moderateur() or utilisateur.est_administrateur()):
        messages.error(request, "Vous n'avez pas les droits pour modifier ce mot car vous n'en êtes pas l'auteur.")
        return redirect('detail_mot', mot_id=mot.id)
    
    # Récupérer la définition existante (première définition)
    definition_existante = mot.definitions.first()
    
    if request.method == 'POST':
        nouveau_nom = request.POST.get('nom')
        nouvelle_definition = request.POST.get('definition')
        
        if not nouveau_nom or not nouvelle_definition:
            return render(request, 'dictionnaire/modifier_mot.html', {
                'erreur': 'Le nom du mot et la définition sont obligatoires.',
                'mot': mot,
                'definition': definition_existante
            })
        
        # Mettre à jour le mot
        mot.nom = nouveau_nom
        mot.save()
        
        # Mettre à jour la définition ou en créer une nouvelle
        if definition_existante:
            definition_existante.texte = nouvelle_definition
            definition_existante.save()
        else:
            Definition.objects.create(
                mot=mot,
                texte=nouvelle_definition,
                ajoute_par=utilisateur
            )
        
        # Si c'est un modérateur ou administrateur qui modifie un mot validé, on conserve le statut validé
        if utilisateur.est_moderateur() or utilisateur.est_administrateur():
            # Ajouter un commentaire système pour tracer la modification par modérateur
            Commentaire.objects.create(
                mot=mot,
                texte=f"Mot modifié par {utilisateur.nom_complet} (modérateur/admin)",
                auteur=utilisateur
            )
        else:
            # Si c'est un contributeur qui modifie un mot en attente ou en révision, on garde le statut actuel
            # Ajouter un commentaire système pour tracer la modification
            Commentaire.objects.create(
                mot=mot,
                texte=f"Mot modifié par {utilisateur.nom_complet}",
                auteur=utilisateur
            )
        
        # Ajouter des points pour la contribution
        Contribution.objects.create(
            utilisateur=utilisateur,
            action="Modification de mot",
            points=2
        )
        
        # Notifier les modérateurs si le statut n'est pas validé
        if mot.statut_validation.statut != StatutValidation.STATUT_VALIDE:
            moderateurs = Utilisateur.objects.filter(role__in=[Utilisateur.ADMIN, Utilisateur.MODERATEUR])
            for moderateur in moderateurs:
                Notification.objects.create(
                    utilisateur=moderateur,
                    message=f"Le mot '{mot.nom}' a été modifié par {utilisateur.nom_complet}.",
                    lien=f"/mot/{mot.id}/examiner/"
                )
        
        messages.success(request, "Le mot a été modifié avec succès.")
        return redirect('detail_mot', mot_id=mot.id)
    
    return render(request, 'dictionnaire/modifier_mot.html', {
        'mot': mot,
        'definition': definition_existante
    })

def examiner_mot(request, mot_id):
    if 'utilisateur_id' not in request.session:
        return redirect('connexion')

    utilisateur_id = request.session['utilisateur_id']
    utilisateur = Utilisateur.objects.get(id=utilisateur_id)

    mot = get_object_or_404(Mot, id=mot_id)
    statut = mot.statut_validation
    definitions = mot.definitions.all()
    commentaires = mot.commentaires.all().order_by('-date_creation')
    
    # Vérifier si l'utilisateur est modérateur ou administrateur
    if not (utilisateur.est_moderateur() or utilisateur.est_administrateur()):
        return redirect('detail_mot', mot_id=mot.id)
        
    # Récupérer les modérateurs pour affichage
    moderateurs = Utilisateur.objects.filter(role__in=[Utilisateur.ADMIN, Utilisateur.MODERATEUR])
    
    if request.method == 'POST':
        action = request.POST.get('action')
        commentaire_texte = request.POST.get('commentaire', '')
        
        if action == 'commencer_revision':
            statut.statut = StatutValidation.STATUT_REVISION
            statut.moderateur = utilisateur
            statut.save()
            
            # Ajouter un commentaire système
            commentaire_texte = f"Révision commencée par {utilisateur.nom_complet}"
            Commentaire.objects.create(
                mot=mot,
                texte=commentaire_texte,
                auteur=utilisateur
            )
            
            # Ajouter points de contribution pour le modérateur
            Contribution.objects.create(
                utilisateur=utilisateur,
                action="Début de révision",
                points=2
            )
            
            # Notifier l'auteur du mot
            Notification.objects.create(
                utilisateur=mot.cree_par,
                message=f"La révision de votre mot '{mot.nom}' a commencé.",
                lien=f"/mot/{mot.id}/"
            )
            
        elif action == 'valider':
            statut.statut = StatutValidation.STATUT_VALIDE
            statut.moderateur = utilisateur
            statut.save()
            
            # Ajouter un commentaire système
            if not commentaire_texte:
                commentaire_texte = f"Mot validé par {utilisateur.nom_complet}"
            Commentaire.objects.create(
                mot=mot,
                texte=commentaire_texte,
                auteur=utilisateur
            )
            
            # Ajouter points de contribution pour le modérateur et le contributeur
            Contribution.objects.create(
                utilisateur=utilisateur,
                action="Validation de mot",
                points=3
            )
            
            # Ajouter points au contributeur
            Contribution.objects.create(
                utilisateur=mot.cree_par,
                action="Mot validé",
                points=10
            )
            
            # Notifier l'auteur du mot
            Notification.objects.create(
                utilisateur=mot.cree_par,
                message=f"Votre mot '{mot.nom}' a été validé et ajouté au dictionnaire.",
                lien=f"/mot/{mot.id}/"
            )
            
        elif action == 'rejeter':
            statut.statut = StatutValidation.STATUT_REJETE
            statut.moderateur = utilisateur
            statut.save()
            
            # Ajouter un commentaire avec la raison du rejet
            if commentaire_texte:
                Commentaire.objects.create(
                    mot=mot,
                    texte=f"Mot rejeté - Raison: {commentaire_texte}",
                    auteur=utilisateur
                )
                
            # Points pour le modérateur
            Contribution.objects.create(
                utilisateur=utilisateur,
                action="Rejet de mot",
                points=1
            )
            
            # Notifier l'auteur du mot
            Notification.objects.create(
                utilisateur=mot.cree_par,
                message=f"Votre mot '{mot.nom}' a été rejeté. Consultez les commentaires pour plus d'informations.",
                lien=f"/mot/{mot.id}/"
            )
            
        elif action == 'demander_clarification':
            # Le statut reste en révision
            statut.statut = StatutValidation.STATUT_REVISION
            statut.moderateur = utilisateur
            statut.save()
            
            # Ajouter un commentaire de demande de clarification
            if commentaire_texte:
                Commentaire.objects.create(
                    mot=mot,
                    texte=f"Demande de clarification: {commentaire_texte}",
                    auteur=utilisateur
                )
                
            # Points pour le modérateur
            Contribution.objects.create(
                utilisateur=utilisateur,
                action="Demande de clarification",
                points=1
            )
            
            # Notifier l'auteur du mot
            Notification.objects.create(
                utilisateur=mot.cree_par,
                message=f"Un modérateur demande des clarifications pour votre mot '{mot.nom}'.",
                lien=f"/mot/{mot.id}/"
            )
            
        elif action == 'reprendre_revision':
            # Changer le statut de rejeté à en révision
            statut.statut = StatutValidation.STATUT_REVISION
            statut.moderateur = utilisateur
            statut.save()
            
            # Ajouter un commentaire
            message = "Mot repris en révision"
            if commentaire_texte:
                message += f" - Commentaire: {commentaire_texte}"
                
            Commentaire.objects.create(
                mot=mot,
                texte=message,
                auteur=utilisateur
            )
            
            # Points pour le modérateur
            Contribution.objects.create(
                utilisateur=utilisateur,
                action="Reprise de révision",
                points=2
            )
            
            # Notifier l'auteur du mot
            Notification.objects.create(
                utilisateur=mot.cree_par,
                message=f"Votre mot '{mot.nom}' a été repris en révision.",
                lien=f"/mot/{mot.id}/"
            )
    
    contexte = {
        'mot': mot,
        'statut': statut,
        'definitions': definitions,
        'commentaires': commentaires,
        'moderateurs': moderateurs,
    }
    
    return render(request, 'dictionnaire/examiner_mot.html', contexte)

def ajouter_commentaire(request, mot_id):
    if 'utilisateur_id' not in request.session:
        return redirect('connexion')
        
    utilisateur_id = request.session['utilisateur_id']
    utilisateur = Utilisateur.objects.get(id=utilisateur_id)
    
    mot = get_object_or_404(Mot, id=mot_id)
    
    if request.method == 'POST':
        commentaire_texte = request.POST.get('commentaire')
        if commentaire_texte:
            Commentaire.objects.create(
                mot=mot,
                texte=commentaire_texte,
                auteur=utilisateur
            )
            
            # Ajouter des points pour la contribution
            Contribution.objects.create(
                utilisateur=utilisateur,
                action="Ajout de commentaire",
                points=1
            )
            
            # Notifier l'auteur du mot si ce n'est pas lui qui commente
            if mot.cree_par.id != utilisateur.id:
                Notification.objects.create(
                    utilisateur=mot.cree_par,
                    message=f"{utilisateur.nom_complet} a commenté votre mot '{mot.nom}'.",
                    lien=f"/mot/{mot.id}/"
                )
                
            # Notifier le modérateur responsable si le mot est en révision
            if mot.statut_validation.statut == StatutValidation.STATUT_REVISION and mot.statut_validation.moderateur and mot.statut_validation.moderateur.id != utilisateur.id:
                Notification.objects.create(
                    utilisateur=mot.statut_validation.moderateur,
                    message=f"{utilisateur.nom_complet} a commenté le mot '{mot.nom}' que vous révisez.",
                    lien=f"/mot/{mot.id}/examiner/"
                )
    
    # Rediriger vers la page appropriée selon le rôle de l'utilisateur
    if utilisateur.est_moderateur() or utilisateur.est_administrateur():
        return redirect('examiner_mot', mot_id=mot.id)
    else:
        return redirect('detail_mot', mot_id=mot.id)

def details_mot(request):
    # Vérifier si l'utilisateur est connecté
    if 'utilisateur_id' not in request.session:
        return redirect('connexion')
        
    # Récupérer l'utilisateur
    utilisateur_id = request.session['utilisateur_id']
    try:
        utilisateur = Utilisateur.objects.get(id=utilisateur_id)
        
        # Récupérer TOUS les mots créés par l'utilisateur
        mots = Mot.objects.filter(cree_par=utilisateur)
        
        # Séparer les mots validés et non validés
        mots_valides = []
        mots_non_valides = []
        
        for mot in mots:
            if mot.statut_validation.statut == StatutValidation.STATUT_VALIDE:
                mots_valides.append(mot)
            else:
                mots_non_valides.append(mot)
        
        return render(request, 'dictionnaire/details_mot.html', {
            'mots_non_valides': mots_non_valides,
            'mots_valides': mots_valides,
            'tous_mots': mots,  # Tous les mots pour un affichage complet
        })
    except Utilisateur.DoesNotExist:
        return redirect('connexion')



def filtrer_mots(request):
    """Vue pour filtrer les mots selon différents critères"""
    # Vérifier si l'utilisateur est connecté
    if 'utilisateur_id' not in request.session:
        return redirect('connexion')
        
    # Récupérer l'utilisateur
    utilisateur_id = request.session['utilisateur_id']
    utilisateur = get_object_or_404(Utilisateur, id=utilisateur_id)
    
    # Vérifier si l'utilisateur est modérateur ou administrateur
    if not (utilisateur.est_moderateur() or utilisateur.est_administrateur()):
        return redirect('accueil')
    
    # Récupérer les paramètres de filtrage
    statut = request.GET.get('statut', '')
    date_debut = request.GET.get('date_debut', '')
    date_fin = request.GET.get('date_fin', '')
    moderateur_id = request.GET.get('moderateur', '')
    contributeur_id = request.GET.get('contributeur', '')
    recherche = request.GET.get('recherche', '')
    
    # Base de la requête
    mots_queryset = Mot.objects.all()
    
    # Appliquer les filtres
    if statut:
        mots_queryset = mots_queryset.filter(statut_validation__statut=statut)
    
    if date_debut:
        from django.utils.dateparse import parse_date
        date_debut_obj = parse_date(date_debut)
        if date_debut_obj:
            mots_queryset = mots_queryset.filter(date_creation__gte=date_debut_obj)
    
    if date_fin:
        from django.utils.dateparse import parse_date
        date_fin_obj = parse_date(date_fin)
        if date_fin_obj:
            mots_queryset = mots_queryset.filter(date_creation__lte=date_fin_obj)
    
    if moderateur_id:
        mots_queryset = mots_queryset.filter(statut_validation__moderateur_id=moderateur_id)
    
    if contributeur_id:
        mots_queryset = mots_queryset.filter(cree_par_id=contributeur_id)
    
    if recherche:
        mots_queryset = mots_queryset.filter(nom__icontains=recherche)
    
    # Trier par date de création (plus récent d'abord)
    mots = mots_queryset.order_by('-date_creation')
    
    # Pour les listes déroulantes de filtres
    moderateurs = Utilisateur.objects.filter(role__in=[Utilisateur.ADMIN, Utilisateur.MODERATEUR])
    contributeurs = Utilisateur.objects.filter(role=Utilisateur.CONTRIBUTEUR)
    
    contexte = {
        'mots': mots,
        'moderateurs': moderateurs,
        'contributeurs': contributeurs,
        'statut_selected': statut,
        'date_debut': date_debut,
        'date_fin': date_fin,
        'moderateur_id': moderateur_id,
        'contributeur_id': contributeur_id,
        'recherche': recherche,
        'statuts_choix': StatutValidation.STATUTS_CHOIX,
    }
    
    return render(request, 'dictionnaire/filtrer_mots.html', contexte)

# Gestion des notifications
def notifications(request):
    # Vérifier si l'utilisateur est connecté
    if 'utilisateur_id' not in request.session:
        return redirect('connexion')
        
    # Récupérer l'utilisateur
    utilisateur_id = request.session['utilisateur_id']
    utilisateur = get_object_or_404(Utilisateur, id=utilisateur_id)
    
    # Récupérer toutes les notifications de l'utilisateur
    notifications = Notification.objects.filter(utilisateur=utilisateur).order_by('-date_creation')
    
    # Compter les notifications non lues
    unread_notifications_count = Notification.objects.filter(utilisateur=utilisateur, est_lue=False).count()
    
    return render(request, 'dictionnaire/notifications.html', {
        'notifications': notifications,
        'unread_notifications_count': unread_notifications_count,
    })

def marquer_comme_lue(request, notification_id):
    # Vérifier si l'utilisateur est connecté
    if 'utilisateur_id' not in request.session:
        return redirect('connexion')
        
    # Récupérer l'utilisateur
    utilisateur_id = request.session['utilisateur_id']
    utilisateur = get_object_or_404(Utilisateur, id=utilisateur_id)
    
    # Récupérer la notification
    notification = get_object_or_404(Notification, id=notification_id)
    
    # Vérifier que la notification appartient à l'utilisateur connecté
    if notification.utilisateur == utilisateur:
        notification.est_lue = True
        notification.save()
    
    return redirect('notifications')  

# Administration
@admin_required
def accueil_admin(request):
    if 'utilisateur_id' not in request.session:
        return redirect('connexion')
        
    try:
        utilisateur = Utilisateur.objects.get(id=request.session['utilisateur_id'])
        if not utilisateur.est_administrateur():
            return redirect('accueil')
        
        # Statistiques globales
        total_utilisateurs = Utilisateur.objects.count()
        total_mots = Mot.objects.count()
        mots_valides = Mot.objects.filter(statut_validation__statut=StatutValidation.STATUT_VALIDE).count()
        
        # Calculer les mots en attente
        mots_en_attente = total_mots - mots_valides
        
        # Récupérer les 5 derniers mots ajoutés
        derniers_mots = Mot.objects.all().order_by('-date_creation')[:5]
        
        return render(request, 'dictionnaire/index_admin.html', {
            'total_utilisateurs': total_utilisateurs,
            'total_mots': total_mots,
            'mots_valides': mots_valides,
            'mots_en_attente': mots_en_attente,  # Nouvelle variable calculée
            'derniers_mots': derniers_mots,
            'accueil_url': reverse('accueil')
        })
    except Utilisateur.DoesNotExist:
        return redirect('connexion')

@admin_required
def interface_admin(request):
    return render(request, 'dictionnaire/interface_admin.html')

@admin_required
def gestion_utilisateurs(request):
    # Récupérer tous les utilisateurs sauf l'admin par défaut
    utilisateurs = Utilisateur.objects.exclude(email="Richatt@gmail.com")
    
    return render(request, 'dictionnaire/gestion_utilisateurs.html', {"utilisateurs": utilisateurs})

@admin_required
def modifier_role(request):
    if request.method == "POST":
        utilisateur_id = request.POST.get("utilisateur_id")
        nouveau_role = request.POST.get("nouveau_role")

        utilisateur = get_object_or_404(Utilisateur, id=utilisateur_id)
        
        # Empêcher la modification de l'admin par défaut
        if utilisateur.email.lower() == "richatt@gmail.com":
            return JsonResponse({"success": False, "error": "Impossible de modifier l'administrateur par défaut."})

        if nouveau_role in dict(Utilisateur.ROLE_CHOICES):
            utilisateur.role = nouveau_role
            utilisateur.save()
            return JsonResponse({"success": True, "nouveau_role": utilisateur.get_role_display()})
        
        return JsonResponse({"success": False, "error": "Rôle non valide."})
    
    return JsonResponse({"success": False, "error": "Méthode non autorisée."})








# Pour la vue du tableau de bord modérateur
def tableau_bord_moderateur(request):
    # Vérification que l'utilisateur est connecté et est modérateur
    if not request.session.get('utilisateur_id'):
        messages.error(request, "Vous devez être connecté pour accéder à cette page.")
        return redirect('connexion')
    
    utilisateur = Utilisateur.objects.get(id=request.session['utilisateur_id'])
    if not utilisateur.est_moderateur and not utilisateur.est_administrateur:
        messages.error(request, "Vous n'avez pas les permissions nécessaires pour accéder à cette page.")
        return redirect('accueil')
    
    # Récupération des mots par statut
    mots_en_attente = Mot.objects.filter(statut_validation__statut='attente').order_by('-date_creation')[:5]
    mots_en_revision = Mot.objects.filter(statut_validation__statut='revision').order_by('-statut_validation__date_mise_a_jour')[:5]
    mots_valides = Mot.objects.filter(statut_validation__statut='valide').order_by('-statut_validation__date_mise_a_jour')[:5]
    mots_rejetes = Mot.objects.filter(statut_validation__statut='rejete').order_by('-statut_validation__date_mise_a_jour')[:5]
    
    # Statistiques
    total_attente = Mot.objects.filter(statut_validation__statut='attente').count()
    total_revision = Mot.objects.filter(statut_validation__statut='revision').count()
    total_valides = Mot.objects.filter(statut_validation__statut='valide').count()
    total_rejetes = Mot.objects.filter(statut_validation__statut='rejete').count()
    
    # Pour les administrateurs, ajouter des statistiques supplémentaires
    est_admin = utilisateur.est_administrateur
    
    # Exemple d'activités récentes (à adapter selon votre modèle)
    # Cela pourrait être des entrées de journal, des commentaires récents, etc.
    activites_recentes = []
    
    # Si vous avez un modèle de journal d'activités, vous pourriez faire quelque chose comme:
    # activites_recentes = JournalActivite.objects.all().order_by('-date')[:10]
    
    context = {
        'mots_en_attente': mots_en_attente,
        'mots_en_revision': mots_en_revision,
        'mots_valides': mots_valides,
        'mots_rejetes': mots_rejetes,
        'total_attente': total_attente,
        'total_revision': total_revision,
        'total_valides': total_valides,
        'total_rejetes': total_rejetes,
        'est_admin': est_admin,
        'activites_recentes': activites_recentes,
        'request': request,
    }
    
    return render(request, 'dictionnaire/index_moderateur.html', context)




def calculer_niveau_utilisateur(utilisateur):
    """
    Calcule le niveau actuel de l'utilisateur, sa progression,
    et les informations pour le niveau suivant.
    
    Retourne un dictionnaire avec les informations de niveau.
    """
    total_points = sum(c.points for c in utilisateur.contributions.all())
    
    # Récupérer tous les niveaux triés
    niveaux = Niveau.objects.all().order_by('points_requis')
    
    # Niveau par défaut (si aucun niveau n'est défini dans la BD)
    niveau_actuel = {
        'niveau': 1,
        'titre': 'Débutant',
        'points_actuels': total_points,
        'points_necessaires': 100,
        'pourcentage': min(int((total_points / 100) * 100), 100),
        'niveau_suivant': 2,
        'points_manquants': max(100 - total_points, 0)
    }
    
    # Si aucun niveau n'est défini, retourner le niveau par défaut
    if not niveaux.exists():
        return niveau_actuel
    
    # Chercher le niveau actuel de l'utilisateur
    niveau_precedent = None
    for niveau in niveaux:
        if total_points < niveau.points_requis:
            # On a trouvé le prochain niveau à atteindre
            niveau_suivant = niveau
            
            if niveau_precedent:
                # Calculer la progression entre le niveau précédent et le suivant
                points_necessaires = niveau_suivant.points_requis - niveau_precedent.points_requis
                points_actuels = total_points - niveau_precedent.points_requis
                pourcentage = min(int((points_actuels / points_necessaires) * 100), 100)
                
                return {
                    'niveau': niveau_precedent.niveau,
                    'titre': niveau_precedent.titre,
                    'points_actuels': total_points,
                    'points_necessaires': niveau_suivant.points_requis,
                    'pourcentage': pourcentage,
                    'niveau_suivant': niveau_suivant.niveau,
                    'points_manquants': niveau_suivant.points_requis - total_points
                }
            else:
                # L'utilisateur n'a pas encore atteint le premier niveau
                pourcentage = min(int((total_points / niveau_suivant.points_requis) * 100), 100)
                return {
                    'niveau': 0,
                    'titre': 'Novice',
                    'points_actuels': total_points,
                    'points_necessaires': niveau_suivant.points_requis,
                    'pourcentage': pourcentage,
                    'niveau_suivant': niveau_suivant.niveau,
                    'points_manquants': niveau_suivant.points_requis - total_points
                }
        
        niveau_precedent = niveau
    
    # Si l'utilisateur a dépassé le niveau maximum
    return {
        'niveau': niveau_precedent.niveau,
        'titre': niveau_precedent.titre,
        'points_actuels': total_points,
        'points_necessaires': niveau_precedent.points_requis,
        'pourcentage': 100,
        'niveau_suivant': niveau_precedent.niveau,
        'points_manquants': 0
    }

def verifier_et_attribuer_badges(utilisateur):
    """
    Vérifie si l'utilisateur est éligible à de nouveaux badges 
    en fonction de ses points et contributions
    """
    total_points = sum(c.points for c in utilisateur.contributions.all())
    mots_proposes = Mot.objects.filter(cree_par=utilisateur).count()
    mots_valides = Mot.objects.filter(cree_par=utilisateur, statut_validation__statut='valide').count()
    
    # Récupérer tous les badges disponibles
    badges_disponibles = Badge.objects.filter(special=False)
    
    badges_attribues = []
    
    for badge in badges_disponibles:
        # Vérifier si l'utilisateur a déjà ce badge
        if not BadgeUtilisateur.objects.filter(utilisateur=utilisateur, badge=badge).exists():
            # Vérifier les conditions d'attribution
            if (badge.points_requis <= total_points and 
                badge.mots_requis <= mots_proposes):
                # Attribuer le badge
                BadgeUtilisateur.objects.create(
                    utilisateur=utilisateur,
                    badge=badge
                )
                badges_attribues.append(badge)
    
    return badges_attribues

@login_required
def liste_badges(request):
    utilisateur_id = request.session['utilisateur_id']
    utilisateur = get_object_or_404(Utilisateur, id=utilisateur_id)
    
    # Récupérer tous les badges
    badges = Badge.objects.all()
    
    # Calculer les statistiques de l'utilisateur
    total_points = sum(c.points for c in utilisateur.contributions.all())
    mots_proposes = utilisateur.mots.count()
    
    # Vérifier automatiquement et attribuer de nouveaux badges
    nouveaux_badges = verifier_et_attribuer_badges(utilisateur)
    
    context = {
        'badges': badges,
        'total_points': total_points,
        'mots_proposes': mots_proposes,
        'utilisateur': utilisateur,
    }
    
    return render(request, 'dictionnaire/liste_des_badges.html', context)



@login_required
def profil_utilisateur(request, utilisateur_id=None):
    # Si aucun ID n'est fourni, utiliser l'utilisateur connecté
    if utilisateur_id is None:
        utilisateur_id = request.session['utilisateur_id']
    
    # Récupérer l'utilisateur
    utilisateur = get_object_or_404(Utilisateur, id=utilisateur_id)
    
    # Calculer les statistiques
    total_points = sum(c.points for c in utilisateur.contributions.all())
    mots_proposes = utilisateur.mots.count()
    mots_valides = utilisateur.mots.filter(statut_validation__statut='valide').count()
    
    # Calculer le niveau
    niveau = calculer_niveau_utilisateur(utilisateur)
    
    # Récupérer les badges
    badges = BadgeUtilisateur.objects.filter(utilisateur=utilisateur)
    
    # Récupérer les contributions récentes
    contributions = utilisateur.contributions.order_by('-date_creation')[:10]
    
    # Récupérer les mots récents
    mots = utilisateur.mots.order_by('-date_creation')[:10]
    
    context = {
        'utilisateur': utilisateur,
        'total_points': total_points,
        'mots_proposes': mots_proposes,
        'mots_valides': mots_valides,
        'niveau': niveau,
        'badges': badges,
        'contributions': contributions,
        'mots': mots
    }
    
    return render(request, 'dictionnaire/Profil.html', context)

@login_required
def verifier_badges(request):
    utilisateur_id = request.session['utilisateur_id']
    utilisateur = get_object_or_404(Utilisateur, id=utilisateur_id)
    
    # Vérifier et attribuer des badges
    nouveaux_badges = verifier_et_attribuer_badges(utilisateur)
    
    if nouveaux_badges:
        messages.success(request, f"Félicitations ! Vous avez obtenu {len(nouveaux_badges)} nouveau(x) badge(s).")
    
    return redirect('liste_badges')


def meilleurs_contributeurs(request):
    # Récupérer les contributeurs triés par points
    contributeurs = Utilisateur.objects.annotate(
        total_points=models.Sum('contributions__points', default=0)
    ).order_by('-total_points')
    
    # Préparer des informations supplémentaires pour chaque contributeur
    contributeurs_avec_details = []
    
    for contributeur in contributeurs:
        # Créer un dictionnaire avec les détails du contributeur
        details_contributeur = {
            'id': contributeur.id,
            'nom_complet': contributeur.nom_complet,
            'role': contributeur.role,
            'total_points': contributeur.total_points,
            'mots_proposes': Mot.objects.filter(cree_par=contributeur).count(),
            'mots_valides': Mot.objects.filter(cree_par=contributeur, statut_validation__statut='valide').count(),
            'badges': list(BadgeUtilisateur.objects.filter(utilisateur=contributeur).select_related('badge')),
            'niveau': calculer_niveau_utilisateur(contributeur)['niveau']
        }
        
        contributeurs_avec_details.append(details_contributeur)
    
    # Si l'utilisateur est connecté, récupérer sa position
    rang_utilisateur = 0
    utilisateur = None
    if 'utilisateur_id' in request.session:
        try:
            utilisateur_id = request.session['utilisateur_id']
            utilisateur = Utilisateur.objects.get(id=utilisateur_id)
            # Calculer le rang de l'utilisateur
            for index, contrib in enumerate(contributeurs_avec_details, 1):
                if contrib['id'] == utilisateur.id:
                    rang_utilisateur = index
                    break
        except Utilisateur.DoesNotExist:
            utilisateur = None
    
    context = {
        'contributeurs': contributeurs_avec_details,
        'utilisateur': utilisateur,
        'rang_utilisateur': rang_utilisateur
    }
    
    return render(request, 'dictionnaire/meilleurs_contributeurs.html', context)