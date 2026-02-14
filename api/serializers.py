from rest_framework import serializers
import Instagram.models as models

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CustomUser
        fields = ('first_name', 'last_name', 'username', 'email', 'password1', 'password2')

class PostsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Posts
        fields = ("post", "text")

class StorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Story
        fields = ("story", "text")

class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.StringRelatedField()
    receiver = serializers.StringRelatedField()

    class Meta:
        model = models.Message
        fields = ['id', 'sender', 'receiver', 'text', 'timestamp']