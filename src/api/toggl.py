import requests
from base64 import b64encode
from datetime import datetime, timedelta


# ----- Me --------------------------------------------------------
def _verify_api_key(auth):
    try:
        data = requests.get(
            "https://api.track.toggl.com/api/v9/me",
            headers={
                "content-type": "application/json",
                "Authorization": "Basic %s"
                % b64encode(auth.encode("ascii")).decode("ascii"),
            },
        )
        return True if data.status_code == 200 else False
    except Exception as e:
        print(f"Error verifying API key: {e}")
        return False


# ----- Time Entries -----------------------------------------------
def _get_current_time_entry(auth):
    try:
        data = requests.get(
            "https://api.track.toggl.com/api/v9/me/time_entries/current",
            headers={
                "content-type": "application/json",
                "Authorization": "Basic %s"
                % b64encode(auth.encode("ascii")).decode("ascii"),
            },
        )
        return data.json()
    except Exception as e:
        print(f"Error fetching current time entry: {e}")
        return None


def _get_time_entries(auth, start_date, end_date=None):
    try:
        end_date = end_date or datetime.now().strftime("%Y-%m-%d")
        params = {"start_date": start_date, "end_date": end_date}

        data = requests.get(
            "https://api.track.toggl.com/api/v9/me/time_entries",
            headers={
                "content-type": "application/json",
                "Authorization": "Basic %s"
                % b64encode(auth.encode("ascii")).decode("ascii"),
            },
            params=params,
        )
        return data.json()
    except Exception as e:
        print(f"Error fetching time entries: {e}")
        return None


# ----- Projects -------------------------------------------------
def _get_workspace_projects(auth, workspace_id):
    try:
        data = requests.get(
            f"https://api.track.toggl.com/api/v9/workspaces/{workspace_id}/projects",
            headers={
                "content-type": "application/json",
                "Authorization": "Basic %s"
                % b64encode(auth.encode("ascii")).decode("ascii"),
            },
        )
        return data.json()
    except Exception as e:
        print(f"Error fetching workspace projects: {e}")
        return None


if __name__ == "__main__":
    auth = "<your_api_key>:api_token"
    print(_verify_api_key(auth))
    time_entry = _get_current_time_entry(auth)
    print(time_entry)
    workspace_projects = _get_workspace_projects(
        auth, time_entry.get("wid", "default_workspace_id")
    )
    projects = {}
    for project in workspace_projects:
        projects[project.get("id")] = project
        print(
            f"name: {project.get('name', 'Unknown')}, color: {project.get('color', 'Unknown')}, client: {project.get('client_name', 'Unknown')}"
        )

    time_entries = _get_time_entries(
        auth, (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    )
    for entry in time_entries:
        project = projects.get(entry.get("pid", ""))
        print(
            f"{entry.get('description')}/{project.get('name', '')}-{project.get('client_name', '')}/{entry.get('duration')}"
        )
