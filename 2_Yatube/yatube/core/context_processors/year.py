from django.utils import timezone


def year(request):
    year_now = timezone.now().year
    return {"year": year_now}
