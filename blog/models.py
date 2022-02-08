import os

from django.db import models
from django.core.validators import RegexValidator
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.core import serializers
from django.dispatch import receiver

from mysite.tasks import create_image, stop_image, run_image, remove_image

from django.conf import settings



class Company(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    companyName = models.TextField()
    maxUserNumber = models.SmallIntegerField()
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True) # validators should be a list
    location = models.TextField(default=None, blank=True, null=True)
    def __str__(self):
        ret = self.companyName
        return ret

class Server(models.Model):

    class ServerStatus(models.TextChoices):
            BUILD_REQUIRED = 'BUILD_REQUIRED', _('Build required')
            BUILDING = 'BUILDING', _('Building')
            BUILT = 'BUILT', _('Built')

            STOP_REQUIRED = 'STOP_REQUIRED', 'Stop required'
            STOPPING = 'STOPPING', _('Stopping')
            STOPED = 'STOPED', _('Stoped')

            RUNNING_REQUIRED = 'RUNNING_REQUIRED', _('Running required')
            STARTING = 'STARTING', _('Starting')
            RUNNING = 'RUNNING', _('Running')
            
            UNKNOWN = 'UNKNOWN', _('Unknown')

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    state = models.CharField(
        max_length=20,
        choices=ServerStatus.choices,
        default=ServerStatus.BUILD_REQUIRED,
    )
    docker_id = models.TextField(max_length=100, blank=True, unique=True)
    domain_regex = RegexValidator(regex=r'^((?!-))(xn--)?[a-z0-9][a-z0-9-_]{0,61}[a-z0-9]{0,1}\.(xn--)?([a-z0-9\-]{1,61}|[a-z0-9-]{1,30}\.[a-z]{2,})$', message="Incorrect domain_name")
    domain_name = models.CharField(validators=[domain_regex], max_length=100, unique=True, null=False)
    password = models.TextField(max_length=100, blank=False, default = 'admin')
    port = models.IntegerField(default = 0, blank=False)

    def __str__(self):
        return self.domain_name + ' (' + self.docker_id + ')'

    def does_string_exist(self, string_to_find, filepath):
        result = False
        with open(filepath) as myfile:
            if string_to_find in myfile.read():
                result = True
        return result

    def delete_file_from_file(self, string_to_find, filepath):
        result = False
        with open(filepath, "r+") as f:
            d = f.readlines()
            f.seek(0)
            for i in d:
                if not (string_to_find in i):
                    f.write(i)
            f.truncate()
        return result

    def save(self, *args, **kwargs):
        result = super(Server, self).save(*args, **kwargs)
        if self.state == self.ServerStatus.BUILD_REQUIRED:
            create_image.delay(self.id)
        if self.state == self.ServerStatus.STOP_REQUIRED:
            stop_image.delay(self.id)
        if self.state == self.ServerStatus.RUNNING_REQUIRED:
            run_image.delay(self.id)

        docker_id = self.docker_id
        print(os.getcwd())
        reverse_filepath = os.path.join(settings.MASMEN_CONFIG_FOLDER, settings.MASMEN_CONFIG_REVERSE)
        forward_filepath = os.path.join(settings.MASMEN_CONFIG_FOLDER, settings.MASMEN_CONFIG_FORWARD)
        reverse_exist = self.does_string_exist(docker_id, reverse_filepath)
        forward_exist = self.does_string_exist(docker_id, forward_filepath)
        if not reverse_exist:
            num_lines = sum(1 for line in open(reverse_filepath))
            line_for_reverse = "\n" + str(num_lines) + "  IN      PTR    " + docker_id + "." + settings.MASMEN_DOMAIN_NAME + ".\n" 
            file_object = open(reverse_filepath, 'a')
            file_object.write(line_for_reverse)
            file_object.close()

        if not forward_exist:
            file_object = open(forward_filepath, 'a')
            line_for_forward = "\n" + docker_id + "  IN       A      " + settings.MASMEN_IP + "\n"
            file_object.write(line_for_forward)
            file_object.close()

        return result


    def delete(self):
        reverse_filepath = os.path.join(settings.MASMEN_CONFIG_FOLDER, settings.MASMEN_CONFIG_REVERSE)
        forward_filepath = os.path.join(settings.MASMEN_CONFIG_FOLDER, settings.MASMEN_CONFIG_FORWARD)
        self.delete_file_from_file(self.docker_id, forward_filepath)
        self.delete_file_from_file(self.docker_id, reverse_filepath)
        super(Server, self).delete()

@receiver(models.signals.post_delete, sender=Server)
def delete_file(sender, instance, *args, **kwargs):
    if instance.docker_id:
        remove_image.delay(instance.docker_id)
