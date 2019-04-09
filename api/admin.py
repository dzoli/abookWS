from django.contrib import admin
from .models import Profile, Project, Role, ProjectMembership, ResearchGroup, Course

admin.site.register(Profile)

admin.site.register(Project)

admin.site.register(Role)

admin.site.register(ProjectMembership)

admin.site.register(ResearchGroup)

admin.site.register(Course)
