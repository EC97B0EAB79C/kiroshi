import logging
from base64 import b64encode
from datetime import datetime, timedelta

from src.api import async_request

logger = logging.getLogger(__name__)

URL = "https://api.track.toggl.com/api/v9"


def _headers(auth: str) -> dict:
    return {"Authorization": f"Basic {b64encode(auth.encode('ascii')).decode('ascii')}"}


async def get_time_entries(auth, start_date, end_date=None) -> list:
    """Return time entries, newest first. Raise on error."""
    logger.debug("Fetching time entries")
    end_date = end_date or (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    params = {"start_date": start_date, "end_date": end_date}
    response = await async_request("GET", f"{URL}/me/time_entries", headers=_headers(auth), params=params)
    return response.json()


async def get_workspace_projects(auth, workspace_id) -> dict:
    """Return the projects of a workspace by project ID. Raise on error."""
    logger.debug(f"Fetching projects for workspace ID: {workspace_id}")
    response = await async_request(
        "GET", f"{URL}/workspaces/{workspace_id}/projects", headers=_headers(auth)
    )
    return {project.get("id"): project for project in response.json() or []}
