from django.apps import AppConfig

def ready(self):
    import voteapp.signals  # Replace with your actual app name

class VotingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'voteapp'

    
