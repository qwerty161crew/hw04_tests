from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .forms import PostForm
from .models import Post, Group, User


def get_page(page_number, posts):
    paginator = Paginator(posts, 10)
    page_obj = paginator.get_page(page_number)
    return page_obj


def index(request):
    posts = Post.objects.all()
    page_obj = get_page(request.GET.get('page'), posts)
    context = {
        'page_obj': page_obj
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=group).all()
    page_obj = get_page(request.GET.get('page'), posts)
    context = {
        'group': group,
        'posts': posts,
        'page_obj': page_obj
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    page_obj = get_page(request.GET.get('page'), posts)
    context = {
        'page_obj': page_obj,
        'author': author,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    context = {
        'post': post
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    """Добавления поста."""
    template = "posts/create_post.html"
    form = PostForm(request.POST or None)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.author_id = request.user.id
        instance.save()
        return redirect(reverse("posts:profile",
                                kwargs={'username': request.user}))

    return render(request, template, {"form": form, "is_edit": False})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user.id != post.author.id:
        return redirect(reverse("posts:post_detail",
                                kwargs={'post_id': post_id}))
    form = PostForm(request.POST or None, instance=post)
    if form.is_valid():
        form.save()
        return redirect(reverse("posts:post_detail",
                                kwargs={'post_id': post_id}))
    context = {
        "form": form,
        "is_edit": True,
    }
    return render(request, "posts/create_post.html", context)
