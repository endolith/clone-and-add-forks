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
    Clone the user's fork of the repository, or verify existing clone.

    Parameters:
    repo_name (str): The name of the repository.
    username (str): The GitHub username of the user.
    """
    clone_url = f"https://github.com/{username}/{repo_name}.git"
    if os.path.exists(repo_name):
        print(f"Repository {repo_name} already exists, verifying remotes...")
        os.chdir(repo_name)
    else:
        print(f"Cloning repository from {clone_url}\n", flush=True)
        subprocess.run(["git", "clone", clone_url], check=True)
        os.chdir(repo_name)


def add_upstream_remote(repo_name, original_owner):
    """
    Add or verify the original repository as upstream.

    Parameters:
    repo_name (str): The name of the repository.
    original_owner (str): The owner of the original repository.
    """
    upstream_url = f"https://github.com/{original_owner}/{repo_name}.git"

    # Check if upstream remote exists
    result = subprocess.run(["git", "remote", "get-url", "upstream"],
                            capture_output=True, text=True)

    if result.returncode == 0:
        current_upstream = result.stdout.strip()
        if current_upstream != upstream_url:
            raise ValueError(f"Upstream URL {current_upstream} doesn't match "
                             f"expected {upstream_url}")
    else:
        print(f"Adding upstream remote {upstream_url}")
        subprocess.run(["git", "remote", "add", "upstream", upstream_url],
                       check=True)

    subprocess.run(["git", "fetch", "upstream"], check=True)


def add_forks_as_remotes(repo_name, original_owner, username, num_forks=30):
    """
    Add forks of the original repository as remotes, named by the fork owner's
    username.

    Parameters:
    repo_name (str): The name of the repository.
    original_owner (str): The owner of the original repository.
    username (str): The GitHub username of the user.
    num_forks (int or None): Number of forks to add (None for all forks)
    """
    # Get existing remotes
    result = subprocess.run(["git", "remote"], capture_output=True, text=True)
    existing_remotes = set(result.stdout.strip().split('\n'))

    # Get repository info including fork count
    repo_url = f"https://api.github.com/repos/{original_owner}/{repo_name}"
    response = requests.get(repo_url)
    repo_info = response.json()
    total_forks = repo_info['forks_count']

    print(f"\nRepository has {total_forks} forks total.")
    if num_forks is None:
        print("fetching all of them...", flush=True)
        if total_forks > 100:
            response = input(f"Warning: Fetching {total_forks} forks. "
                             "Continue? (y/N) ")
            if response.lower() != 'y':
                print("Aborted.")
                return
    else:
        print(f"Fetching up to {num_forks} forks...", flush=True)

    # Get forks (GitHub API paginates, typically 30 per page)
    forks_url = f"{repo_url}/forks"
    forks_added = 0
    forks_processed = 0
    page = 1

    while True:
        # Fetching page {page} from {forks_url}
        response = requests.get(forks_url, params={'page': page})
        forks = response.json()

        if not forks:  # No more forks to process
            break

        # Processing {len(forks)} forks from page {page}
        for fork in forks:
            fork_owner = fork['owner']['login']
            forks_processed += 1

            # Skip if it's our own fork or if remote already exists
            if fork_owner == username or fork_owner in existing_remotes:
                print(f"Skipping {fork_owner} (already exists)")
                if num_forks is not None and forks_processed >= num_forks:
                    print(f"Processed {num_forks} forks ({forks_added} added, "
                          f"{forks_processed - forks_added} skipped).")
                    return
                continue

            fork_url = fork['clone_url']
            print("Adding remote for fork owned by "
                  f"{fork_owner}: {fork_url}")
            subprocess.run(
                ["git", "remote", "add", fork_owner, fork_url], check=True)
            forks_added += 1
            # Add to set to prevent duplicates
            existing_remotes.add(fork_owner)

            if num_forks is not None and forks_processed >= num_forks:
                print(f"Processed {num_forks} forks ({forks_added} added, "
                      f"{forks_processed - forks_added} skipped).")
                return

        page += 1

    print(f"Added {forks_added} new forks, skipped "
          f"{forks_processed - forks_added}.")


def main():
    """
    Main function to clone the repository and add forks as remotes.
    """
    if len(sys.argv) not in (3, 4):
        print("Usage: clone-and-add-forks <repo_url> <username> [num_forks]")
        print("  <repo_url>: The full URL of the upstream GitHub repository "
              "(e.g., https://github.com/owner/repo)")
        print("  <username>: Your GitHub username "
              "(the owner of the origin fork you want to clone)")
        print("  [num_forks]: Number of forks to add "
              "(default: 30, 'all' for all forks)")
        sys.exit(1)

    repo_url = sys.argv[1]
    username = sys.argv[2]
    num_forks = sys.argv[3] if len(sys.argv) > 3 else '30'

    # Validate URL format
    if not repo_url.startswith('https://github.com/'):
        raise ValueError(f"Invalid GitHub URL: {repo_url}\n"
                         "URL must start with 'https://github.com/'")

    # Extract original owner and repo name from the URL
    parts = repo_url.split('/')
    if len(parts) < 5:  # ['https:', '', 'github.com', 'owner', 'repo']
        raise ValueError(f"Invalid GitHub URL format: {repo_url}\n"
                         "Expected format: https://github.com/owner/repo")

    original_owner = parts[-2]
    repo_name = parts[-1].replace('.git', '')

    # Convert num_forks to integer or None for 'all'
    if num_forks.lower() == 'all':
        num_forks = None
    else:
        try:
            num_forks = int(num_forks)
            if num_forks < 1:
                raise ValueError("Number of forks must be positive")
        except ValueError as e:
            print(f"Invalid number of forks: {num_forks}")
            print("Must be a positive number or 'all'")
            sys.exit(1)

    clone_repo(repo_name, username)
    add_upstream_remote(repo_name, original_owner)
    add_forks_as_remotes(repo_name, original_owner, username, num_forks)


if __name__ == "__main__":
    main()
