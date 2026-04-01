from django.apps import AppConfig


class OffersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name               = 'offers'
    verbose_name       = 'Ofertas'

    def ready(self):
        import offers.signals  # noqa: F401
