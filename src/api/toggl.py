import logging
import requests
from base64 import b64encode
from datetime import datetime, timedelta


logger = logging.getLogger(__name__)


# ----- Me --------------------------------------------------------
def verify_api_key(auth):
    logger.debug("Verifying API key")

    try:
        logger.debug("> Sending request to Toggl API (api/v9/me)")
        data = requests.get(
            "https://api.track.toggl.com/api/v9/me",
            headers={
                "content-type": "application/json",
                "Authorization": "Basic %s"
                % b64encode(auth.encode("ascii")).decode("ascii"),
            },
        )
        logger.debug(f"> API response status code: {data.status_code}")

        return (
            data.json().get("default_workspace_id") if data.status_code == 200 else None
        )
    except Exception as e:
        logger.error(f"> Error verifying API key: {e}")
        return None


# ----- Time Entries -----------------------------------------------
def get_time_entries(auth, start_date, end_date=None):
    logger.debug(f"Fetching time entries.")

    end_date = end_date or (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    params = {"start_date": start_date, "end_date": end_date}

    try:
        logger.debug("> Sending request to Toggl API (api/v9/me/time_entries)")
        data = requests.get(
            "https://api.track.toggl.com/api/v9/me/time_entries",
            headers={
                "content-type": "application/json",
                "Authorization": "Basic %s"
                % b64encode(auth.encode("ascii")).decode("ascii"),
            },
            params=params,
        )
        logger.debug(f"> API response status code: {data.status_code}")

        return data.json()
    except Exception as e:
        logger.error(f"> Error fetching time entries: {e}")
        return []


# ----- Projects -------------------------------------------------
def get_workspace_projects(auth, workspace_id):
    logger.debug(f"Fetching projects for workspace ID: {workspace_id}")
    try:
        logger.debug(
            "> Sending request to Toggl API (api/v9/workspaces/{workspace_id}/projects)"
        )
        data = requests.get(
            f"https://api.track.toggl.com/api/v9/workspaces/{workspace_id}/projects",
            headers={
                "content-type": "application/json",
                "Authorization": "Basic %s"
                % b64encode(auth.encode("ascii")).decode("ascii"),
            },
        )
        logger.debug(f"> API response status code: {data.status_code}")

        projects = {}
        for project in data.json():
            projects[project.get("id")] = project
        return projects
    except Exception as e:
        logger.error(f"> Error fetching workspace projects: {e}")
        return {}


if __name__ == "__main__":
    auth = "<your_api_key>:api_token"
    print(verify_api_key(auth))
    projects = get_workspace_projects(auth, 9165417)

    time_entries = get_time_entries(
        auth, (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    )
    for entry in time_entries:
        project = projects.get(entry.get("pid", ""))
        print(
            f"{entry.get('description')}/{project.get('name', '')}-{project.get('client_name', '')}/{entry.get('duration')}"
        )
