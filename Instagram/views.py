from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
import Instagram.form as forms
from django.db.models import Q
import Instagram.models as models
from django.http import JsonResponse
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate, logout


from django.contrib.auth import authenticate, login

def login_view(request):
    # is_authenticated tekshiruvini olib tashladik
    if request.POST:
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "Xush kelibsiz!")
                return redirect("/")
            else:
                messages.error(request, f"XATO: User is not Found")
        else:
            messages.error(request, f"XATO: {form.errors}")
    form = AuthenticationForm()
    return render(request, "login.html", {"form": form})


def register_view(request):
    # is_authenticated tekshiruvini olib tashladik
    if request.method == "POST":
        form = forms.CustomUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Register bo'lgandan keyin avtomatik login qilish
            login(request, user)
            messages.success(request, "Muvaffaqiyatli ro'yxatdan o'tdingiz!")
            return redirect('/')
        else:
            messages.error(request, "Ma'lumotlarni to'g'ri kiriting.")
    else:
        form = forms.CustomUserForm()

    return render(request, "register.html", {"form": form})


def edit_profile_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    user = request.user
    
    if request.method == "POST":
        # Profil ma'lumotlarini yangilash
        user.bio = request.POST.get('bio', '')[:150]
        user.website = request.POST.get('website', '')
        
        # Profil rasmini yangilash
        if 'image' in request.FILES:
            user.image = request.FILES['image']
        
        if 'song' in request.FILES:
            user.song = request.FILES['song']
        
        user.save()
        messages.success(request, "Profil muvaffaqiyatli yangilandi!")
        return redirect('/', username=user.username)
    
    return render(request, 'edit_profile.html', {'user': user})

def create_post(request):
    if request.method == "POST":
        form = forms.PostsForm(request.POST, files=request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.owner = request.user
            post.save()
            messages.success(request, "Post muvaffaqiyatli qo'shildi!")
            return redirect('/')
        else:
            print(form.errors)
            messages.error(request, "Formani to'g'ri to'ldiring.")
            return redirect('/post/create/')
            
    form = forms.PostsForm()
    return render(request, "form.html", {"form": form})

def create_story(request):
    if request.method == "POST":
        form = forms.StoryForm(request.POST, request.FILES)
        if form.is_valid():
            story = form.save(commit=False)
            story.owner = request.user
            story.save()
            messages.success(request, "Istoriya Qo'shildi")
        else:
            messages.error(request, "Malumotlari tog'ri kiriting")
    else:
        form = forms.StoryForm()

    return render(request, "form.html", {"form":form})


def dashboard(request):
    if not request.user.is_authenticated:
        posts = models.Posts.objects.all().order_by('-created_at')
        return render(request, 'dashboard.html', {'posts': posts})

    following_users = models.Follow.objects.filter(follower=request.user).values_list('following', flat=True)

    if not following_users:
        posts = models.Posts.objects.exclude(owner=request.user).order_by('-created_at')
    else:
        posts = models.Posts.objects.filter(owner__in=following_users).order_by('-created_at')

    return render(request, 'dashboard.html', {'posts': posts})

def profile_view(request, username=None):
    if username:
        target_user = get_object_or_404(models.CustomUser, username=username)
    else:
        target_user = request.user
    
    followers_count = target_user.following.count()
    following_count = target_user.followers.count()
    saved_posts = models.Saved_posts.objects.filter(owner=request.user).select_related('posts')
    return render(request, 'profile.html', {
        'target_user': target_user,
        'followers_count': followers_count,
        'following_count': following_count,
        'saved_posts': saved_posts,
    })

def toggle_follow(request, username):
    target_user = get_object_or_404(models.CustomUser, username=username)
    current_user = request.user

    if current_user == target_user:
        return redirect('profile', username=username)
    follow, created = models.Follow.objects.get_or_create(follower=current_user, following=target_user)

    if not created:
        follow.delete()
        is_following = False
    else:
        is_following = True
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'is_following': is_following, 'followers_count': target_user.follower.count()})
    return redirect('user_profile', username=username)


def following_list(request, username):
    target_user = get_object_or_404(models.CustomUser, username=username)
    following_records = models.Follow.objects.filter(follower=target_user).select_related('following')
    return render(request, 'following.html', {'target_user': target_user, 'following_users': following_records,})


def followers_list(request, username):
    target_user = get_object_or_404(models.CustomUser, username=username)
    follower_records = models.Follow.objects.filter(following=target_user).select_related('follower')
    return render(request, 'followers.html', {'target_user': target_user, 'follower_users': follower_records,})



def toggle_like(request, post_id):
    post = get_object_or_404(models.Posts, id=post_id)
    user = request.user

    if user in post.likes.all():
        post.likes.remove(user)
        liked = False
    else:
        post.likes.add(user)
        liked = True

    like_count = post.likes.count()

    return JsonResponse({'liked': liked, 'like_count': like_count})


def search_users(request):
    query = request.GET.get('q', '').strip()

    if not query:
        return JsonResponse({'users': []})
    users = models.CustomUser.objects.filter(username__icontains=query)

    results = []
    for user in users[:10]:
        results.append({
            'username': user.username,
            'image': user.image.url if user.image else None,
            'followers_count': user.followers.count(),
        })

    return JsonResponse({'users': results})

def user_stories(request, username):
    user = get_object_or_404(models.CustomUser, username=username)
    stories = models.Story.objects.filter(owner=user).order_by('-created_at')

    context = {
        'user': user,
        'stories': stories,
    }
    return render(request, 'user_stories.html', context)


def send_message(request, username):
    receiver = get_object_or_404(models.CustomUser, username=username)
    if request.method == "POST":
        text = request.POST.get('text')
        if text:
            models.Message.objects.create(sender=request.user, receiver=receiver, text=text)
        return redirect('messages_with_user', username=username)

    return redirect('messages')

def messages_view(request, username=None):
    try:
        current_user = models.CustomUser.objects.get(id=request.user.id)
    except models.CustomUser.DoesNotExist:
        logout(request)
        return redirect('/login/')

    if username:
        selected_user = get_object_or_404(models.CustomUser, username=username)
    else:
        selected_user = current_user

    recent_users = models.CustomUser.objects.filter(Q(sent_messages__receiver=current_user) | Q(received_messages__sender=current_user)).distinct()[:5]

    if username:
        messages = models.Message.objects.filter((Q(sender=current_user) & Q(receiver=selected_user)) | (Q(sender=selected_user) & Q(receiver=current_user))).order_by('timestamp')
    else:
        messages = []

    return render(request, 'chat.html', {
        'selected_user': selected_user,
        'recent_users': recent_users,
        'messages': messages
    })


def write_comment(request, post_id):
    get_post = get_object_or_404(models.Posts, id=post_id)
    if request.method == "POST":
        text = request.POST.get("text")
        if text:
            models.Comment.objects.create(comment=text, owner=request.user, post=get_post)
        return redirect('post_detail', post_id=post_id)
    
    return redirect('post_detail', post_id=post_id)


def comment_list(request, post_id):
    post = get_object_or_404(models.Posts, id=post_id)
    comments = models.Comment.objects.filter(post=post)
    return render(request, "post_detail.html", {"comments": comments, "post": post})

from django.http import JsonResponse

def add_saved(request, post_id):
    if request.method == "POST":
        post = get_object_or_404(models.Posts, id=post_id)
        saved_exists = models.Saved_posts.objects.filter(owner=request.user, posts=post).first()
        if saved_exists:
            saved_exists.delete()
            is_saved = False
        else:
            models.Saved_posts.objects.create(owner=request.user, posts=post)
            is_saved = True

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'is_saved': is_saved})
        
        return redirect('user_profile', username=request.user.username)
    return redirect('user_profile', username=request.user.username)

def delete_post(request, post_id):
    post = models.Posts.objects.filter(id=post_id)
    post.delete()
    return redirect("/")