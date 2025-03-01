import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stajj2.settings')
application = get_wsgi_application()

from users.models import CustomUser
from collections import Counter

def main():
    # Get a list of all email addresses in the CustomUser model
    emails = CustomUser.objects.values_list('email', flat=True)

    # Count the occurrences of each email address
    email_counts = Counter(emails)

    # Identify duplicate email addresses
    duplicates = [email for email, count in email_counts.items() if count > 1]

    # Iterate through duplicates and update email addresses
    for duplicate in duplicates:
        users_with_duplicate = CustomUser.objects.filter(email=duplicate)

        for i, user in enumerate(users_with_duplicate[1:], start=1):
            new_email = f"{user.username}{i}@example.com"
            user.email = new_email
            user.save()

if __name__ == "__main__":
    main()
