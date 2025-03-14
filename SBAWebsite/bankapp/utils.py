import datetime
from .views import AuthService
import os
from django.db import connection
from django.contrib.auth.hashers import make_password, check_password
from django.utils.timezone import now
from dotenv import load_dotenv
from bankapp.models import User

def get_jwt_token():
    load_dotenv()

    # Ensure correct DB connection
    db = connection

    # Fetch user details from .env
    password = os.getenv("DEFAULT_PASSWORD")
    email = os.getenv("EMAIL")
    usern = os.getenv("USERNAME_")  # Explicitly fetch username
    first_name = os.getenv("FIRST_NAME", "DefaultFirstName")
    last_name = os.getenv("LAST_NAME", "DefaultLastName")
    role = os.getenv("ROLE", "user")
    is_superuser = 0
    is_staff = 0
    is_active = 1
    date_joined = now()

    print(f"🔍 Checking user: {usern} ({email})")

    try:
        # Check if user exists by both email and username
        user = User.objects.filter(username=usern, email=email).first()

        if user:
            print(f"✅ User already exists: {user.email}")

            # Check if password matches
            if not check_password(password, user.password):
                print("⚠️ Password mismatch. Using stored password.")
                password = user.password  # Use existing password for token retrieval

        else:
            print("⚠️ User does not exist, creating...")
            user = User.objects.create(
                email=email,
                username=usern,
                first_name=first_name,
                last_name=last_name,
                password=make_password(password),  # Secure password hashing
                is_superuser=is_superuser,
                is_staff=is_staff,
                is_active=is_active,
                date_joined=date_joined,
                role=role,
            )
            print(f"✅ Created new user: {user.email}")

        # Activate user and fetch token
        auth_service = AuthService(db)
        response = auth_service.activate_user_and_fetch_token(email, password)
        return response.get("access_token", None)

    except Exception as e:
        print(f"❌ Error in get_jwt_token: {e}")
        return None
