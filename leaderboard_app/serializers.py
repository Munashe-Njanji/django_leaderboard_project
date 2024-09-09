from django.contrib.auth.models import User
from rest_framework import serializers
from .models import (
    Game,
    Score,
    Leaderboard,
    LeaderboardEntry,
    Achievement,
    UserAchievement,
)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "password"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class GameSerializer(serializers.ModelSerializer):
    leaderboard = LeaderboardSerializer(read_only=True)

    class Meta:
        model = Game
        fields = ["id", "name", "description", "created_at", "leaderboard"]
        read_only_fields = ["created_at"]


class ScoreSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Score
        fields = ["id", "game", "user", "score", "timestamp", "is_verified"]
        read_only_fields = ["timestamp", "user"]

    def create(self, validated_data):
        game = validated_data.get("game")
        score = validated_data.get("score")
        user = self.context["request"].user
        return Score.objects.create(game=game, score=score, user=user)


class LeaderboardSerializer(serializers.ModelSerializer):
    entries = LeaderboardEntrySerializer(many=True, read_only=True)
    game_name = serializers.CharField(source="game.name", read_only=True)

    class Meta:
        model = Leaderboard
        fields = ["id", "game", "game_name", "entries"]


class LeaderboardEntrySerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = LeaderboardEntry
        fields = ["id", "user", "total_score", "rank"]


class AchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Achievement
        fields = ["id", "name", "description", "criteria", "created_at"]
        read_only_fields = ["created_at"]


class UserAchievementSerializer(serializers.ModelSerializer):
    achievement = AchievementSerializer(read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserAchievement
        fields = ["id", "user", "achievement", "date_earned"]
        read_only_fields = ["date_earned", "user"]
