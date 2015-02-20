from django.db import models

class Worker(models.Model):
	society = models.ForeignKey('society.Society', on_delete=models.PROTECT)
	active = models.BooleanField(default=True)
	name = models.CharField(max_length=1000)
	address = models.CharField(max_length=1000)
	account_no = models.CharField(max_length=20, blank=True)
	person_id = models.CharField(max_length=20, blank=True)
	norlonn_number = models.IntegerField(blank=True, null=True, unique=True)

	def __str__(self):
		return self.name + " (" + self.society.shortname + ")"	
