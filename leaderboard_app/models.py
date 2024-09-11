from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator


class User(AbstractUser):
    total_score = models.BigIntegerField(default=0, db_index=True)
    level = models.IntegerField(default=1, db_index=True)
    experience_points = models.BigIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    groups = models.ManyToManyField(
        "auth.Group",
        related_name="leaderboard_user_set",
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="leaderboard_user_set",
        blank=True,
    )

    def __str__(self):
        return self.username

    class Meta:
        indexes = [
            models.Index(fields=["total_score", "level"]),
        ]
        ordering = ["-total_score"]


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True)
    country = models.CharField(max_length=100, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    # Automatically create a profile when a user is created
    @staticmethod
    def post_save_user(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)


models.signals.post_save.connect(Profile.post_save_user, sender=User)


class Organisation(models.Model):
    """Represents the organization that starts activities."""

    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Activity(models.Model):
    """Represents an activity or game."""

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=50, db_index=True)
    is_active = models.BooleanField(default=True)
    organisation = models.ForeignKey(
        Organisation, on_delete=models.CASCADE, related_name="activities"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["category"]),
        ]

    def __str__(self):
        return self.name


class ActivitySession(models.Model):
    """Represents a session for a specific activity."""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    score = models.BigIntegerField(default=0)
    experience_gained = models.IntegerField(
        default=0, validators=[MinValueValidator(0)]
    )

    class Meta:
        unique_together = ("user", "activity", "start_time")

    def __str__(self):
        return f"{self.user.username} - {self.activity.name} ({self.start_time})"


class LeaderboardEntry(models.Model):
    """Represents an entry in the leaderboard for an activity."""

    activity = models.ForeignKey(
        Activity, on_delete=models.CASCADE, related_name="leaderboard_entries"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="leaderboard_entries"
    )
    total_score = models.IntegerField(default=0)
    rank = models.IntegerField(null=True, blank=True, db_index=True)

    class Meta:
        unique_together = ("activity", "user")
        ordering = ["rank"]

    def __str__(self):
        return f"{self.rank}: {self.user.username} - {self.total_score}"


class UserGameStats(models.Model):
    """Tracks stats for a user per activity."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="game_stats")
    activity = models.ForeignKey(
        Activity, on_delete=models.CASCADE, related_name="game_stats"
    )
    high_score = models.BigIntegerField(default=0)
    total_score = models.BigIntegerField(default=0)
    games_played = models.IntegerField(default=0)
    current_streak = models.IntegerField(default=0)
    best_streak = models.IntegerField(default=0)
    total_playtime = models.DurationField(default=timezone.timedelta())
    last_played = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("user", "activity")

    def __str__(self):
        return f"{self.user.username} stats for {self.activity.name}"


class Friendship(models.Model):
    """Tracks friendships between users."""

    user = models.ForeignKey(User, related_name="friendships", on_delete=models.CASCADE)
    friend = models.ForeignKey(User, related_name="friends", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "friend")

    def __str__(self):
        return f"{self.user.username} is friends with {self.friend.username}"


class FriendRequest(models.Model):
    """Tracks friend requests sent between users."""

    sender = models.ForeignKey(
        User, related_name="sent_requests", on_delete=models.CASCADE
    )
    recipient = models.ForeignKey(
        User, related_name="received_requests", on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=10,
        choices=[
            ("pending", "Pending"),
            ("accepted", "Accepted"),
            ("rejected", "Rejected"),
        ],
        default="pending",
        db_index=True,
    )

    class Meta:
        unique_together = ("sender", "recipient")

    def __str__(self):
        return f"{self.sender.username} to {self.recipient.username} ({self.status})"


class Tournament(models.Model):
    """Represents a tournament for an activity."""

    name = models.CharField(max_length=100)
    activity = models.ForeignKey(
        Activity, on_delete=models.CASCADE, related_name="tournaments"
    )
    description = models.TextField(blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    max_participants = models.IntegerField(
        default=100, validators=[MinValueValidator(2)]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["start_date", "end_date"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.activity.name})"


class TournamentParticipant(models.Model):
    """Tracks participants in a tournament."""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    score = models.BigIntegerField(default=0)
    rank = models.IntegerField(null=True, blank=True, db_index=True)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "tournament")

    def __str__(self):
        return f"{self.user.username} in {self.tournament.name}"


class Notification(models.Model):
    """Represents a notification sent to users."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="notifications"
    )
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=["-created_at"]),
        ]

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message[:30]}..."
