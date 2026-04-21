"""Site-wide middleware for Marketly."""
from __future__ import annotations

from django.conf import settings
from django.utils import translation


class PreferredLanguageMiddleware:
    """Honor the user's saved language preference for authenticated users.

    Falls back to the session, cookie, or request Accept-Language otherwise.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, "user", None)
        language = None
        if user and user.is_authenticated:
            profile = getattr(user, "profile", None)
            language = getattr(profile, "preferred_language", None)
        if not language:
            language = request.COOKIES.get("preferred_language") or request.session.get(
                "preferred_language"
            )
        if language and any(language == code for code, _ in settings.LANGUAGES):
            translation.activate(language)
            request.LANGUAGE_CODE = language
        return self.get_response(request)
