from django.shortcuts import get_object_or_404
from .models import Utilisateur, Notification

def unread_notifications_count(request):
    """Ajoute le compteur de notifications non lues au contexte de tous les templates."""
    if 'utilisateur_id' in request.session:
        try:
            utilisateur_id = request.session['utilisateur_id']
            utilisateur = get_object_or_404(Utilisateur, id=utilisateur_id)
            count = Notification.objects.filter(utilisateur=utilisateur, est_lue=False).count()
            return {'unread_notifications_count': count}
        except:
            return {'unread_notifications_count': 0}
    return {'unread_notifications_count': 0}