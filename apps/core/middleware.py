"""Site-wide middleware for Marketly."""
from __future__ import annotations

from django.conf import settings
from django.utils import translation
from django.utils.translation.trans_real import get_language_from_path


class PreferredLanguageMiddleware:
    """Honor the user's saved language preference for authenticated users.

    Falls back to the session, cookie, or request Accept-Language otherwise.
    A language prefix in the URL (e.g. ``/fr/services/``) always wins so that
    the i18n URL resolver can strip it correctly.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # If the URL already carries a language prefix, let LocaleMiddleware's
        # activation stand — overriding it here would make LocalePrefixPattern
        # mismatch the path and return 404.
        if get_language_from_path(request.path_info):
            return self.get_response(request)

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
