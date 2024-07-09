"""
Here's a Python script that accomplishes the task of cloning your GitHub fork
as origin, adding the original repository as upstream, and adding all other
forks as remotes named by the fork owner's username.

Created on Mon Jul  8 23:04:52 2024

@author: ChatGPT and endolith
"""
import os
import subprocess
import sys

import requests


def run_command(command):
    result = subprocess.run(command, shell=True,
                            capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error running command: {command}")
        print(result.stderr)
        sys.exit(1)
    return result.stdout.strip()


def clone_repo(upstream_url, username):
    repo_name = upstream_url.split('/')[-1].replace('.git', '')
    clone_url = f"git@github.com:{username}/{repo_name}.git"
    run_command(f"git clone {clone_url}")
    os.chdir(repo_name)
    run_command(f"git remote add upstream {upstream_url}")
    run_command("git fetch upstream")
    return repo_name


def add_forks_as_remotes(upstream_url):
    original_owner = upstream_url.split('/')[-2]
    repo_name = upstream_url.split('/')[-1].replace('.git', '')
    forks_url = f"https://api.github.com/repos/{
        original_owner}/{repo_name}/forks"
    response = requests.get(forks_url)
    forks = response.json()
    for fork in forks:
        fork_owner = fork['owner']['login']
        fork_url = fork['clone_url']
        run_command(f"git remote add {fork_owner} {fork_url}")
    print("All remotes have been added successfully.")


def main():
    if len(sys.argv) != 3:
        print("Usage: python clone_and_add_forks.py "
              "<upstream_url> <github_username>")
        sys.exit(1)

    upstream_url = sys.argv[1]
    github_username = sys.argv[2]

    clone_repo(upstream_url, github_username)
    add_forks_as_remotes(upstream_url)


if __name__ == "__main__":
    main()
