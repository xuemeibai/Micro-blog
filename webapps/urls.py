"""webapps URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from socialnetwork import views
from django.contrib.auth import views as auth_views
from django.conf.urls import url, include

urlpatterns = [
    path('', views.globalStream_action, name='globalStream'),
    path('globalStream', views.globalStream_action, name='globalStream'),
    path('followerStream', views.followerStream_action, name='followerStream'),
    path('login', views.login_action, name='login'),
    path('logout', views.logout_action, name='logout'),
    path('register', views.register_action, name='register'),
    path('socialnetwork/add_post', views.add_post,name = 'add_post'),
    path('edit', views.edit_profile, name='edit'),
    path('follow/(<int:id>)',views.follow,name='follow'),
    path('unfollow/(<int:id>)',views.unfollow,name='unfollow'),
    path('socialnetwork/profiles/<int:id>',views.profiles_action, name='profiles'),
    path('photo/(<int:id>)', views.get_photo, name='photo'),
    path('socialnetwork/refresh-global',views.refresh_global),
    path('socialnetwork/refresh-follower',views.refresh_follower),
    path('socialnetwork/add-comment', views.add_comment),
    path('socialnetwork/load_global', views.loadGlobalStream),
    path('socialnetwork/load_follower', views.loadFollowerStream),
    # ('socialnetwork/add-comment/(<int:id>)', views.add_comment),
    # path('get-list-json', views.get_list_json),
    # path('get_comment_json/<int:id>',views.get_comment_json),
    # path('get_comments_json',views.get_comments_json),
]
