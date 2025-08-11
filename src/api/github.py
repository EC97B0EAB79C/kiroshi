import logging
import requests
import os


logger = logging.getLogger(__name__)


def get_github_contributions(username, token, year=None):
    logger.debug(f"Fetching contributions for user: {username}")
    result = _graphql_query(username, token, year)

    if result is None:
        logger.debug(f"No contributions found for user: {username}")
        return None

    contributions = result.get("contributionCalendar", {}).get("weeks", [])
    logger.debug(f"Contributions found: {len(contributions)} weeks")

    return contributions


def _graphql_query(username, token, year=None):
    url = "https://api.github.com/graphql"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    query = """
    query GetUserContributions($username: String!, $from: DateTime, $to: DateTime) {
      user(login: $username) {
        contributionsCollection(from: $from, to: $to) {
          contributionCalendar {
            totalContributions
            weeks {
              contributionDays {
                color
                contributionCount
                date
              }
            }
          }
        }
      }
    }
    """
    variables = {"username": username}

    if year:
        from_date = f"{year}-01-01T00:00:00Z"
        to_date = f"{year}-12-31T23:59:59Z"
        variables["from"] = from_date
        variables["to"] = to_date

    payload = {"query": query, "variables": variables}

    try:
        logger.debug(f"> Sending GraphQL request to {url}")
        response = requests.post(url, json=payload, headers=headers)
        logger.debug(f"> Received response: {response.status_code}")

        response.raise_for_status()
        data = response.json()
        if data is None:
            return None
        if data.get("data") is None:
            return None
        if data.get("data").get("user") is None:
            return None

        return data.get("data").get("user").get("contributionsCollection", {})
    except requests.RequestException as e:
        print(f"Error fetching contributions: {e}")
        return None


if __name__ == "__main__":
    username = "TEST_USERNAME"
    token = os.getenv("GITHUB_TOKEN")
    contributions = get_github_contributions(username, token)

    if contributions:
        print(f"Contributions for {username}:")
        for contribution in contributions:
            print(contribution)
    else:
        print(f"No contributions found for {username}.")
