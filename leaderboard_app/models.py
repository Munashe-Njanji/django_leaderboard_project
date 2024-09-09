from django.contrib.auth.models import User
from django.db import models


class Game(models.Model):
    """Represents a game in the leaderboard system."""

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    create_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        self.name


class Score(models.Model):
    """Tracks scores submitted by users for specific games."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="scores")
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="scores")
    score = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    class Meta:
        unique_together = ("user", "game", "timestamp")
        ordering = ["-score", "-timestamp"]

    def __str__(self) -> str:
        return f"{self.user.username}: {self.score} in {self.game.name}"


class Leaderboard(models.Model):
    """Represents the leaderboard for a specific game."""

    game = models.OneToOneField(
        Game, on_delete=models.CASCADE, related_name="leaderboard"
    )
    entries = models.ManyToManyField(User, through="LeaderboardEntry")


class LeaderboardEntry(models.Model):
    """Represents an entry in the leaderboard for a user."""

    leaderboard = models.ForeignKey(
        Leaderboard, on_delete=models.CASCADE, related_name="leaderboard_entries"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_score = models.IntegerField(default=0)
    rank = models.IntegerField()

    class Meta:
        unique_together = ("leaderboard", "user")
        ordering = ["rank"]

    def __str__(self):
        return f"{self.rank}: {self.user.username} - {self.total_score} in {self.leaderboard.game.name}"


class Achievement(models.Model):
    """Represents achievements that users can earn."""

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    criteria = models.TextField()  # Criteria for earning the achievement
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class UserAchievement(models.Model):
    """Tracks achievements earned by users."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="achievements"
    )
    achievement = models.ForeignKey(
        Achievement, on_delete=models.CASCADE, related_name="user_achievements"
    )
    date_earned = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "achievement")

    def __str__(self):
        return f"{self.user.username} earned {self.achievement.name}"
