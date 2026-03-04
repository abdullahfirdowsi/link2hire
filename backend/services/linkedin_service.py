"""
LinkedIn service for job posting integration.
Placeholder implementation for future LinkedIn API integration.
"""

import logging
import os
from typing import Optional
from datetime import datetime, timedelta

import httpx

from backend.config import settings
from backend.models.job_model import JobEntry, LinkedInPost


logger = logging.getLogger(__name__)


class LinkedInService:
    """Service for LinkedIn integration using OAuth2 and UGC Post API."""

    TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"
    ME_URL = "https://api.linkedin.com/v2/me"
    USERINFO_URL = "https://api.linkedin.com/v2/userinfo"
    UGC_POST_URL = "https://api.linkedin.com/v2/ugcPosts"

    def __init__(self):
        self.client_id = settings.linkedin_client_id
        self.client_secret = settings.linkedin_client_secret
        self.redirect_uri = settings.linkedin_redirect_uri

        # In-memory token storage (for demo). Replace with DB/secret manager in prod.
        self.access_token: Optional[str] = None
        self.access_token_expires_at: Optional[datetime] = None
        self.author_urn: Optional[str] = None
        self._load_from_env(force=True)

    def _load_from_env(self, force: bool = False) -> None:
        """Load LinkedIn token/author from env when missing (or force refresh)."""
        env_access_token = (os.getenv("LINKEDIN_ACCESS_TOKEN") or settings.linkedin_access_token or "").strip()
        env_author_urn = (os.getenv("LINKEDIN_AUTHOR_URN") or settings.linkedin_author_urn or "").strip()

        if force or not self.access_token:
            if env_access_token and "..." not in env_access_token:
                self.access_token = env_access_token
                self.access_token_expires_at = datetime.utcnow() + timedelta(days=60)
                logger.info("LinkedIn access token loaded from environment")
            elif env_access_token and "..." in env_access_token:
                logger.warning("Ignoring LINKEDIN_ACCESS_TOKEN containing ellipsis '...' placeholder")

        if force or not self.author_urn:
            if env_author_urn:
                if env_author_urn.startswith("urn:li:person:"):
                    env_author_urn = env_author_urn.replace("urn:li:person:", "urn:li:member:", 1)
                self.author_urn = env_author_urn
                logger.info(f"LinkedIn author URN loaded from environment: {self.author_urn}")

    async def authenticate(self, access_token: Optional[str] = None) -> bool:
        """Validate and store an existing access token."""
        self._load_from_env()
        if access_token:
            self.access_token = access_token
            # Attempt to fetch profile to validate token and populate author URN
            try:
                async with httpx.AsyncClient(timeout=settings.request_timeout) as client:
                    headers = {"Authorization": f"Bearer {self.access_token}"}
                    r = await client.get(self.ME_URL, headers=headers)
                    r.raise_for_status()
                    data = r.json()
                    if "id" in data:
                        self.author_urn = f"urn:li:person:{data['id']}"
                        self.access_token_expires_at = datetime.utcnow() + timedelta(days=60)
                        logger.info("LinkedIn token validated and author URN set")
                        return True
            except httpx.HTTPStatusError as exc:
                logger.error(f"LinkedIn /v2/me failed: status={exc.response.status_code}, body={exc.response.text}")
                return False
            except Exception as exc:
                logger.error(f"Failed to validate LinkedIn token: {exc}")
                return False

        logger.warning("No access token provided for LinkedIn.authenticate")
        return False

    async def handle_oauth_callback(self, authorization_code: str) -> Optional[str]:
        """Exchange authorization code for access token and populate author URN.

        Returns the access token on success.
        """
        if not (self.client_id and self.client_secret and self.redirect_uri):
            logger.error("LinkedIn client configuration missing")
            return None

        data = {
            "grant_type": "authorization_code",
            "code": authorization_code,
            "redirect_uri": self.redirect_uri,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }

        try:
            async with httpx.AsyncClient(timeout=settings.request_timeout) as client:
                # Let httpx handle Content-Type header automatically with data=
                r = await client.post(self.TOKEN_URL, data=data)
                r.raise_for_status()
                token_resp = r.json()

            access_token = token_resp.get("access_token")
            expires_in = token_resp.get("expires_in")

            if not access_token:
                logger.error("LinkedIn token exchange did not return access_token")
                return None

            self.access_token = access_token
            if expires_in:
                self.access_token_expires_at = datetime.utcnow() + timedelta(seconds=int(expires_in))

            # Fetch basic profile to get author URN
            async with httpx.AsyncClient(timeout=settings.request_timeout) as client:
                headers = {"Authorization": f"Bearer {self.access_token}"}
                r = await client.get(self.ME_URL, headers=headers)
                r.raise_for_status()
                profile = r.json()

            if "id" in profile:
                self.author_urn = f"urn:li:person:{profile['id']}"
                logger.info("LinkedIn OAuth completed; author URN set")
            else:
                logger.warning("LinkedIn profile did not return id")

            return self.access_token

        except httpx.HTTPStatusError as exc:
            logger.error(f"LinkedIn token exchange failed: {exc.response.text}")
        except Exception:
            logger.exception("Unexpected error during LinkedIn OAuth callback handling")

        return None

    async def post_job(self, job_entry: JobEntry, linkedin_post: LinkedInPost) -> bool:
        """Publish a simple text UGC post to LinkedIn on behalf of the authenticated user.

        Returns True on success.
        """
        self._load_from_env()
        if not self.access_token or (self.access_token_expires_at and datetime.utcnow() >= self.access_token_expires_at):
            logger.warning("No valid LinkedIn access token available; skipping post")
            return False

        if not self.author_urn:
            logger.error("LinkedIn author URN not configured. Set LINKEDIN_AUTHOR_URN in .env file.")
            logger.info("Format must be: urn:li:member:<numeric_id>")
            return False

        candidate_authors = [self.author_urn]

        token_sub = await self._get_userinfo_sub()
        if token_sub:
            token_person_urn = f"urn:li:person:{token_sub}"
            if token_person_urn not in candidate_authors:
                candidate_authors.append(token_person_urn)

        # De-duplicate while preserving order
        deduped_candidates = []
        for candidate in candidate_authors:
            if candidate and candidate not in deduped_candidates:
                deduped_candidates.append(candidate)

        if not deduped_candidates:
            logger.error("No valid LinkedIn author candidates available")
            return False

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "X-Restli-Protocol-Version": "2.0.0",
            "Content-Type": "application/json"
        }

        last_error_status = None
        last_error_body = None

        for author_urn_for_post in deduped_candidates:
            payload = {
                "author": author_urn_for_post,
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {"text": linkedin_post.post_text},
                        "shareMediaCategory": "NONE"
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                }
            }

            try:
                async with httpx.AsyncClient(timeout=settings.request_timeout) as client:
                    r = await client.post(self.UGC_POST_URL, headers=headers, json=payload)
                    r.raise_for_status()
                    resp = r.json()
                    self.author_urn = author_urn_for_post
                    logger.info(f"LinkedIn post published with author {author_urn_for_post}: {resp.get('id')}")
                    return True
            except httpx.HTTPStatusError as exc:
                last_error_status = exc.response.status_code
                last_error_body = exc.response.text
                logger.warning(
                    f"LinkedIn post failed for author {author_urn_for_post}: "
                    f"status={last_error_status}, body={last_error_body}"
                )
                continue
            except Exception:
                logger.exception("Unexpected error while posting to LinkedIn")
                return False

        logger.error(f"LinkedIn post failed for all author candidates. last_status={last_error_status}, last_body={last_error_body}")
        return False

    async def _get_userinfo_sub(self) -> Optional[str]:
        """Get OIDC subject from LinkedIn userinfo endpoint for token-bound identity."""
        if not self.access_token:
            return None

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "X-Restli-Protocol-Version": "2.0.0",
            "LinkedIn-Version": "202501",
        }

        try:
            async with httpx.AsyncClient(timeout=settings.request_timeout) as client:
                r = await client.get(self.USERINFO_URL, headers=headers)
                r.raise_for_status()
                data = r.json()
                return data.get("sub")
        except Exception:
            return None

    def get_authorization_url(self) -> str:
        """Generate LinkedIn OAuth authorization URL."""
        # Request both posting and profile reading permissions
        scopes = "openid profile w_member_social"
        auth_url = (
            f"https://www.linkedin.com/oauth/v2/authorization"
            f"?response_type=code"
            f"&client_id={self.client_id}"
            f"&redirect_uri={self.redirect_uri}"
            f"&scope={scopes}"
        )
        return auth_url

    def is_configured(self) -> bool:
        """Check if LinkedIn service has valid credentials to post."""
        self._load_from_env()
        has_oauth = bool(self.client_id and self.client_secret and self.redirect_uri)
        has_token = bool(self.access_token)
        return has_oauth or has_token


# Singleton instance
_linkedin_service_instance = None


def get_linkedin_service() -> LinkedInService:
    """Get or create singleton LinkedIn service instance."""
    global _linkedin_service_instance
    if _linkedin_service_instance is None:
        _linkedin_service_instance = LinkedInService()
    return _linkedin_service_instance
