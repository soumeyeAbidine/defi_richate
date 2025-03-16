import sys
from django.apps import AppConfig
from django.db import OperationalError, ProgrammingError


class DictionnaireConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dictionnaire'
    def ready(self):
        if "runserver" not in sys.argv: 
            return

        from .models import Utilisateur
        try:
            Utilisateur.create_default_admin()
        except (OperationalError, ProgrammingError):
            pass