from rest_framework import serializers
from django.contrib.auth.models import User, Group
from .models import Post


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        models = Group
        fields = ['url', 'name']


class PostSerializer(serializers.Serializer):
    class Meta:
        model = Post
        fields = ['content', 'author']