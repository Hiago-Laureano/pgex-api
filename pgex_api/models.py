from django.db import models
from django.utils import timezone
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin

class CustomUserManager(BaseUserManager):
    def _create_user(self, email, password, first_name, last_name, **extra_fields):
        if not email:
            raise ValueError("The given username must be set")
        if not password:
            raise ValueError("The given password must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, first_name=first_name, last_name=last_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password, first_name, last_name, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, first_name, last_name, **extra_fields)

    def create_superuser(self, email, password, first_name, last_name, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self._create_user(email, password, first_name, last_name, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, max_length=255)

    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)

    date_joined = models.DateTimeField(default=timezone.now)

    objects = CustomUserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['first_name', 'last_name']

    @property
    def last_login_date(self):
        if self.last_login:
            return self.last_login.strftime("%d/%m/%Y %H:%M:%S")
        return self.last_login
    @property
    def joined(self):
        return self.date_joined.strftime("%d/%m/%Y %H:%M:%S")

    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"

    def __str__(self):
        return f"{self.id} | {self.first_name} | {self.email}"

class Base(models.Model):
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)

    @property
    def created(self):
        return self.created_at.strftime("%d/%m/%Y %H:%M:%S")

    @property
    def updated(self):
        return self.updated_at.strftime("%d/%m/%Y %H:%M:%S")

    class Meta:
        abstract = True

class Survey(Base):
    name = models.CharField(max_length = 255, unique = True)
    questions = models.JSONField() #JSON with body == {'*your title for this list of question*': [{'id': 1, 'question': 'text', 'is_descriptive': false}, ...]}
    n_questions = models.IntegerField()
    active = models.BooleanField(default = True)
    active_until = models.DateTimeField(null = True)

class Response(Base):
    responses = models.JSONField() # JSON with body == {1: 5, 2: "text"} keys are ids of questions
    survey = models.ForeignKey(Survey, on_delete = models.CASCADE, related_name = "responses")