from django.apps import AppConfig


class SystemNetworkConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.system_network'
    dependent_modules = ['module_system']
    version = '0.0.1-a'
    description = ''
