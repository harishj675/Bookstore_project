from django.apps import AppConfig


class UserConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'


def ready(self):
    importlib.import_module('users.signals')
