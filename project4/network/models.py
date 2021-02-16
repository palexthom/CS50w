from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    following = models.ManyToManyField("User", related_name="followers", blank=True, null=True)


class Post(models.Model):
    author = models.ForeignKey("User", on_delete=models.CASCADE, related_name="posts", blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    body = models.TextField(blank=True)
    likes = models.IntegerField(default=0)

    def serialize(self):
        return {
            "id": self.id,
            "author": self.author.username,
            "timestamp": self.timestamp,
            "body": self.body,
            "likes": self.likes
        }