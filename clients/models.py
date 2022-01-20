from PIL import ImageDraw
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import F
from django.db.models.functions import Radians, Sin, Power, Cos, ATan2, Sqrt
from imagekit.models import ProcessedImageField


class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifier
    for authentication instead of username.
    """

    def create_user(self, email, password, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(email, password, **extra_fields)

    def get_users_within_distance(self, origin_lat, origin_long, max_distance):
        user_lat = F('latitude')
        user_long = F('longitude')
        earth_radius = 6371

        delta_lat = Radians(user_lat - origin_lat)
        delta_long = Radians(user_long - origin_long)

        a = Power(Sin(delta_lat/2), 2) + Cos(Radians(origin_lat)) * Cos(Radians(user_lat)) * Power(Sin(delta_long / 2), 2)
        c = 2 * ATan2(Sqrt(a), Sqrt(1-a))
        d = earth_radius * c

        return self.annotate(distance=d).filter(distance__lt=max_distance)


class Watermark(object):
    @staticmethod
    def process(image):
        draw = ImageDraw.Draw(image)
        draw.line((0, 0) + image.size, fill=128)
        draw.line((0, image.size[1], image.size[0], 0), fill=128)
        return image


class Client(AbstractUser):
    GENDER_CHOICES = [("M", "Male"), ("F", "Female"), ("O", "Others")]

    username = None
    first_name = models.CharField(null=False, blank=False, max_length=150)
    last_name = models.CharField(null=False, blank=False, max_length=150)
    email = models.EmailField(unique=True)
    avatar = ProcessedImageField(upload_to='avatars', processors=[Watermark()])
    gender = models.CharField(choices=GENDER_CHOICES, max_length=1)
    liked = models.ManyToManyField('self', symmetrical=False)
    latitude = models.DecimalField(max_digits=6, decimal_places=3)
    longitude = models.DecimalField(max_digits=6, decimal_places=3)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['latitude', 'longitude']
    objects = CustomUserManager()
