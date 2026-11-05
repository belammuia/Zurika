from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.db import transaction
from apps.accounts.models import Profile, OfficerProfile

User = get_user_model()

data = {
    "client": [
        ("client1@zurika.test", "John", "Kamau"),
        ("client2@zurika.test", "Mary", "Wanjiku"),
        ("client3@zurika.test", "Peter", "Mwangi"),
        ("client4@zurika.test", "Grace", "Achieng"),
        ("client5@zurika.test", "David", "Omondi"),
    ],
    "claims_officer": [
        ("officer1@zurika.test", "James", "Maina"),
        ("officer2@zurika.test", "Sarah", "Njeri"),
        ("officer3@zurika.test", "Brian", "Otieno"),
        ("officer4@zurika.test", "Lucy", "Wambui"),
        ("officer5@zurika.test", "Kevin", "Kiptoo"),
    ],
    "senior_officer": [
        ("senior1@zurika.test", "Michael", "Mutua"),
        ("senior2@zurika.test", "Esther", "Nyambura"),
        ("senior3@zurika.test", "Daniel", "Ochieng"),
        ("senior4@zurika.test", "Faith", "Chebet"),
        ("senior5@zurika.test", "Samuel", "Kariuki"),
    ],
    "admin": [
        ("admin1@zurika.test", "Alex", "Muriuki"),
        ("admin2@zurika.test", "Diana", "Atieno"),
        ("admin3@zurika.test", "Victor", "Kamau"),
        ("admin4@zurika.test", "Anne", "Wairimu"),
        ("admin5@zurika.test", "Joseph", "Barasa"),
    ],
}

passwords = {
    "client": "client123",
    "claims_officer": "officer123",
    "senior_officer": "senior123",
    "admin": "admin123",
}


class Command(BaseCommand):
    help = "Create demo users (clients, officers, admins). Dev only."

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError("Refusing to seed demo accounts when DEBUG is off.")

        created = 0
        skipped = 0

        with transaction.atomic():
            for role, people in data.items():
                for email, first, last in people:
                    user, new = User.objects.get_or_create(
                        email=email,
                        defaults={
                            "role": role,
                            "is_active": True,
                            "is_staff": role != "client",
                            "is_superuser": role == "admin",
                        },
                    )

                    if not new:
                        print(f"SKIPPED: {email}")
                        skipped += 1
                        continue

                    user.set_password(passwords[role])
                    user.save()

                    if role in ("claims_officer", "senior_officer"):
                        OfficerProfile.objects.create(
                            officer=user,
                            first_name=first,
                            last_name=last,
                        )
                    else:
                        Profile.objects.create(
                            user=user,
                            first_name=first,
                            last_name=last,
                        )

                    created += 1
                    print(f"CREATED: {email} ({role})")

        print(f"\nCreated: {created}")
        print(f"Skipped: {skipped}")
