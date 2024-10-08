from django.urls import path
from .views import *



urlpatterns = [
    path('', index,name="index"),
    path('signup/', signup,name="signup"),
    path('signin/', signin,name="signin"),
    path('logout/', logout,name="logout"),
    path('sett/', sett,name="sett"),
    path('upload', upload, name='upload'),
    path('like-post', like_post, name='like-post'),
    path('profile/<str:pk>', profile, name='profile'),
    path('follow', follow, name='follow'),
    path('search', search, name='search'),
    path('delete_post/<int:post_id>/', delete_post, name='delete_post')



]
