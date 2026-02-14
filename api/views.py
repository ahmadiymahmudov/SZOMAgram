from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.core.files.storage import default_storage
from Instagram import models
from .serializers import CustomUserSerializer, PostsSerializer, StorySerializer, MessageSerializer


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response({'error': 'Username va parol talab qilinadi.'}, status=status.HTTP_400_BAD_REQUEST)
    
    user = authenticate(username=username, password=password)
    if user is not None:
        login(request, user)
        return Response({
            'message': 'Muvaffaqiyatli tizimga kirildi.',
            'user_id': user.id,
            'username': user.username
        }, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Notogri foydalanuvchi nomi yoki parol.'}, status=status.HTTP_401_UNAUTHORIZED)
    


@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    serializer = CustomUserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        user.set_password(request.data['password'])  # Parolni xavfsiz saqlash
        user.save()
        return Response({
            'message': 'Muvaffaqiyatli royxatdan otdingiz!',
            'user_id': user.id,
            'username': user.username
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_post(request):
    serializer = PostsSerializer(data=request.data)
    
    if serializer.is_valid():
        post = serializer.save(owner=request.user)
        return Response({
            'message': 'Post muvaffaqiyatli qo‘shildi!',
            'post_id': post.id
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_story(request):
    serializer = StorySerializer(data=request.data)
    if serializer.is_valid():
        story = serializer.save(owner=request.user)
        return Response({
            'message': 'Istoriya qoshildi!',
            'story_id': story.id
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_follow(request, username):
    target_user = get_object_or_404(models.CustomUser, username=username)
    current_user = request.user

    if current_user == target_user:
        return Response({'error': 'Ozingizga obuna bololmaysiz.'}, status=status.HTTP_400_BAD_REQUEST)

    follow, created = models.Follow.objects.get_or_create(
        follower=current_user,
        following=target_user
    )

    if not created:
        follow.delete()
        is_following = False
    else:
        is_following = True

    return Response({
        'is_following': is_following,
        'followers_count': target_user.following.count()
    }, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_like(request, post_id):
    post = get_object_or_404(models.Posts, id=post_id)
    user = request.user

    if user in post.likes.all():
        post.likes.remove(user)
        liked = False
    else:
        post.likes.add(user)
        liked = True

    return Response({
        'liked': liked,
        'like_count': post.likes.count()
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_users(request):
    query = request.GET.get('q', '').strip()
    if not query:
        return Response({'users': []}, status=status.HTTP_200_OK)

    users = models.CustomUser.objects.filter(username__icontains=query)[:10]
    results = []
    for user in users:
        results.append({
            'username': user.username,
            'image': user.image.url if user.image else None,
            'followers_count': user.following.count(),
        })
    return Response({'users': results}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard(request):
    following_ids = models.Follow.objects.filter(follower=request.user).values_list('following', flat=True)
    posts = models.Posts.objects.filter(owner__in=following_ids).order_by('-created_at')
    serializer = PostsSerializer(posts, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile_view(request, username=None):
    if username:
        target_user = get_object_or_404(models.CustomUser, username=username)
    else:
        target_user = request.user

    followers_count = target_user.following.count()
    following_count = target_user.followers.count()

    return Response({
        'username': target_user.username,
        'followers_count': followers_count,
        'following_count': following_count,
        'is_own_profile': (target_user == request.user)
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def following_list(request, username):
    target_user = get_object_or_404(models.CustomUser, username=username)
    following_records = models.Follow.objects.filter(follower=target_user).select_related('following')
    following_users = [record.following for record in following_records]
    serializer = CustomUserSerializer(following_users, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def followers_list(request, username):
    target_user = get_object_or_404(models.CustomUser, username=username)
    follower_records = models.Follow.objects.filter(following=target_user).select_related('follower')
    followers = [record.follower for record in follower_records]
    serializer = CustomUserSerializer(followers, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_message(request, username):
    receiver = get_object_or_404(models.CustomUser, username=username)
    text = request.data.get('text', '').strip()

    if not text:
        return Response({'error': 'Xabar matni bo‘sh bo‘lmasligi kerak.'}, status=status.HTTP_400_BAD_REQUEST)

    message = models.Message.objects.create(
        sender=request.user,
        receiver=receiver,
        text=text
    )

    serializer = MessageSerializer(message)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def messages_view(request, username=None):
    current_user = request.user

    if username:
        selected_user = get_object_or_404(models.CustomUser, username=username)
        messages = models.Message.objects.filter(
            (Q(sender=current_user) & Q(receiver=selected_user)) |
            (Q(sender=selected_user) & Q(receiver=current_user))
        ).order_by('timestamp')
        messages_data = MessageSerializer(messages, many=True).data
    else:
        selected_user = current_user
        messages_data = []

    # So'nggi 5 ta suhbatdosh
    recent_users = models.CustomUser.objects.filter(
        Q(sent_messages__receiver=current_user) |
        Q(received_messages__sender=current_user)
    ).distinct()[:5]

    recent_users_data = CustomUserSerializer(recent_users, many=True).data

    return Response({
        'selected_user': CustomUserSerializer(selected_user).data,
        'recent_users': recent_users_data,
        'messages': messages_data
    }, status=status.HTTP_200_OK)