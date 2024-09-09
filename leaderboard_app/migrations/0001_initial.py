# Generated by Django 5.1.1 on 2024-09-09 03:08

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Achievement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField()),
                ('criteria', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('create_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Leaderboard',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('game', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='leaderboard', to='leaderboard_app.game')),
            ],
        ),
        migrations.CreateModel(
            name='LeaderboardEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_score', models.IntegerField(default=0)),
                ('rank', models.IntegerField()),
                ('leaderboard', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='leaderboard_entries', to='leaderboard_app.leaderboard')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['rank'],
                'unique_together': {('leaderboard', 'user')},
            },
        ),
        migrations.AddField(
            model_name='leaderboard',
            name='entries',
            field=models.ManyToManyField(through='leaderboard_app.LeaderboardEntry', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='Score',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.IntegerField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('is_verified', models.BooleanField(default=False)),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='scores', to='leaderboard_app.game')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='scores', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-score', '-timestamp'],
                'unique_together': {('user', 'game', 'timestamp')},
            },
        ),
        migrations.CreateModel(
            name='UserAchievement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_earned', models.DateTimeField(auto_now_add=True)),
                ('achievement', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_achievements', to='leaderboard_app.achievement')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='achievements', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'achievement')},
            },
        ),
    ]
