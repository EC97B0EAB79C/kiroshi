import logging

from src.api import request

logger = logging.getLogger(__name__)

URL = "https://api.github.com/graphql"
QUERY = """
query GetUserContributions($username: String!, $from: DateTime, $to: DateTime) {
  user(login: $username) {
    contributionsCollection(from: $from, to: $to) {
      contributionCalendar {
        weeks {
          contributionDays {
            color
            date
          }
        }
      }
    }
  }
}
"""


def get_github_contributions(username, token, year=None) -> list:
    """Return the contribution weeks of a user. Raise on error."""
    logger.debug(f"Fetching contributions for user: {username}")
    variables = {"username": username}
    if year:
        variables["from"] = f"{year}-01-01T00:00:00Z"
        variables["to"] = f"{year}-12-31T23:59:59Z"

    data = request(
        "POST",
        URL,
        json={"query": QUERY, "variables": variables},
        headers={"Authorization": f"Bearer {token}"},
    ).json()

    user = (data.get("data") or {}).get("user")
    if user is None:
        raise ValueError(f"GitHub user not found: {username} ({data.get('errors')})")

    weeks = user["contributionsCollection"]["contributionCalendar"]["weeks"]
    logger.debug(f"Contributions found: {len(weeks)} weeks")
    return weeks
