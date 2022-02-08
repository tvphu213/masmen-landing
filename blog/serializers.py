from django.contrib.auth.models import User, Group
from blog.models import Company, Server
from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']


class CompanySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Company
        read_only_fields = [ 'id' ]
        fields = ['companyName', 'phone_number', 'maxUserNumber', 'location']


class ServerSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Server
        read_only_fields = ['id', 'docker_id', 'port' ]
        fields = ['id', 'company', 'domain_name', 'state', 'port']
