
from itertools import chain
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User,auth
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from account.models import Profile,Post,LikePost,FollowersCount
import random
from django.http import JsonResponse


@login_required(login_url='signin')
def index(req):
    # Fetch the logged-in user and their profile
    user_object = User.objects.get(username=req.user.username)
    user_profile = Profile.objects.get(user=user_object)

    # Fetch the list of users whom the logged-in user is following
    user_following = FollowersCount.objects.filter(follower=req.user.username)
    user_following_list = [user.user for user in user_following]

    # Fetch posts from the logged-in user
    user_posts = Post.objects.filter(user=req.user)

    # Fetch posts from users whom the logged-in user is following
    following_posts = Post.objects.filter(user__in=user_following_list)

    # Combine the posts from the logged-in user and the users they are following
    feed_list = list(user_posts) + list(following_posts)

    # Sorting the feed by the created_at field (adjust the field based on your model)
    feed_list.sort(key=lambda x: x.created_at, reverse=False)    

    #user suggestion starts
    all_users=User.objects.all()
    user_following_all=[]

    for user in user_following:
        user_list=User.objects.get(username=user.user)
        user_following_all.append(user_list)

    new_suggestions_list = [x for x in list(all_users) if (x not in list(user_following_all))]
    current_user = User.objects.filter(username=req.user.username)
    final_suggestion_list = [x for x in list(new_suggestions_list) if (x not in list(current_user))]   
    random.shuffle(final_suggestion_list)


    username_profile =[]
    username_profile_list = []

    for users in final_suggestion_list:
        username_profile.append(users.id)

    for ids in username_profile:
        profile_lists = Profile.objects.filter(id_user=ids) 
        username_profile_list.append(profile_lists)

    suggestions_username_profile_list=list(chain(*username_profile_list))

    return render (req,'index.html',{'user_profile':user_profile,'posts':feed_list,'suggestions_username_profile_list':suggestions_username_profile_list[:4]})

def signup(req):

    if req.method == "POST":
        first_name = req.POST["first_name"] 
        last_name = req.POST["last_name"]
        username = req.POST["username"]
        email = req.POST["email"]
        password = req.POST["password"]
        password2 = req.POST["confirm_password"]

        if password == password2:
            if User.objects.filter(email=email).exists():
                messages.info(req,'Email already used')
                return redirect ('signup')
            elif User.objects.filter(username=username).exists():
                messages.info(req,'Username already used')
                return redirect ('signup')
            else:
                user = User.objects.create_user(first_name=first_name,last_name=last_name,username=username,email=email,password=password)
                user.save()
                # log user in and redirect to setting page
                user_login = auth.authenticate(username=username,password=password)
                auth.login(req,user_login)
                # create a profile objrct for new user
                user_model = User.objects.get(username=username)
                new_profile = Profile.objects.create(user=user_model,id_user=user_model.id)
                new_profile.save()
                return redirect("sett")
        else: 
            messages.info(req,'Password not  Matching')
            return redirect('signup')
    else:
        return render(req,'signup.html')
    
def signin(req):

    if req.method == "POST":
        username = req.POST['username']
        password = req.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(req,user)
            return redirect('/')
        else:
            messages.info(req,'Credentials Invalid') 
            return redirect('signin')
    else :    
        return render(req,"signin.html")


@login_required(login_url='signin')    
def logout(req) :

    auth.logout(req)   
    return redirect('signin')

# @login_required(login_url='signin')  
# def sett(request):
#     import pdb; pdb.set_trace()
#     user_profile = Profile.objects.get(id=request.user.id)

#     if request.method == 'POST':
        
#         if request.FILES.get('image') == None:
#             image = user_profile.profileimg
#             bio = request.POST['bio']
#             location = request.POST['location']

#             user_profile.profileimg = image
#             user_profile.bio = bio
#             user_profile.location = location
#             user_profile.save()
#         if request.FILES.get('image') != None:
#             image = request.FILES.get('image')
#             bio = request.POST['bio']
#             location = request.POST['location']

#             user_profile.profileimg = image
#             user_profile.bio = bio
#             user_profile.location = location
#             user_profile.save()
        
#         return redirect('sett')
#     return render(request, 'setting.html', {'user_profile': user_profile}) 
@login_required(login_url='signin')
def sett(request):
    user_profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        image = request.FILES.get('image', user_profile.profileimg)
        bio = request.POST.get('bio', user_profile.bio)
        location = request.POST.get('location', user_profile.location)

        user_profile.profileimg = image
        user_profile.bio = bio
        user_profile.location = location
        user_profile.save()
        
        return redirect('index')
    
    return render(request, 'setting.html', {'user_profile': user_profile})

@login_required(login_url='signin')
def upload(req):
    if req.method == "POST":
        user = req.user.username
        image = req.FILES.get("image_upload")
        caption = req.POST['caption']

        new_post = Post(user=user, image=image, caption=caption)
        new_post.save()

        return redirect('/')

    else:
        return redirect('/')

@login_required(login_url='signin')    
def like_post(req):
    username=req.user.username
    post_id=req.GET.get('post_id')
    post = Post.objects.get(id=post_id)

    like_filter= LikePost.objects.filter(post_id=post_id,username=username).first()
    if like_filter == None:
        new_like = LikePost.objects.create(post_id=post_id,username=username)
        new_like.save()
        post.no_of_likes=post.no_of_likes+1
        post.save()
        return redirect('/') 
    else:
        like_filter.delete()
        post.no_of_likes=post.no_of_likes-1
        post.save()
        return redirect('/') 

@login_required(login_url='signin')   
def profile(req, pk):
    user_object= User.objects.get(username=pk)
    user_profile=Profile.objects.get(user=user_object)
    user_posts = Post.objects.filter(user=pk)
    user_post_length=len(user_posts)
    
    follower=req.user.username
    user=pk

    if FollowersCount.objects.filter(follower=follower,user=user).first():
        button_text = 'Unfollow'
    else:
        button_text ='Follow'

    user_followers = len(FollowersCount.objects.filter(user=pk))
    user_following = len(FollowersCount.objects.filter(follower=pk))        

    context={
        'user_object':user_object,
        'user_profile':user_profile,
        'user_posts':user_posts,
        'user_post_length':user_post_length,
        'button_text':button_text,
        'user_followers':user_followers,
        'user_following':user_following,
    }
    return render(req,'profile.html',context)    
       
@login_required(login_url='signin')   
def follow(req):
    if req.method == 'POST':
        follower = req.POST['follower']
        user = req.POST['user']

        if FollowersCount.objects.filter(follower=follower,user=user):
            delete_follower= FollowersCount.objects.get(follower=follower,user=user)
            delete_follower.delete()
            return redirect('/profile/'+user)
        
        else:
            new_follower=FollowersCount.objects.create(follower=follower,user=user)
            new_follower.save()
            return redirect('/profile/'+user)

    
    else:
        return redirect('/')
    
@login_required(login_url='signin')   
def search(req):
    user_object = User.objects.get(username=req.user.username)
    user_profile = Profile.objects.get(user=user_object)

    if req.method == 'POST':
        username=req.POST['username']
        username_object = User.objects.filter(username__icontains=username)

        username_profile = []
        username_profile_list=[]

        for users in username_object:
            username_profile.append(users.id)

        for ids in username_profile:
            profile_lists=Profile.objects.filter(id_user=ids)
            username_profile_list.append(profile_lists)

        username_profile_list=list(chain(*username_profile_list))    

    return render(req,'search.html',{'user_object':user_profile,'username_profile_list':username_profile_list})

@login_required(login_url='signin')
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    # Check if the logged-in user is the owner of the post
    if request.user == post.user:
        post.delete()
        return JsonResponse({'message': 'Post deleted successfully'})
    else:
        return JsonResponse({'message': 'Unauthorized'}, status=403)
