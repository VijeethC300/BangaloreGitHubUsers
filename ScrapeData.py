## Code to scrape data from GitHub 

import requests
import csv
import pandas as pd
import time  # Import time module

# Used a GitHub token
GITHUB_TOKEN = "TokenDetails"
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}


# Users based on location [User location is passed as parameter]
def get_users_in_location(location, page=1):
    url = f"https://api.github.com/search/users?q=location:{location}+followers:>100&per_page=30&page={page}"
    response = requests.get(url, headers=HEADERS)
    time.sleep(3)  # 3-second delay between each request
    return response.json().get("items", [])


# Fetch user details
def scrape_user_details(username):
    url = f"https://api.github.com/users/{username}"
    response = requests.get(url, headers=HEADERS)
    time.sleep(3)
    return response.json()

# Fetch and save user data all users
def fetch_all_user_data():
    user_data = []

    # Query for both "Bangalore" and "Bengaluru"
    for location in ["Bangalore"]:
        page = 1
        while True:
            users = get_users_in_location(location, page=page)
            if not users:  # If no more users are found, break the loop
                break

            for user in users:
                details = scrape_user_details(user['login'])
                user_data.append({
                    "login": details.get("login", ""),
                    "name": details.get("name", ""),
                    "company": clean_company_name(details.get("company", "")),
                    "location": details.get("location", ""),
                    "email": details.get("email", ""),
                    "hireable": details.get("hireable", ""),
                    "bio": details.get("bio", ""),
                    "public_repos": details.get("public_repos", ""),
                    "followers": details.get("followers", ""),
                    "following": details.get("following", ""),
                    "created_at": details.get("created_at", "")
                })
            print(f"Fetched page {page} for location '{location}'")
            page += 1  # Move to the next page for the current location

    return user_data


# Clean company names
def clean_company_name(company):
    if company:
        company = company.strip().lstrip('@').upper()
    return company or ""


def save_to_csv(data, filename):
    pd.DataFrame(data).to_csv(filename, index=False)

# Fetch repositories for a specific user
def scrape_repo_details(username):
    repos = []
    page = 1
    while True:
        url = f"https://api.github.com/users/{username}/repos?per_page=100&page={page}"  # Max 100 per page
        response = requests.get(url, headers=HEADERS)
        user_repos = response.json()
        time.sleep(4)  # 4-second delay between each request

        if not user_repos or response.status_code != 200:
            break  # No more repos or error

        repos.extend(user_repos)
        if len(repos) >= 500:  # Limit to 500 repos per user
            repos = repos[:500]
            break
        page += 1
    return repos
    
# Fetch repository data for all users in `users.csv`
def fetch_repository_data(user_data):
    repository_data = []

    for user in user_data:
        username = user['login']
        repos = scrape_repo_details(username)
        for repo in repos:
          license_info = repo.get("license")  # Get the license info
          license_name = license_info.get("key", "") if license_info else ""  # Check if license_info is not None
          repository_data.append({
            "login": username,
            "full_name": repo.get("full_name", ""),
            "created_at": repo.get("created_at", ""),
            "stargazers_count": repo.get("stargazers_count", 0),
            "watchers_count": repo.get("watchers_count", 0),
            "language": repo.get("language", ""),
            "has_projects": repo.get("has_projects", False),
            "has_wiki": repo.get("has_wiki", False),
            #"license_name": repo.get("license", {}).get("key", "")
            "license_name": license_name,
            "is_private": repo.get("private", False)  # Add visibility field here
            })
        print(f"Fetched repositories for user: {username}")

    return repository_data


##################################################################

# Scrape Users Data from all page
user_data = fetch_all_user_data()
save_to_csv(user_data, "users.csv")

# Scrape User Repository data
repository_data = fetch_repository_data(user_data)
save_to_csv(repository_data, "repositories.csv")

##################################################################

