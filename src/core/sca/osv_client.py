import httpx
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class OSVClient:
    """Client for downloading Open Source Vulnerabilities (OSV.dev) database."""

    BASE_URL = "https://osv-vulnerabilities.storage.googleapis.com"

    def fetch_ecosystem(self, ecosystem: str) -> Dict[str, Any]:
        """Fetch zip archive for an ecosystem (e.g. PyPI, npm)."""
        url = f"{self.BASE_URL}/{ecosystem}/all.zip"
        try:
            logger.info(f"Downloading OSV definitions from {url}")
            response = httpx.get(url, timeout=30.0)
            response.raise_for_status()
            return {"status": "success", "ecosystem": ecosystem, "url": url, "size": len(response.content)}
        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch OSV definitions: {e}")
            return {"status": "error", "error": str(e)}

    def query_vulnerability(self, package_name: str, version: str, ecosystem: str) -> Dict[str, Any]:
        """Query OSV API for a specific package version."""
        url = "https://api.osv.dev/v1/query"
        payload = {
            "version": version,
            "package": {
                "name": package_name,
                "ecosystem": ecosystem
            }
        }
        try:
            logger.info(f"Querying OSV for {package_name} {version} ({ecosystem})")
            response = httpx.post(url, json=payload, timeout=10.0)
            response.raise_for_status()
            return {"status": "success", "data": response.json()}
        except httpx.HTTPError as e:
            logger.error(f"Failed to query OSV API for {package_name}: {e}")
            return {"status": "error", "error": str(e)}
