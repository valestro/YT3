from django.db import models
from django.contrib.auth.models import User


class YTSearchQuery(models.Model):
    user = models.ForeignKey(User, default=1, on_delete=models.CASCADE)
    ytQuery = models.CharField(max_length=100, null=True)
    ytQueryUrls = models.CharField(verbose_name='URL', max_length=2000, null=True)
    vidTitle = models.CharField(max_length=100, null=True)
    date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return str(self.ytQuery) + '--' + str(self.user)
