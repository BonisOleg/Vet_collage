from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.http import HttpRequest


def site_contact(request: 'HttpRequest') -> dict:
    """Інжектує контактні дані сайту в усі шаблони."""
    try:
        from core.models import SiteContact
        return {'site_contact': SiteContact.load()}
    except Exception:
        return {'site_contact': None}
