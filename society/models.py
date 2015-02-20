from django.db import models


class Society(models.Model):
	name = models.CharField(max_length=100)
	shortname = models.CharField(max_length=10)
	invoice_email = models.EmailField(default="")
	default_wage = models.DecimalField(max_digits=10, decimal_places=2)

	def __str__(self):
		return self.shortname
