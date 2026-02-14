from django.urls import path
import Instagram.views as views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('post/<int:post_id>/delete', views.delete_post, name="delete_post"),
    path('accounts/edit/', views.edit_profile_view, name='edit_profile'),
    path('post/<int:post_id>/save/', views.add_saved, name='add_saved'),
    path('post/<int:post_id>/comment/', views.write_comment, name="write_comment"),
    path('post/<int:post_id>/', views.comment_list, name='post_detail'),
    path('stories/<str:username>/', views.user_stories, name='user_stories'),
    path('register/', views.register_view, name='register'),
    path('post/create/', views.create_post, name='create_post'),
    path('story/create/', views.create_story, name='create_story'),
    path("", views.dashboard, name='dashboard'),
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