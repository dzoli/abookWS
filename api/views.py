from typing import Any

from django.shortcuts import render

from django.contrib.auth.models import User
from rest_framework import viewsets
from .serializers import UserSerializer, ProfileSerializer, ProjectSerializer, ProjectMembershipSerializer, \
    RoleSerializer, ResearchGroupSerializer, CourseSerializer
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from .models import Profile, Project, ProjectMembership, Role, ResearchGroup, Course
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework import generics
from django.db.models import Q


# from .serializers import UserProfileSerializer


# ViewSet is a view that is used to display serialized model
class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # authentication_classes = (TokenAuthentication, SessionAuthentication)
    # permission_classes = (IsAuthenticated,)


# class GroupViewSet(viewsets.ModelViewSet):
#     """
#     API endpoint that allows groups to be viewd or edited
#     """
#     queryset = Group.objects.all()
#     serializer_class = GroupSerializer

class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    parser_classes = (MultiPartParser, FormParser, JSONParser)


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def get_queryset(self):
        queryset = Course.objects.all()
        profile_id = self.request.query_params.get('id', None)
        if profile_id is not None:
            queryset = queryset.filter(profile_id=profile_id)
        return queryset


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    def get_queryset(self):
        queryset = Project.objects.all()
        user_id = self.request.query_params.get('id', None)
        user_nid = self.request.query_params.get('nid', None)
        if user_id is not None and user_nid is None:
            queryset = queryset.filter(members__user__id=user_id)
        elif user_id is None and user_nid is not None:
            queryset = queryset.filter(~Q(members__user__id=user_nid))
        return queryset


class MembershipsViewSet(viewsets.ModelViewSet):
    """
    API endpoint that provides list, detail, retrieve, update for list of ProjectMembership
    """
    queryset = ProjectMembership.objects.all()
    serializer_class = ProjectMembershipSerializer

    def get_serializer(self, *args: Any, **kwargs: Any):
        if isinstance(kwargs.get('data', {}), list):
            kwargs['many'] = True
        return super(MembershipsViewSet, self).get_serializer(*args, **kwargs)


class RolesViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer


class ResearchGroupViewSet(viewsets.ModelViewSet):
    queryset = ResearchGroup.objects.all()
    serializer_class = ResearchGroupSerializer
    parser_classes = (MultiPartParser, FormParser, JSONParser)


class ApiObtainAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        response = super(ApiObtainAuthToken, self).post(request, *args, **kwargs)
        token = Token.objects.get(key=response.data['token'])
        user = User.objects.get(id=token.user_id)
        # context is for obtaining object url so it can build absolute URLs.
        serializer = UserSerializer(user, many=False, context={'request': request})
        return Response({'token': token.key, 'user': serializer.data})

# class FilterProjectView(generics.ListAPIView):
#     serializer_class = ProjectSerializer
#
#     # query params filter
#     def get_queryset(self):
#         queryset = Project.objects.all()
#         user_id = self.request.query_params.get('id', None)
#         if user_id is not None:
#             queryset = queryset.filter(members__user__id=user_id)
#         return queryset
