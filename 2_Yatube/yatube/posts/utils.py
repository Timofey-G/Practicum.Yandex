from django.conf import settings
from django.core.paginator import Paginator


def paginator(object_list, request):
    paginator = Paginator(object_list, settings.RECORDS_PER_PAGE)
    page_number = request.GET.get("page")
    return paginator.get_page(page_number)
