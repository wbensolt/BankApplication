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

<<<<<<< HEAD
import os
import datetime
import pyodbc
from django.contrib.auth.hashers import make_password
from django.utils.crypto import get_random_string
from dotenv import load_dotenv

def generate_token():
    return get_random_string(length=32)  # Génère un token aléatoire de 32 caractères

import os
import datetime
import pyodbc
from django.contrib.auth.hashers import make_password
from django.utils.crypto import get_random_string
from dotenv import load_dotenv

def generate_token():
    return get_random_string(length=32)  # Génère un token aléatoire de 32 caractères

def get_jwt_token():
    # Charger les variables d'environnement
    load_dotenv()

    # Récupérer les variables d'environnement pour la connexion à Azure SQL Database
    db_host = os.getenv("serverdj_")  # Serveur Azure SQL
    db_name = os.getenv("databasedj_")  # Nom de la base de données
    db_user = os.getenv("usernamedj_")  # Nom d'utilisateur
    db_password = os.getenv("passworddj_")  # Mot de passe
    db_driver = os.getenv("driverdj_").replace("+", " ")  # Driver ODBC (remplace les "+" par des espaces)

    # Connexion à Azure SQL Database
    conn_str = f"DRIVER={{{db_driver}}};SERVER={db_host};DATABASE={db_name};UID={db_user};PWD={db_password}"
    try:
        conn = pyodbc.connect(conn_str)
        print("Connexion à la base de données réussie.", flush=True)
    except pyodbc.Error as e:
        print(f"Erreur de connexion à la base de données : {e}", flush=True)
        return None

    cursor = conn.cursor()

    # Récupérer les valeurs depuis le fichier .env
    password = make_password(os.getenv("DEFAULT_PASSWORD"))  # Hacher le mot de passe
    usern = os.getenv("username_")
    email = os.getenv("EMAIL")
    is_superuser = 0  # Valeur par défaut (False)
    is_staff = 0  # Ajout de is_staff pour éviter d'autres erreurs
    first_name = os.getenv("FIRST_NAME", "Admin")  # Valeur par défaut pour first_name
    last_name = os.getenv("last_name", "Admin")  # Valeur par défaut pour last_name
    date_joined = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Date d'inscription actuelle
    role = os.getenv("ROLE", "user")  # Ajout du rôle par défaut
    is_active = 1  # L'utilisateur est actif par défaut

    print("Informations de l'utilisateur :", usern, password, email, flush=True)

=======

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
>>>>>>> d8f83e11fd7befe26bf988b9beb356f3f201c912
    try:
        # Vérifier si l'utilisateur existe déjà
        cursor.execute("SELECT id FROM bankapp_user WHERE username = ? AND email = ?", (usern, email))
        user = cursor.fetchone()

        if user:
            user_id = user[0]
<<<<<<< HEAD
            print("Utilisateur existant trouvé. ID :", user_id, flush=True)
=======
>>>>>>> d8f83e11fd7befe26bf988b9beb356f3f201c912
        else:
            # Insérer l'utilisateur s'il n'existe pas
            cursor.execute(
                """INSERT INTO bankapp_user 
                (username, email, password, first_name, last_name, is_superuser, is_staff, is_active, date_joined, role) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (usern, email, password, first_name, last_name, is_superuser, is_staff, is_active, date_joined, role)
            )
            conn.commit()
<<<<<<< HEAD

            # Récupérer l'ID du dernier enregistrement inséré
            cursor.execute("SELECT SCOPE_IDENTITY()")
            user_id = cursor.fetchone()[0]

            if not user_id:
                print("Erreur : L'utilisateur n'a pas été inséré.", flush=True)
                return None
            else:
                print("Utilisateur inséré avec succès. ID :", user_id, flush=True)

            # Activer l'utilisateur et récupérer le token
=======
            user_id = cursor.lastrowid  # Récupérer l'ID du nouvel utilisateur
>>>>>>> d8f83e11fd7befe26bf988b9beb356f3f201c912
            from django.db import connection
            db = connection
            auth_service = AuthService(db)
            try:
<<<<<<< HEAD
                response = auth_service.activate_user_and_fetch_token(email, os.getenv("DEFAULT_PASSWORD"))
                print("Réponse de l'activation :", response, flush=True)  # Affichez le résultat dans les logs
            except Exception as e:
                print(f"Erreur lors de l'activation : {e}", flush=True)
=======
                response = auth_service.activate_user_and_fetch_token(email, password)
                print(response)  # Affichez le résultat dans les logs
            except Exception as e:
                print(f"Erreur lors de l'activation : {e}")
>>>>>>> d8f83e11fd7befe26bf988b9beb356f3f201c912

        # Récupérer le token de l'utilisateur
        cursor.execute("SELECT token FROM bankapp_tokenmodel WHERE user_id = ?", (user_id,))
        token = cursor.fetchone()

        if token:
<<<<<<< HEAD
            print(f"Token récupéré : {token[0]}", flush=True)
            return token[0]
        else:
            # Générer et insérer un nouveau token
            new_token = generate_token()
            expires_at = datetime.datetime.now() + datetime.timedelta(days=1)  # Expiration dans 1 jour
            cursor.execute(
                "INSERT INTO bankapp_tokenmodel (user_id, token, expires_at) VALUES (?, ?, ?)",
                (user_id, new_token, expires_at)
            )
            conn.commit()
            print(f"Nouveau token généré et inséré : {new_token}", flush=True)
            return new_token

    except Exception as e:
        print(f"Erreur lors de la récupération ou de l'insertion du token : {e}", flush=True)
        return None
    finally:
        cursor.close()
=======
            print(f"Token récupéré : {token[0]}")
            return token[0]
        else:
            print("Aucun token trouvé pour cet utilisateur.")
            return None

    except sqlite3.Error as e:
        print(f"Erreur SQLite : {e}")
        return None

    finally:
>>>>>>> d8f83e11fd7befe26bf988b9beb356f3f201c912
        conn.close()