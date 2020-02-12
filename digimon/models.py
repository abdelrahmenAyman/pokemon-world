from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Digimon(models.Model):
    creator = models.ForeignKey(User, related_name='created_digimons', on_delete=models.SET_NULL, null=True)

    name = models.CharField(max_length=75)
    description = models.CharField(max_length=250)
    weight = models.DecimalField(max_digits=4, decimal_places=1)
