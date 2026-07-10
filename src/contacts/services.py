from helpers import mygoogler
from django.utils import timezone
from .models import Contact


def sync_google_other_contacts(user, max_results=2):
    page_token = None
    total_complete = 0
    while True:
        results = mygoogler.get_my_other_contacts(user, page_token=page_token)
        parsed_results = mygoogler.parse_contact_info(results)
        for contact_data in parsed_results:
            email = contact_data.get("email")
            Contact.objects.update_or_create(
                user=user,
                email=email,
                defaults={
                    "first_name": contact_data.get("first_name") or "",
                    "last_name": contact_data.get("last_name") or "",
                    "last_sync": timezone.now(),
                },
            )
            total_complete += 1
            if total_complete >= max_results:
                return  # early exit if limit reached
        page_token = results.get("nextPageToken")  # use nextPageToken for pagination
        if not page_token:
            break  # no more pages
