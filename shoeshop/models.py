from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)
    address = models.CharField(max_length=50)

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)

class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.FloatField(default=0.0)
    size = models.FloatField()
    colour = models.CharField(max_length=200)

class Cart(models.Model):
    user = models.ForeignKey(User)
    product = models.ForeignKey(Product)
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.FloatField(default=0.0)