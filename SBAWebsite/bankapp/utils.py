import datetime
from django.utils import timezone

from .views import AuthService
from .models import TokenModel
import requests
from django.conf import settings
from django.contrib import messages


def get_service_account_token():
    """
    Retrieves a service account token from the database or fetches a new one if expired.
    """
    # Check if token exists and is not expired
    token_obj = TokenModel.objects.filter(user__is_superuser=True).first()

    if token_obj and token_obj.expires_at > timezone.now():
        print("✅ Using cached service account token.")
        return token_obj.token
    
    # ✅ Hardcoded credentials for testing
    email = "Antoine.SecureBank@test.com"  # Replace with your service account email
    password = "motdepassefort"             # Replace with your service account password

    # If no token or expired, request a new one using hardcoded service account credentials
    try:
        response = requests.post(
            "http://localhost:8001/auth/login",  # Adjust FastAPI URL if needed
            json={
                "email": email,
                "password": password
            }
        )
        response.raise_for_status()  # Raise error for bad status
        token_data = response.json()

        # Save the new token and expiration
        token_obj, created = TokenModel.objects.update_or_create(
            user=None,  # Not linked to a specific user
            defaults={
                "token": token_data.get("access_token"),
                "expires_at": timezone.now() + timezone.timedelta(seconds=129600)  # 3 days availability
            }
        )

        print("✅ New service account token retrieved and stored.")
        return token_obj.token

    except requests.exceptions.RequestException as e:
        print(f"Token Retrieval Error: {str(e)}")
        return None


import sqlite3
import os
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env


def get_jwt_token():
    load_dotenv()
    db_path = os.getenv("DB_PATH", "db.sqlite3")  # Utilise la valeur du .env ou "db.sqlite3" par défaut
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Récupérer les valeurs depuis le fichier .env
    password = os.getenv("DEFAULT_PASSWORD")
    usern = os.getenv("username_")
    email = os.getenv("EMAIL")
    is_superuser = 0  # Valeur par défaut (False en SQLite)
    is_staff = 0  # Ajout de is_staff pour éviter d'autres erreurs
    first_name = os.getenv("FIRST_NAME")  # Valeur par défaut pour first_name
    last_name = os.getenv("LAST_NAME")  # Valeur par défaut pour last_name
    date_joined = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Date d'inscription actuelle
    role = os.getenv("ROLE", "user")  # Ajout du rôle par défaut
    is_active = 1  # L'utilisateur est actif par défaut
    print("userrrrrr",usern, password,email)
    try:
        # Vérifier si l'utilisateur existe déjà
        cursor.execute("SELECT id FROM bankapp_user WHERE username = ? AND email = ?", (usern, email))
        user = cursor.fetchone()

        if user:
            user_id = user[0]
        else:
            # Insérer l'utilisateur s'il n'existe pas
            cursor.execute(
                """INSERT INTO bankapp_user 
                (username, email, password, first_name, last_name, is_superuser, is_staff, is_active, date_joined, role) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (usern, email, password, "first_name", "last_name", is_superuser, is_staff, is_active, date_joined, role)
            )
            conn.commit()
            user_id = cursor.lastrowid  # Récupérer l'ID du nouvel utilisateur
            from django.db import connection
            db = connection
            auth_service = AuthService(db)
            try:
                response = auth_service.activate_user_and_fetch_token(email, password)
                print(response)  # Affichez le résultat dans les logs
            except Exception as e:
                print(f"Erreur lors de l'activation : {e}")

        # Récupérer le token de l'utilisateur
        cursor.execute("SELECT token FROM bankapp_tokenmodel WHERE user_id = ?", (user_id,))
        token = cursor.fetchone()

        if token:
            print(f"Token récupéré : {token[0]}")
            return token[0]
        else:
            print("Aucun token trouvé pour cet utilisateur.")
            return None

    except sqlite3.Error as e:
        print(f"Erreur SQLite : {e}")
        return None

    finally:
        conn.close()