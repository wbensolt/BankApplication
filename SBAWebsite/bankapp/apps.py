import os
from django.apps import AppConfig


class BankappConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "bankapp"

    def ready(self):
            from .views import AuthService
            from django.conf import settings
            import threading
            from django.db import connection

            def run_activation():
                password = os.getenv("DEFAULT_PASSWORD")
                email = os.getenv("EMAIL")
                db = connection
                auth_service = AuthService(db)
                try:
                    response = "er"#auth_service.activate_user_and_fetch_token(email, password)
                    print(response)  # Affichez le résultat dans les logs
                except Exception as e:
                    print(f"Erreur lors de l'activation : {e}")

            # Exécuter la tâche dans un thread séparé pour ne pas bloquer le démarrage
            threading.Thread(target=run_activation).start()