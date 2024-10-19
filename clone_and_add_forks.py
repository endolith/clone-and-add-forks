"""
A Python script to clone a GitHub fork as the origin, add the original
repository as upstream, and add all other forks as remotes named by the
fork owner's username.

Created on Mon Jul 8 23:04:52 2024

Author: ChatGPT and endolith
"""
import os
import subprocess
import sys

import requests


def clone_repo(repo_name, username):
    """
    Clone the user's fork of the repository.

    Parameters:
    repo_name (str): The name of the repository.
    username (str): The GitHub username of the user.
    """
    clone_url = f"https://github.com/{username}/{repo_name}.git"
    print(f"Cloning repository from {clone_url}", flush=True)
    subprocess.run(["git", "clone", clone_url], check=True)
    os.chdir(repo_name)


def add_upstream_remote(repo_name, original_owner):
    """
    Add the original repository as upstream.

    Parameters:
    repo_name (str): The name of the repository.
    original_owner (str): The owner of the original repository.
    """
    upstream_url = f"https://github.com/{original_owner}/{repo_name}.git"
    print(f"Adding upstream remote {upstream_url}", flush=True)
    subprocess.run(["git", "remote", "add", "upstream",
                   upstream_url], check=True)
    subprocess.run(["git", "fetch", "upstream"], check=True)


def add_forks_as_remotes(repo_name, original_owner, username):
    """
    Add all forks of the original repository as remotes, named by the
    fork owner's username.

    Parameters:
    repo_name (str): The name of the repository.
    original_owner (str): The owner of the original repository.
    username (str): The GitHub username of the user.
    """
    forks_url = ("https://api.github.com/repos/"
                 f"{original_owner}/{repo_name}/forks")
    print(f"Fetching forks from {forks_url}", flush=True)
    response = requests.get(forks_url)
    forks = response.json()
    for fork in forks:
        fork_owner = fork['owner']['login']
        if fork_owner == username:
            continue
        fork_url = fork['clone_url']
        print("Adding remote for fork owned by "
              f"{fork_owner}: {fork_url}", flush=True)
        subprocess.run(
            ["git", "remote", "add", fork_owner, fork_url], check=True)
    print("All remotes have been added successfully.", flush=True)


def main():
    """
    Main function to clone the repository and add forks as remotes.
    """
    if len(sys.argv) != 3:
        print("Usage: python clone_and_add_forks.py <repo_url> <username>",
              flush=True)
        print("  <repo_url>: The full URL of the upstream GitHub repository "
              "(e.g., https://github.com/owner/repo)")
        print("  <username>: Your GitHub username (the owner of the origin "
              "fork you want to clone)")
        sys.exit(1)

    repo_url = sys.argv[1]
    username = sys.argv[2]

    # Extract original owner and repo name from the URL
    parts = repo_url.split('/')
    original_owner = parts[-2]
    repo_name = parts[-1].replace('.git', '')

    clone_repo(repo_name, username)
    add_upstream_remote(repo_name, original_owner)
    add_forks_as_remotes(repo_name, original_owner, username)


if __name__ == "__main__":
    main()
