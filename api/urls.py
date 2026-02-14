from django.urls import path
import api.views as views

urlpatterns = [
    # path('auth/login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('post/create/', views.create_post, name='create_post'),
    path('story/create/', views.create_story, name='create_story'),
    path("dashboard/", views.dashboard, name='dashboard'),
    path('messages/', views.messages_view, name='messages'),
    path('messages/<str:username>/', views.messages_view, name='messages_with_user'),
    path('send/<str:username>/', views.send_message, name='send_message'),
    path('search/', views.search_users, name='search_users'),
    path('<str:username>/following/', views.following_list, name='following_list'),
    path('<str:username>/followers/', views.followers_list, name='followers_list'),
    path('follow/<str:username>/', views.toggle_follow, name='toggle_follow'),
    path('<str:username>/', views.profile_view, name='user_profile'),
    path('post/<int:post_id>/like/', views.toggle_like, name='toggle_like'),
]