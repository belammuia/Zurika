from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models
from auditlog.registry import auditlog
from django.core.validators import RegexValidator

phone_validator = RegexValidator(
    regex=r'^\+?\d{9,13}$',
    message="Enter a valid Kenyan number (e.g., 0712345678 or +254712345678)."
)



class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_custom_staff(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("is_active", True)
        return self.create_user(email, password, **extra_fields)


    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("role", "admin")

        if extra_fields["is_staff"] is not True:
            raise ValueError("Superuser must have is_staff=True")

        if extra_fields["is_superuser"] is not True:
            raise ValueError("Superuser must have is_superuser=True")

        return self.create_user(email, password, **extra_fields)



class User(AbstractBaseUser, PermissionsMixin):
    class Role(models.TextChoices):
        CLIENT = "client", "Client"
        OFFICER = "claims_officer", "Claims Officer"
        SENIOR_OFFICER = "senior_officer", "Senior Claims Officer"
        ADMIN = "admin", "Administrator"

    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=20, choices=Role.choices, default=Role.CLIENT, db_index=True
    )
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)


    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    ROLE_HIERARCHY = {
        Role.CLIENT: 1,
        Role.OFFICER: 2,
        Role.SENIOR_OFFICER: 3,
        Role.ADMIN: 4
    }

    objects = UserManager()

    def __str__(self):
        return self.email

    @property
    def role_rank(self):
        return self.ROLE_HIERARCHY.get(self.role, 0)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")

    first_name = models.CharField(max_length=65, db_index=True)
    last_name = models.CharField(max_length=65, db_index=True)
    phone_number = models.CharField(validators=[phone_validator], max_length=15, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        super().clean()
        
        if not self.phone_number:
            return
            
        num = self.phone_number.strip().lstrip('+')
        
        if num.startswith('0'):
            self.phone_number = "254" + num[1:]
            
        elif (num.startswith('7') or num.startswith('1')) and len(num) == 9:
            self.phone_number = "254" + num
            
        else:
            self.phone_number = num

    def save(self, *args, **kwargs):
        self.full_clean()  
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.user_id})"
    


class OfficerProfile(models.Model):
    class Availability(models.TextChoices):
        AVAILABLE = "available", "Available"
        BUSY = "busy", "Busy"

    officer = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="officer_profile",
    )
    availability = models.CharField(
        max_length=10,
        choices=Availability.choices,
        default=Availability.AVAILABLE,
    )

    first_name = models.CharField(max_length=65, default="")
    last_name = models.CharField(max_length=65, default="")

    def __str__(self):
        return f"{self.officer.email} - {self.availability}"

auditlog.register(
    User,
    include_fields=[
        "email",
        "role",
        "is_active",
        "is_staff",
    ],
)

auditlog.register(
    Profile,
    include_fields=[
        "first_name",
        "last_name",
    ],
)