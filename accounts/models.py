from django.contrib.auth.models import User
from django.db import models


class SpfUser(models.Model):
    user = models.OneToOneField(User)
    society = models.ForeignKey('society.Society', null=True, on_delete=models.SET_NULL)
