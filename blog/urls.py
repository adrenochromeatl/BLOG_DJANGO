"""
URL routes для приложения блога.
"""
from django.urls import path
from . import views
from .views import (
    PostListView, PostDetailView, PostCreateView,
    PostUpdateView, PostDeleteView,
    PostListAPI, PostDetailAPI, CommentListAPI
)

urlpatterns = [
    # Web interface URLs
    path('', PostListView.as_view(), name='post-list'),
    path('post/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('post/new/', PostCreateView.as_view(), name='post-create'),
    path('post/<int:pk>/update/', PostUpdateView.as_view(), name='post-update'),
    path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='post-delete'),
    path('post/<int:pk>/comment/', views.add_comment, name='add-comment'),
    path('comment/<int:pk>/delete/', views.delete_comment, name='delete-comment'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),

    # API endpoints
    path('api/posts/', PostListAPI.as_view(), name='api-post-list'),
    path('api/posts/<int:pk>/', PostDetailAPI.as_view(), name='api-post-detail'),
    path('api/posts/<int:post_id>/comments/', CommentListAPI.as_view(), name='api-comment-list'),
]