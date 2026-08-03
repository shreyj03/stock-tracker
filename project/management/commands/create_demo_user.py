from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from project.models import Profile


class Command(BaseCommand):
    help = 'Create the demo user (alex_trader) if they do not exist'

    def handle(self, *args, **options):
        username = 'alex_trader'
        password = 'demo1234!'

        user, created = User.objects.get_or_create(username=username)
        if created:
            user.set_password(password)
            user.save()
            Profile.objects.get_or_create(user=user)
            self.stdout.write(self.style.SUCCESS(f'Created demo user: {username}'))
        else:
            self.stdout.write(f'Demo user already exists: {username}')
