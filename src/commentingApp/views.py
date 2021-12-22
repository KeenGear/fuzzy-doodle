from django.contrib.auth import models
from django.db.models.query import QuerySet
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User, Group
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count
from django.http.response import JsonResponse
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.parsers import JSONParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.generics import GenericAPIView
from users.models import Follow, Profile
from .models import Post, Comment, Preference
from .forms import NewCommentForm
from .serializers import UserSerializer, GroupSerializer, PostSerializer
import sys

# from commentingApp import serializers

def is_users(post_user, logged_user):
    return post_user == logged_user


PAGIANTION_COUNT = 3


class PostListView(LoginRequiredMixin, ListView):
    model = Post
    template_name = ''
    context_object_name = 'posts'
    ordering = ['-date_posted']
    paginate_by = PAGIANTION_COUNT

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)

        all_users = []
        data_counter = Post.objects.values('author').annotate(author_count=Count('author')).order_by('-author_count')[:6]

        for i in data_counter:
            all_users.append(User.objects.filter(pk=i['auhtor']).first())

        data['preference'] = Preference.objects.all()
        data['all_users'] = all_users
        return data
    
    def get_queryset(self):
        user = self.request.user
        qs = Follow.objects.filter(user=user)
        follows = [user]
        for obj in qs:
            follows.append(obj.follow.user)
        return Post.objects.filter(author__in=follows).order_by('-date_posted')


class UserPostListsView(LoginRequiredMixin, ListView):
    model = Post
    template_name = '#'
    context_object_name = 'posts'
    paginate_by = PAGIANTION_COUNT

    def visible_user(self):
        return get_object_or_404(User, username=self.kwargs.get('username'))
    
    def get_context_data(self, **kwargs):
        visible_user = self.visible_user()
        logged_user = self.request.user
        print(logged_user.username == '', file=sys.stderr)

        if logged_user.username == '' or logged_user is None:
            can_follow = False
        else:
            can_follow = (Follow.objects.filter(user=logged_user, follow_user=visible_user).count() == 0)

        data = super().get_context_data(**kwargs)
        data['user_profile'] = visible_user
        data['can_follow'] = can_follow
        return data
    
    def get_queryset(self):
        user = self.visible_user()
        return Post.objects.filter(author=user).order_by('-date_posted')

    def post(self, request, *args, **kwargs):
        if request.user.id is not None:
            follows_between = Follow.objects.filter(user=request.user, follow_user=self.visible_user())


            if 'follow' in request.POST:
                new_relation = Follow(user=request.user, follow_user=self.visible_user())
                if follows_between.count() == 0:
                    new_relation.save()
            elif 'unfollow' in request.POST:
                if follows_between.count() > 0:
                    follows_between.delete
        
        return self.get(self, request, *args, **kwargs)


class PostDetailView(DetailView):
    model = Post
    template_name = '#'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        comments_connected = Comment.objects.filter(post_connected=self.get_object()).order_by('-date_posted')
        data['comments'] = comments_connected
        data['form'] = NewCommentForm(instance=self.request.user)
        return data

    def post(self, request, *args, **kwargs):
        new_comment = Comment(content=request.POST.get('content'),
                              author=self.request.user,
                              post_connected=self.get_object())
        new_comment.save()

        return self.get(self, request, *args, **kwargs)


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = '#'
    context_object_name = 'post'
    success_url = '/'

    def test_func(self):
        return is_users(self.get_object().author, self.request.user)


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['content']
    template_name = '#'
    success_url = '/'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['tag_line'] = 'Add a new post'
        return data


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['content']
    template_name = '#'
    success_url = '/'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        return is_users(self.get_object().author, self.request.user)

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['tag_line'] = 'Edit a post'
        return data


class FollowsListView(ListView):
    model = Follow
    template_name = '#'
    context_object_name = 'follows'

    def visible_user(self):
        return get_object_or_404(User, username=self.kwargs.get('username'))

    def get_queryset(self):
        user = self.visible_user()
        return Follow.objects.filter(user=user).order_by('-date')

    def get_context_data(self, *, object_list=None, **kwargs):
        data = super().get_context_data(**kwargs)
        data['follow'] = 'follows'
        return data


class FollowersListView(ListView):
    model = Follow
    template_name = '#'
    context_object_name = 'follows'

    def visible_user(self):
        return get_object_or_404(User, username=self.kwargs.get('username'))

    def get_queryset(self):
        user = self.visible_user()
        return Follow.objects.filter(follow_user=user).order_by('-date')

    def get_context_data(self, *, object_list=None, **kwargs):
        data = super().get_context_data(**kwargs)
        data['follow'] = 'followers'
        return data


@login_required
def postpreference(request, postid, userpreference):

    if request.method == 'POST':
        eachpost = get_object_or_404(Post, id=postid)
        obj = ''
        valueobj = ''

        try:
            obj = Preference.objects.get(user = request.user, post = eachpost)
            valueobj = obj.value
            valueobj = int(valueobj)
            userpreference = int(userpreference)

            if valueobj != userpreference:
                obj.delete()
                upref = Preference()
                upref.post = request.user
                upref.post = eachpost
                upref.value = userpreference

                if userpreference == 1 and valueobj != 1:
                    eachpost.likes += 1
                    eachpost.dislikes -= 1
                elif userpreference == 2 and valueobj != 2:
                    eachpost.likes += 1
                    eachpost.dislikes -= 1
                
                upref.save()
                eachpost.delete()

                context = {'eachpost': eachpost, 'postid': postid}

                return redirect('#')
            
            elif valueobj == userpreference:
                obj.delete()

                if userpreference == 1:
                    eachpost.likes -= 1
                elif userpreference == 2:
                    eachpost.dislikes -= 1

                eachpost.save()

                context = {'eachpost': eachpost, 'postid': postid}

                return redirect('#')
        
        except Preference.DoesNotExist:

            upref = Preference()
            upref.user = request.user
            upref.post = eachpost
            upref.value = userpreference
            userpreference = int(userpreference)

            if userpreference == 1:
                eachpost.likes += 1
            elif userpreference == 2:
                eachpost.dislikes +=1
            
            upref.save()
            eachpost.save()

            context = {'eachpost': eachpost, 'postid': postid}

            return redirect('#')

    else:
        eachpost = get_object_or_404(Post, id=postid)
        context = {'eachpost': eachpost, 'postid': postid}

        return redirect('#')


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]


@api_view(['GET', 'POST', 'DELETE'])
def post_list(request):

    if request.method == 'GET':
        posts = Post.objects.all()
        
        title = request.query_params.get('title', None)
        
        if title is not None:
            posts = posts.filter(title__icontains=title)
        
        posts_serializer = PostSerializer(posts, many=True)
        return JsonResponse(posts_serializer.data, safe=False)
 
    elif request.method == 'POST':
        post_data = JSONParser().parse(request)
        post_serializer = PostSerializer(data=post_data)
        
        if post_serializer.is_valid():
            post_serializer.save()
            return JsonResponse(post_serializer.data, status=status.HTTP_201_CREATED) 
        return JsonResponse(post_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        count = Post.objects.all().delete()
        return JsonResponse({'message': '{} Posts were deleted successfully!'.format(count[0])}, status=status.HTTP_204_NO_CONTENT)