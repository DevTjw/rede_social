from django.conf import settings

def site_info(request):
    return {
        "SITE_NAME": settings.SITE_NAME,
        "SITE_URL": settings.SITE_URL,
        "SITE_SLOGAN": settings.SITE_SLOGAN,
    }
