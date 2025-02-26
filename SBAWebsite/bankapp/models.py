from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone
from django.db import models

###### User Model and assigned roles 

class UserManager(BaseUserManager):
    """
    Custom User Manager to handle user creation and superuser creation.
    Automatically assigns roles:
        - 'advisor' for superusers
        - 'client' for all other users
    """
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        extra_fields.setdefault('role', 'client')  # Default role is client
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'advisor')  # Superusers are advisors
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    ROLE_CHOICES = (
        ('client', 'Client'),
        ('advisor', 'Conseiller Bancaire'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    email = models.EmailField(unique=True)  # Email as unique identifier

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']  # Keep username for compatibility

    objects = UserManager()

    def save(self, *args, **kwargs):
        # Assign role based on superuser status
        if self.is_superuser:
            self.role = 'advisor'
        elif not self.role:
            self.role = 'client'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.email} ({self.role})"
    

#Pairing advisors to clients 
from django.contrib.auth import get_user_model
from django.db.models import Count
from random import choice

User = get_user_model()

class AdvisorClientPairing(models.Model):
    """
    Advisor-Client Pairing Model
    - Stores the advisor-client relationships.
    - Ensures only clients are assigned advisors.
    """
    client = models.OneToOneField(User, on_delete=models.CASCADE, related_name='advisor_pairing')
    advisor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='clients')

    def __str__(self):
        return f"{self.client.email} paired with {self.advisor.email}"

    @classmethod
    def assign_advisor(cls, client):
        """
        Assigns an advisor to the client using round-robin strategy.
        - Only assigns advisors to clients (not other advisors).
        """
        advisors = User.objects.filter(role='advisor').annotate(client_count=Count('clients')).order_by('client_count')
        return advisors.first() if advisors.exists() else None

    @classmethod
    def auto_assign(cls, client):
        """
        Automatically assigns an advisor to the client upon registration.
        """
        if client.role == 'client' and not cls.objects.filter(client=client).exists():
            assigned_advisor = cls.assign_advisor(client)
            if assigned_advisor:
                cls.objects.create(client=client, advisor=assigned_advisor)



###### Messages 

User = get_user_model()

class Conversation(models.Model):
    """
    Conversation Model
    - Manages chat sessions between a client and an advisor.
    - Each conversation is unique to a client-advisor pair.
    """
    client = models.ForeignKey(User, related_name='client_conversations', on_delete=models.CASCADE)
    advisor = models.ForeignKey(User, related_name='advisor_conversations', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Conversation between {self.client} and {self.advisor}"

class Message(models.Model):
    """
    Message Model
    - Stores individual messages within a conversation.
    - Messages can be sent by either the client or the advisor.
    """
    conversation = models.ForeignKey(Conversation, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Message from {self.sender} at {self.timestamp}"
    

###### News 

#News model 
class NewsArticle(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to='news_images/', blank=True, null=True)
    published_date = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    @property
    def excerpt(self):
        return self.content[:100] + '...' if len(self.content) > 100 else self.content


class TokenModel(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.TextField()
    expires_at = models.DateTimeField()