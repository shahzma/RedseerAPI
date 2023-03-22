from django.apps import AppConfig


class FormapiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'FormAPI'

    def ready(self):  # to make it run only once, add --noreload in run command
        from FormAPI.scheduler import start
        start()
