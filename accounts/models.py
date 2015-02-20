from django.db import models
from django.contrib.auth.models import User

class SpfUser(models.Model):
	user = models.OneToOneField(User)
	society = models.ForeignKey('society.Society', null=True, on_delete=models.SET_NULL)
