"""
Сериализаторы для преобразования экземпляров моделей в JSON и обратно.
"""
from rest_framework import serializers
from .models import Post, Comment
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели User.
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'date_joined']


class CommentSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Comment с информацией об авторе.
    """
    author = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'content', 'author', 'created_at']
        read_only_fields = ['id', 'author', 'created_at']


class PostSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Post с информацией об авторе и количеством комментариев.
    """
    author = UserSerializer(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'author', 'created_at', 'updated_at', 'comments', 'comments_count']
        read_only_fields = ['id', 'author', 'created_at', 'updated_at', 'comments']

    def get_comments_count(self, obj):
        """Возвращает количество комментариев к посту."""
        return obj.comments.count()