from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    image = models.ImageField(upload_to="user_image/", blank=True, null=True)
    bio = models.TextField(blank=True)
    song = models.FileField(upload_to="music/", blank=True, null=True)
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )


class Follow(models.Model):
    following = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='followers')
    follower = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='following')

    class Meta:
        unique_together = ('follower', 'following')
        verbose_name = 'Follow'
        verbose_name_plural = 'Follows'

    def __str__(self):
        return f"{self.follower} follows {self.following}"

class Comment(models.Model):
    post = models.ForeignKey('Posts', on_delete=models.CASCADE, related_name="comments")
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="Comment")
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Posts(models.Model):
    owner = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name="posts")
    post = models.FileField(upload_to="media/")
    likes = models.ManyToManyField(CustomUser, related_name="liked_posts", blank=True)
    text = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Post by {self.owner.username}"


class Story(models.Model):
    owner = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name="stories")
    story = models.FileField(upload_to="media/")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Story by {self.owner.username}"


class Message(models.Model):
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='received_messages')
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.sender} → {self.receiver}: {self.text[:20]}"
    
class Saved_posts(models.Model):
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="owner")
    posts = models.ForeignKey(Posts, on_delete=models.CASCADE, related_name="posts")

    def __str__(self):
        return f"{self.owner}"
    
class Conversation(models.Model):
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, through="ConvUser")
    updated_at = models.DateTimeField(null=True, blank=True)

class ConvUser(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    unread_count = models.IntegerField(default=0)
    last_seen_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("conversation", "user")
class Messsage(models.Model):
    conversation = models.ForeignKey(Conversation, related_name="messages", on_delete=models.CASCADE)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    body = models.TextField()
    image = models.ImageField(upload_to="chat_images/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
                                     
