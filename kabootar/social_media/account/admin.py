from django.contrib import admin
from account.models import Profile,Post,LikePost,FollowersCount

admin.site.register(Profile)
admin.site.register(Post)
admin.site.register(LikePost)
admin.site.register(FollowersCount)

# Register your models here.
