from django.apps import AppConfig
from django.db.models.signals import post_migrate


def create_default_users(sender, **kwargs):
    """
    Ensure the standard role accounts always exist:
    1. Super Admin: admin / 12345 (is_superuser=True)
    2. Franchise Admin: franchise / 12345
    3. School Admin: school / 12345
    """
    from django.contrib.auth.models import User
    try:
        # 1. Superuser
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'aarav.singhal@source2destination.in',
                'first_name': 'Aarav',
                'last_name': 'Singhal',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created or not admin_user.has_usable_password():
            admin_user.set_password('12345')
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.save()

        # 2. Franchise Admin
        franchise_user, created = User.objects.get_or_create(
            username='franchise',
            defaults={
                'email': 'v.singhania@northedunet.in',
                'first_name': 'Vikramaditya',
                'last_name': 'Singhania',
            }
        )
        if created or not franchise_user.has_usable_password():
            franchise_user.set_password('12345')
            franchise_user.is_staff = False
            franchise_user.is_superuser = False
            franchise_user.save()

        # 3. School Admin
        school_user, created = User.objects.get_or_create(
            username='school',
            defaults={
                'email': 'principal@doonvalley.edu.in',
                'first_name': 'Dr. Ramesh',
                'last_name': 'Sharma',
            }
        )
        if created or not school_user.has_usable_password():
            school_user.set_password('12345')
            school_user.is_staff = False
            school_user.is_superuser = False
            school_user.save()
    except Exception:
        pass


class Source2DestinationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Source2Destination'

    def ready(self):
        post_migrate.connect(create_default_users, sender=self)
