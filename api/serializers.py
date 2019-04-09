from django.contrib.auth.models import User, Group
from rest_framework import serializers
from .models import Profile, Project, ProjectMembership, Role, ResearchGroup, Course
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.contrib.auth import get_user_model
from drf_writable_nested import WritableNestedModelSerializer


# HyperlinkModelSerializer is a serializer for built-in models
class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'first_name', 'last_name')
        extra_kwargs = {
            'password': {'write_only': True, 'required': True}
        }

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class UpdateUserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name')

        # required because i's nested serializer
        extra_kwargs = {
            'username': {
                'validators': [UnicodeUsernameValidator()],
            },
        }


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ('id', 'title')


class ProfileSerializer(WritableNestedModelSerializer):
    user = UpdateUserSerializer()

    class Meta:
        model = Profile
        fields = ('id', 'user', 'department', 'workplace', 'office', 'phone', 'address', 'personal_web_site',
                  'profile_img')
        extra_kwargs = {'id': {'read_only': False}}

    def create(self, validated_data):
        print('-- create new profile --')
        user_data = validated_data.pop('user')
        username = user_data.pop('username')
        user = get_user_model().objects.get_or_create(username=username)[0]
        profile = Profile.objects.create(user=user, **validated_data)
        return profile

    def update(self, instance, validated_data):
        print('-- update profile for user --' + str(instance.user.id))
        # get validated data
        user_data = validated_data.pop('user')
        user = instance.user

        user.first_name = user_data.get('first_name', user.first_name)
        user.last_name = user_data.get('last_name', user.last_name)
        user.save()

        # get existing or create new user
        # user = get_user_model().objects.get_or_create(id=instance.user.id)[0]

        # set profile related properties
        instance.department = validated_data.get('department', instance.department)
        instance.workplace = validated_data.get('workplace', instance.workplace)
        instance.office = validated_data.get('office', instance.office)
        instance.phone = validated_data.get('phone', instance.phone)
        instance.address = validated_data.get('address', instance.address)
        instance.personal_web_site = validated_data.get('personal_web_site', instance.personal_web_site)
        instance.profile_img = validated_data.get('profile_img', instance.profile_img)
        instance.save()
        return instance


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ('id', 'title', 'label', 'institutions', 'pmf_status', 'start_year', 'duration', 'project_manager',
                  'web_site', 'contact_person')
        extra_kwargs = {'id': {'read_only': False}}


class ProjectMembershipSerializer(serializers.ModelSerializer):
    profile = serializers.PrimaryKeyRelatedField(many=False, queryset=Profile.objects.all())
    project = serializers.PrimaryKeyRelatedField(many=False, queryset=Project.objects.all())
    role = serializers.PrimaryKeyRelatedField(many=False, queryset=Role.objects.all())

    class Meta:
        model = ProjectMembership
        fields = ('id', 'profile', 'project', 'role')


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ('id', 'role_name')


# class UpdateProfileSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Profile
#         fields = ('id', 'department', 'workplace', 'office', )

class ResearchGroupSerializer(serializers.ModelSerializer):
    project_set = ProjectSerializer(many=True)
    contact_person = ProfileSerializer()

    class Meta:
        model = ResearchGroup
        fields = ('id', 'title', 'key_words', 'research_direction', 'group_leader', 'members', 'goals', 'equipment',
                  'cooperation', 'web_site', 'project_set', 'contact_person')

    def create(self, validated_data):
        print('-- create new research group --')
        profile_data = validated_data.pop('contact_person')
        projects_data = validated_data.pop('project_set')
        print(projects_data)
        profile = Profile.objects.get(id=profile_data.pop('id'))
        research_group = ResearchGroup.objects.create(contact_person=profile, **validated_data)

        for project in projects_data:
            group_project = Project.objects.get(id=project.get('id'))
            research_group.project_set.add(group_project)

        research_group.save()
        return research_group
