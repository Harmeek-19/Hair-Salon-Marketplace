from django.db import models
from django.conf import settings

class AdminDashboardSetting(models.Model):
    user = models.OneToOneField('authentication.User', on_delete=models.CASCADE)
    preferred_view = models.CharField(max_length=50, default='summary')
    show_quick_actions = models.BooleanField(default=True)
    show_recent_activities = models.BooleanField(default=True)

    def __str__(self):
        return f"Admin Dashboard Settings for {self.user.username}"