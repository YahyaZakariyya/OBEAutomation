from django.apps import AppConfig


class ObesystemConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'obesystem'

    def ready(self):
        import obesystem.signals