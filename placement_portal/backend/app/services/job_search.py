"""Live remote job search using Remotive's public API (no Adzuna credentials)."""
from __future__ import annotations
import re
from typing import Any
import httpx

TIMEOUT = httpx.Timeout(15.0, connect=5.0)


def _clean(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def _normalise_remotive(row: dict) -> dict:
    return {
        "id": f"remotive-{row.get('id', '')}", "title": _clean(row.get("title")),
        "company": _clean(row.get("company_name")) or "Company not listed",
        "location": _clean(row.get("candidate_required_location")) or "Remote",
        "description": _clean(re.sub(r"<[^>]+>", " ", row.get("description", ""))),
        "url": row.get("url") or "", "salary": _clean(row.get("salary")) or None,
        "job_type": _clean(row.get("job_type")) or "Not specified", "source": "Remotive",
        "posted_at": row.get("publication_date"), "remote": True,
    }


async def search_live_jobs(role: str, location: str = "India", limit: int = 30) -> tuple[list[dict], list[str]]:
    """Fetch actual remote vacancies. AI APIs are used separately for analysis, not invented listings."""
    role = _clean(role)[:100]
    location = _clean(location)[:100]
    limit = max(1, min(int(limit), 50))
    jobs: list[dict] = []
    notes: list[str] = []
    async with httpx.AsyncClient(timeout=TIMEOUT, headers={"User-Agent": "CareerPilot student project job discovery"}) as client:
        try:
            response = await client.get("https://remotive.com/api/remote-jobs", params={"search": role, "limit": limit})
            response.raise_for_status()
            payload = response.json()
            for item in payload.get("jobs", []):
                job = _normalise_remotive(item)
                eligible_location = job["location"].lower()
                if location and location.lower() not in ("any", "anywhere", "remote"):
                    if not any(x in eligible_location for x in (location.lower(), "worldwide", "anywhere", "all countries")):
                        continue
                if job["url"]:
                    jobs.append(job)
        except (httpx.HTTPError, ValueError) as exc:
            notes.append(f"Remotive remote-job search unavailable: {type(exc).__name__}. Try again later.")
    unique = {}
    for job in jobs:
        unique.setdefault((job["title"].lower(), job["company"].lower()), job)
    if not unique:
        notes.append("No matching remote vacancies were returned. This source does not provide a comprehensive India-based on-site job feed.")
    return list(unique.values())[:limit], notes
