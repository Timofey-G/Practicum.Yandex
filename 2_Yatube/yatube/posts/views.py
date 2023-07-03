from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Comment, Follow, Group, Post
from .utils import paginator

User = get_user_model()


def index(request):
    search_query = request.GET.get("search", "")
    if search_query:
        post_list = Post.objects.select_related("group").filter(
            text__iregex=search_query,
        )
    else:
        post_list = Post.objects.select_related("group").all()
    page_obj = paginator(post_list, request)
    context = {
        "page_obj": page_obj,
    }
    return render(request, "posts/index.html", context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    page_obj = paginator(post_list, request)
    context = {
        "group": group,
        "page_obj": page_obj,
    }
    return render(request, "posts/group_list.html", context)


def profile(request, username):
    user_obj = get_object_or_404(User, username=username)
    post_list = Post.objects.filter(author=user_obj)
    page_obj = paginator(post_list, request)
    following = (
        request.user.is_authenticated
        and (
            Follow.objects.filter(
                user=request.user,
                author=user_obj,
            )
        ).exists()
    )
    context = {
        "user_obj": user_obj,
        "page_obj": page_obj,
        "amount_posts": post_list.count(),
        "following": following,
    }
    return render(request, "posts/profile.html", context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    comments = Comment.objects.filter(post=post_id)
    context = {
        "post": post,
        "amount_posts": Post.objects.filter(author=post.author).count(),
        "form": form,
        "comments": comments,
    }
    return render(request, "posts/post_detail.html", context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None, files=request.FILES or None)

    if request.method == "POST" and form.is_valid():
        temp_form = form.save(commit=False)
        temp_form.author = request.user
        temp_form.save()
        return redirect("posts:profile", temp_form.author)

    context = {
        "form": form,
    }
    return render(request, "posts/create_post.html", context)


@login_required
def post_edit(request, post_id):
    is_edit = Post.objects.get(id=post_id)

    if request.user != is_edit.author:
        return redirect("posts:post_detail", post_id)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=is_edit,
    )

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("posts:post_detail", post_id)

    context = {
        "form": form,
        "is_edit": is_edit,
    }
    return render(request, "posts/create_post.html", context)


@login_required
def add_comment(request, post_id):
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = Post.objects.get(id=post_id)
        comment.save()
    return redirect("posts:post_detail", post_id=post_id)


@login_required
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user)
    page_obj = paginator(post_list, request)
    context = {
        "page_obj": page_obj,
    }
    return render(request, "posts/follow.html", context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect("posts:profile", username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    following = Follow.objects.filter(user=request.user, author=author)
    following.delete()
    return redirect("posts:profile", username)


@login_required
def post_like(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    author = get_object_or_404(User, id=request.user.id)
    if post.likes.filter(id=author.id).exists():
        post.likes.remove(author)
    else:
        post.likes.add(author)
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
