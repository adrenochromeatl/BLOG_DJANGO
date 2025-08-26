"""
Представления для приложения блога, включая CRUD операции и API endpoints.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth import login
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from rest_framework import generics, permissions
from .models import Post, Comment
from .forms import PostForm, CommentForm, UserRegisterForm
from .serializers import PostSerializer, CommentSerializer


def register(request):
    """
    Обработка регистрации пользователя.
    """
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Аккаунт успешно создан!')
            return redirect('post-list')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = UserRegisterForm()

    return render(request, 'register.html', {'form': form})


class PostListView(ListView):
    """
    Отображение paginated списка всех постов блога.
    """
    model = Post
    template_name = 'post_list.html'
    context_object_name = 'posts'
    paginate_by = 5
    ordering = ['-created_at']


class PostDetailView(DetailView):
    """
    Отображение отдельного поста блога с комментариями и формой комментария.
    """
    model = Post
    template_name = 'post_detail.html'

    def get_context_data(self, **kwargs):
        """Добавляет форму комментария в контекст."""
        context = super().get_context_data(**kwargs)
        context['comment_form'] = CommentForm()
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    """
    Создание нового поста блога (требует авторизации).
    """
    model = Post
    form_class = PostForm
    template_name = 'post_form.html'

    def form_valid(self, form):
        """Устанавливает автора поста перед сохранением."""
        form.instance.author = self.request.user
        messages.success(self.request, 'Пост успешно создан!')
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UpdateView):
    """
    Обновление существующего поста блога (требует авторизации и владения).
    """
    model = Post
    form_class = PostForm
    template_name = 'post_form.html'

    def dispatch(self, request, *args, **kwargs):
        """Проверяет, является ли пользователь автором поста."""
        obj = self.get_object()
        if obj.author != self.request.user:
            messages.error(request, 'Вы можете редактировать только свои посты.')
            return redirect('post-detail', pk=obj.pk)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """Показывает сообщение об успешном обновлении."""
        messages.success(self.request, 'Пост успешно обновлен!')
        return super().form_valid(form)


class PostDeleteView(LoginRequiredMixin, DeleteView):
    """
    Удаление поста блога (требует авторизации и владения).
    """
    model = Post
    template_name = 'post_confirm_delete.html'
    success_url = '/'

    def dispatch(self, request, *args, **kwargs):
        """Проверяет, является ли пользователь автором поста."""
        obj = self.get_object()
        if obj.author != self.request.user:
            messages.error(request, 'Вы можете удалять только свои посты.')
            return redirect('post-detail', pk=obj.pk)
        return super().dispatch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        """Показывает сообщение об успешном удалении."""
        messages.success(request, 'Пост успешно удален!')
        return super().delete(request, *args, **kwargs)


@login_required
def add_comment(request, pk):
    """
    Добавление комментария к посту блога (требует авторизации).
    """
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            messages.success(request, 'Комментарий добавлен!')
        else:
            messages.error(request, 'Ошибка при добавлении комментария.')

    return redirect('post-detail', pk=post.pk)


@login_required
def delete_comment(request, pk):
    """
    Удаление комментария (требует авторизации и владения).
    """
    comment = get_object_or_404(Comment, pk=pk)
    if request.user == comment.author or request.user == comment.post.author:
        comment.delete()
        messages.success(request, 'Комментарий удален!')
    else:
        messages.error(request, 'Вы не можете удалить этот комментарий.')

    return redirect('post-detail', pk=comment.post.pk)


@login_required
def profile(request):
    """
    Отображение профиля пользователя с его постами.
    """
    user_posts = Post.objects.filter(author=request.user).order_by('-created_at')
    return render(request, 'profile.html', {'posts': user_posts})


# REST API Views
class PostListAPI(generics.ListCreateAPIView):
    """
    API endpoint для получения списка постов и создания новых.
    """
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        """Устанавливает автора поста перед сохранением."""
        serializer.save(author=self.request.user)


class PostDetailAPI(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint для получения, обновления и удаления конкретного поста.
    """
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class CommentListAPI(generics.ListCreateAPIView):
    """
    API endpoint для получения списка комментариев и создания новых для конкретного поста.
    """
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """Возвращает комментарии для конкретного поста."""
        post_id = self.kwargs['post_id']
        return Comment.objects.filter(post_id=post_id)

    def perform_create(self, serializer):
        """Устанавливает автора и пост перед сохранением комментария."""
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        serializer.save(author=self.request.user, post=post)