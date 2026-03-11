"""
Bunny.net Stream API service.

REST API docs: https://docs.bunny.net/stream/http-api
Embed docs: https://docs.bunny.net/docs/stream-embedding-videos
Token auth: https://docs.bunny.net/stream/token-authentication
"""
from __future__ import annotations

import hashlib
import logging
import time
from typing import Any, BinaryIO, Optional

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

BASE_URL = 'https://video.bunnycdn.com'
EMBED_BASE = 'https://iframe.mediadelivery.net/embed'


class BunnyNetService:

    @staticmethod
    def _headers() -> dict[str, str]:
        return {
            'AccessKey': settings.BUNNY_API_KEY,
            'Accept': 'application/json',
        }

    # ── Embed URLs ──────────────────────────────────────────

    @staticmethod
    def get_embed_url(
        video_id: str,
        library_id: str = '',
        autoplay: bool = False,
        responsive: bool = True,
    ) -> str:
        lib_id = library_id or settings.BUNNY_LIBRARY_ID
        url = f'{EMBED_BASE}/{lib_id}/{video_id}'
        params = []
        if autoplay:
            params.append('autoplay=true')
        if responsive:
            params.append('responsive=true')
        if params:
            url += '?' + '&'.join(params)
        return url

    @staticmethod
    def generate_signed_url(
        video_id: str,
        library_id: str = '',
        expires_hours: int = 24,
    ) -> str:
        """Generate a token-authenticated embed URL (SHA256).

        Falls back to an unsigned embed URL when BUNNY_TOKEN_AUTH_KEY is not set,
        so callers never receive an invalid/predictable token URL.
        """
        lib_id = library_id or settings.BUNNY_LIBRARY_ID
        token_key = settings.BUNNY_TOKEN_AUTH_KEY

        if not token_key:
            return BunnyNetService.get_embed_url(video_id=video_id, library_id=lib_id)

        expires = int(time.time()) + (expires_hours * 3600)

        raw = f'{token_key}{video_id}{expires}'
        token = hashlib.sha256(raw.encode()).hexdigest()

        return (
            f'{EMBED_BASE}/{lib_id}/{video_id}'
            f'?token={token}&expires={expires}'
        )

    # ── Video CRUD ──────────────────────────────────────────

    @staticmethod
    def create_video(
        title: str,
        library_id: str = '',
        collection_id: str = '',
    ) -> Optional[dict[str, Any]]:
        lib_id = library_id or settings.BUNNY_LIBRARY_ID
        url = f'{BASE_URL}/library/{lib_id}/videos'
        payload: dict[str, Any] = {'title': title}
        if collection_id:
            payload['collectionId'] = collection_id

        resp = requests.post(
            url, json=payload, headers=BunnyNetService._headers(), timeout=30,
        )
        if resp.ok:
            return resp.json()
        logger.error('Bunny create_video failed: %s %s', resp.status_code, resp.text)
        return None

    @staticmethod
    def upload_video(
        video_id: str,
        file: BinaryIO,
        library_id: str = '',
    ) -> bool:
        lib_id = library_id or settings.BUNNY_LIBRARY_ID
        url = f'{BASE_URL}/library/{lib_id}/videos/{video_id}'
        headers = BunnyNetService._headers()
        headers['Content-Type'] = 'application/octet-stream'

        resp = requests.put(url, data=file, headers=headers, timeout=600)
        if resp.ok:
            return True
        logger.error('Bunny upload_video failed: %s %s', resp.status_code, resp.text)
        return False

    @staticmethod
    def get_video(
        video_id: str,
        library_id: str = '',
    ) -> Optional[dict[str, Any]]:
        lib_id = library_id or settings.BUNNY_LIBRARY_ID
        url = f'{BASE_URL}/library/{lib_id}/videos/{video_id}'
        resp = requests.get(url, headers=BunnyNetService._headers(), timeout=30)
        if resp.ok:
            return resp.json()
        logger.error('Bunny get_video failed: %s %s', resp.status_code, resp.text)
        return None

    @staticmethod
    def delete_video(
        video_id: str,
        library_id: str = '',
    ) -> bool:
        lib_id = library_id or settings.BUNNY_LIBRARY_ID
        url = f'{BASE_URL}/library/{lib_id}/videos/{video_id}'
        resp = requests.delete(url, headers=BunnyNetService._headers(), timeout=30)
        if resp.ok:
            return True
        logger.error('Bunny delete_video failed: %s %s', resp.status_code, resp.text)
        return False

    @staticmethod
    def list_videos(
        library_id: str = '',
        page: int = 1,
        items_per_page: int = 100,
    ) -> Optional[dict[str, Any]]:
        lib_id = library_id or settings.BUNNY_LIBRARY_ID
        url = f'{BASE_URL}/library/{lib_id}/videos'
        params = {'page': page, 'itemsPerPage': items_per_page}
        resp = requests.get(
            url, params=params, headers=BunnyNetService._headers(), timeout=30,
        )
        if resp.ok:
            return resp.json()
        logger.error('Bunny list_videos failed: %s %s', resp.status_code, resp.text)
        return None

    # ── Collections ─────────────────────────────────────────

    @staticmethod
    def create_collection(
        name: str,
        library_id: str = '',
    ) -> Optional[dict[str, Any]]:
        lib_id = library_id or settings.BUNNY_LIBRARY_ID
        url = f'{BASE_URL}/library/{lib_id}/collections'
        resp = requests.post(
            url, json={'name': name},
            headers=BunnyNetService._headers(), timeout=30,
        )
        if resp.ok:
            return resp.json()
        logger.error('Bunny create_collection failed: %s %s', resp.status_code, resp.text)
        return None
