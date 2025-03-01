from django.utils import timezone
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

