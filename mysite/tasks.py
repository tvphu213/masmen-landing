from celery import shared_task
from celery import Celery
from celery.decorators import task
from django.apps import apps
from django.conf import settings

#from blog.models import Server
import docker
client = docker.from_env()
broker_url = settings.CELERY_BROKER_URL
backend_url = settings.CELERY_RESULT_BACKEND

celery = Celery('tasks', backend=backend_url, broker=broker_url)


@task(name="create_image")
def create_image(server_id):
    Server = apps.get_model('blog', 'Server')
    print(server_id)
    server_local = Server.objects.get(pk=server_id)
    password = "admin"
    server_local.state = 'BUILDING'
    server_local.save()
    container = client.containers.create("postgres", detach=True, name=server_local.domain_name, restart_policy={
                                         "Name": "on-failure", "MaximumRetryCount": 5}, environment={'POSTGRES_PASSWORD': server_local.password}, ports={'5432/tcp': None})
    server_local.state = 'BUILT'
    server_local.docker_id = container.id
    server_local.port = 0
    server_local.save()


@task(name="stop_image")
def stop_image(server_id):
    Server = apps.get_model('blog', 'Server')
    server_local = Server.objects.get(pk=server_id)
    container = client.containers.get(server_local.docker_id)
    server_local.state = 'STOPPING'
    server_local.save()
    container.stop()
    server_local.state = 'STOPED'
    server_local.port = 0
    server_local.save()


@task(name="run_image")
def run_image(server_id):
    Server = apps.get_model('blog', 'Server')
    server_local = Server.objects.get(pk=server_id)
    container = client.containers.get(server_local.docker_id)
    server_local.state = 'STARTING'
    server_local.save()
    container.start()
    container.reload()
    ports = container.ports
    server_local.port = 0
    for port in ports['5432/tcp']:
        server_local.port = int(port['HostPort'])
        break
    server_local.state = 'RUNNING'
    server_local.save()


@task(name="remove_image")
def remove_image(docker_id):
    container = client.containers.get(docker_id)
    container.stop()
    container.remove()


@task(name="demo")
def add(x, y):
    return x + y
