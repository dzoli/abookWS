from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


# Path to upload profile image to media dir
def path(instance, filename):
    return 'images/{username}/{filename}'.format(
        username=instance.user.username, filename=filename)


# custom user Profile is related to the built-in User used for auth
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.CharField(max_length=80, blank=True)
    workplace = models.CharField(max_length=80, blank=True)
    office = models.CharField(max_length=80, blank=True)
    phone = models.CharField(max_length=80, blank=True)
    address = models.CharField(max_length=80, blank=True)
    personal_web_site = models.CharField(max_length=80, blank=True)
    profile_img = models.ImageField(blank=True, null=True, upload_to=path)

    # def save(self, *args, **kwargs):
    #     print("== saving profile")
    #     print(self.department)
    #     self.department += " aaa "
    #     self.profile_img.upload_to = "asdf/"
    #     super(Profile, self).save(*args, **kwargs)
    def __str__(self):
        return str(self.id)


class Course(models.Model):
    title = models.CharField(max_length=128, blank=True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)


class Project(models.Model):
    title = models.CharField(max_length=128, blank=True)
    label = models.CharField(max_length=128, blank=True)
    project_type = models.CharField(max_length=128, blank=True)
    institutions = models.TextField(blank=True)
    pmf_status = models.CharField(max_length=128, blank=True)
    start_year = models.PositiveIntegerField(blank=True)
    duration = models.PositiveIntegerField(blank=True)
    project_manager = models.CharField(max_length=128, blank=True)  # it's not PMF member?
    web_site = models.CharField(max_length=128, blank=True)
    contact_person = models.CharField(max_length=128, blank=True)  # it's not a PMF member?
    members = models.ManyToManyField(Profile, through='ProjectMembership')
    research_group = models.ForeignKey('ResearchGroup', on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return str(self.id)


class Role(models.Model):
    role_name = models.CharField(max_length=128, blank=True)

    def __str__(self):
        return str(self.id)


class ProjectMembership(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('profile', 'project', 'role')

    def __str__(self):
        return 'id = ' + str(self.id)


class ResearchGroup(models.Model):
    title = models.CharField(max_length=255, blank=True)
    key_words = models.CharField(max_length=255, blank=True)
    research_direction = models.TextField(blank=True)
    group_leader = models.CharField(max_length=255, blank=True)
    members = models.TextField(blank=True)
    goals = models.TextField(blank=True)
    equipment = models.TextField(blank=True)
    cooperation = models.TextField(blank=True)
    web_site = models.CharField(max_length=255, blank=True)
    # project_set
    contact_person = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)
    img_1 = models.ImageField(blank=True, null=True, upload_to=path)
    img_2 = models.ImageField(blank=True, null=True, upload_to=path)
    img_3 = models.ImageField(blank=True, null=True, upload_to=path)
    img_4 = models.ImageField(blank=True, null=True, upload_to=path)


# =========================  SIGNALS ==========================
# Signals that will listen for post_save event from User sender
# create new signal
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


# update signal
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
