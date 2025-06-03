#this is models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta

class User(AbstractUser):
    dark_mode = models.BooleanField(default=False)
    ghost_avatar = models.CharField(max_length=100, default='default-ghost.png')

    class Meta:
        db_table = 'tracker_user'

    def __str__(self):
        return self.username

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    current_streak = models.PositiveIntegerField(default=0)
    longest_streak = models.PositiveIntegerField(default=0)
    total_detox_minutes = models.PositiveIntegerField(default=0)
    last_checkin = models.DateField(null=True, blank=True)
    total_minutes_detoxed = models.FloatField(default=0)
    total_detox_time = models.IntegerField(default=0)
    last_detox_date = models.DateField(null=True, blank=True)

    def update_streak(self):
        today = timezone.now().date()
        if self.last_checkin == today - timedelta(days=1):
            self.current_streak += 1
        elif self.last_checkin != today:
            self.current_streak = 1

        if self.current_streak > self.longest_streak:
            self.longest_streak = self.current_streak

        self.last_checkin = today
        self.save()

    def __str__(self):
        return self.user.username

class ProductiveNote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    note = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Note at {self.created_at}"

class Badge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    awarded_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.name} - {self.user.username}"

class UserBadge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="badges_earned")
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'badge')

class DetoxSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    duration = models.PositiveIntegerField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.end_time and self.start_time:
            self.duration = (self.end_time - self.start_time).total_seconds() / 60
            profile = self.user.userprofile
            profile.total_detox_minutes += self.duration
            profile.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username}'s session"

class DailyCheckIn(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    checked_in = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'date')

    def __str__(self):
        return f"{self.user.username} - {self.date}: {'✓' if self.checked_in else '✗'}"
