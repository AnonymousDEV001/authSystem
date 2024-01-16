from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

# Create your models here.


class CustomAccountManager(BaseUserManager):

    def create_superuser(self, email, first_name, password, **other_fields):

        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)
        other_fields.setdefault('is_active', True)

        if other_fields.get('is_staff') is not True:
            raise ValueError(
                'Superuser must be assigned to is_staff=True.')
        if other_fields.get('is_superuser') is not True:
            raise ValueError(
                'Superuser must be assigned to is_superuser=True.')

        return self.create_user(email, first_name, password, **other_fields)

    def create_user(self, email, first_name, password, **other_fields):

        if not email:
            raise ValueError(_('You must provide an email address'))

        email = self.normalize_email(email)
        user = self.model(email=email,
                          first_name=first_name, **other_fields)
        user.set_password(password)
        user.save()
        return user
    

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(verbose_name='email address', unique=True)
    # username = models.CharField(max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    provider = models.CharField(max_length=100, default="email")
    last_login = models.DateTimeField(null=True, blank=True)
    date_joined = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = CustomAccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.email
    

class social_auth(models.Model):
    foreignKey = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='oauth_access_tokens')
    email = models.EmailField(unique=True)
    access_token = models.TextField()
    provider = models.CharField(max_length=100)

    def __str__(self):
        return self.email


