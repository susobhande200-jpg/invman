# FOR MORE REAL TIME PROJECTS VISIT :- https://updategadh.com/ 
# Developed By UPDATEGADH TEAM

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from inventory.models import Profile, Category

class Command(BaseCommand):
    help = "Create a starter admin/staff login and categories without Django Admin."

    def handle(self, *args, **kwargs):
        username = "admin"
        password = "admin123"
        user, created = User.objects.get_or_create(username=username, defaults={"is_staff": False})
        user.set_password(password)
        user.save()
        Profile.objects.get_or_create(user=user, defaults={"role":"ADMIN"})
        for name in ["General","Electronics","Office"]:
            Category.objects.get_or_create(name=name)
        self.stdout.write(self.style.SUCCESS("Starter login: admin / admin123"))
