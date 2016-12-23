from django.db import models


class NorlonnReport(models.Model):
    date = models.DateField()

    def __str__(self):
        return str(self.date)

    class Meta:
        permissions = (
            ('generate_report', 'Can generate norlønn report'),
            ('view_report', 'Can view norlønn reports'),
        )
