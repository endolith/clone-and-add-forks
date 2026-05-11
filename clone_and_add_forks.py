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
from urllib.parse import urlparse

import requests


def _strip_git_suffix(path_component):
    return path_component[:-4] if path_component.endswith(".git") else path_component


def parse_github_owner_repo(remote_url):
    """
    Return (owner, repo_name) from a GitHub https or SSH remote URL.

    HTTPS URLs may include credentials (for example token helpers); parsing uses
    urlparse so netloc userinfo does not break owner/repo detection.
    """
    url = remote_url.strip()
    if url.startswith("git@github.com:"):
        path = _strip_git_suffix(url.split("git@github.com:", 1)[1])
        parts = path.split("/")
        if len(parts) != 2:
            raise ValueError(f"Could not parse GitHub repository from URL: "
                             f"{remote_url!r}")
        return parts[0], parts[1]

    parsed = urlparse(url)
    if parsed.scheme in ("http", "https") and parsed.hostname == "github.com":
        segments = [s for s in parsed.path.split("/") if s]
        if len(segments) < 2:
            raise ValueError(f"Could not parse GitHub repository from URL: "
                             f"{remote_url!r}")
        owner = segments[0]
        repo = _strip_git_suffix(segments[1])
        return owner, repo

    raise ValueError(f"Unsupported GitHub remote URL format: {remote_url!r}")


def get_git_toplevel():
    """Return absolute path to git root, or None if not inside a repository."""
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def get_remote_url(remote_name):
    """Return URL for named remote, or None if missing."""
    result = subprocess.run(
        ["git", "remote", "get-url", remote_name],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def canonical_repo_from_github_api(owner, repo_name):
    """
    Return (original_owner, repo_name) for fork-network discovery.

    If the repo is a fork, use its parent; otherwise use the repo itself.
    """
    api_url = f"https://api.github.com/repos/{owner}/{repo_name}"
    response = requests.get(api_url)
    response.raise_for_status()
    data = response.json()
    parent = data.get("parent")
    if data.get("fork") and parent is not None:
        full = parent["full_name"]
        original_owner, name = full.split("/", 1)
        return original_owner, name
    return owner, repo_name


def resolve_canonical_repo_from_git():
    """
    Determine upstream owner and repo name using `upstream`, or `origin`
    plus GitHub API when `upstream` is absent (fork parent or non-fork root).
    """
    upstream_url = get_remote_url("upstream")
    if upstream_url is not None:
        return parse_github_owner_repo(upstream_url)

    origin_url = get_remote_url("origin")
    if origin_url is None:
        raise ValueError(
            "No upstream or origin remote found; add upstream or pass "
            "the upstream repository URL."
        )

    owner, repo_name = parse_github_owner_repo(origin_url)
    return canonical_repo_from_github_api(owner, repo_name)


def infer_username_from_origin():
    """Return GitHub login from origin remote URL."""
    origin_url = get_remote_url("origin")
    if origin_url is None:
        raise ValueError(
            "Cannot infer username: no origin remote. Pass your GitHub "
            "username on the command line."
        )
    owner, _repo = parse_github_owner_repo(origin_url)
    return owner


def looks_like_num_forks(token):
    return token.lower() == "all" or (
        token.isdigit() and int(token) >= 1
    )


def parse_cli_args(argv):
    """
    Parse argv into (repo_url, username, num_forks_token).

    github.com URL if present must be the first argument. Remaining tokens are
    username and/or fork count.
    """
    args = argv[1:]
    if not args:
        return None, None, "30"

    repo_url = None
    if args[0].startswith("https://github.com/"):
        repo_url = args[0]
        rest = args[1:]
    else:
        rest = args[:]

    if len(rest) > 2:
        raise ValueError(
            "Too many arguments. Expected: [<repo_url>] [<username>] "
            "[<num_forks|all>]"
        )

    if not rest:
        return repo_url, None, "30"

    if len(rest) == 1:
        if looks_like_num_forks(rest[0]):
            return repo_url, None, rest[0]
        return repo_url, rest[0], "30"

    return repo_url, rest[0], rest[1]


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
        actual_owner, actual_repo = parse_github_owner_repo(current_upstream)
        if actual_owner != original_owner or actual_repo != repo_name:
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


def print_usage():
    print("Usage: clone-and-add-forks [<repo_url>] [<username>] "
          "[<num_forks>]")
    print("  <repo_url>: Optional. Full URL of the upstream GitHub repository "
          "(e.g., https://github.com/owner/repo). Omit when running inside "
          "an existing clone (upstream/origin identify the project).")
    print("  <username>: Optional if origin points at your fork; your GitHub "
          "username (owner of the fork used as origin). Required when cloning "
          "a new repository without an existing origin.")
    print("  <num_forks>: Number of forks to add "
          "(default: 30, 'all' for all forks)")


def main():
    """
    Main function to clone the repository and add forks as remotes.
    """
    starting_cwd = os.getcwd()

    if len(sys.argv) > 1:
        raw_first = sys.argv[1]
        if raw_first.startswith(("http://", "https://")) and (
                not raw_first.startswith("https://github.com/")):
            raise ValueError(f"Invalid GitHub URL: {raw_first}\n"
                             "URL must start with 'https://github.com/'")

    try:
        repo_url, username, num_forks_arg = parse_cli_args(sys.argv)
    except ValueError as e:
        print(str(e), file=sys.stderr)
        print_usage()
        sys.exit(1)

    git_root = get_git_toplevel()

    if repo_url is None and git_root is None:
        print("Specify the upstream repository URL, or run this command "
              "inside an existing Git clone.", file=sys.stderr)
        print_usage()
        sys.exit(1)

    # Extract original owner and repo name from URL or from git remotes/API
    if repo_url is not None:
        parts = repo_url.split('/')
        original_owner = parts[-2]
        repo_name = _strip_git_suffix(parts[-1])
    else:
        original_owner, repo_name = resolve_canonical_repo_from_git()

    # Convert num_forks to integer or None for 'all'
    if num_forks_arg.lower() == 'all':
        num_forks = None
    else:
        try:
            num_forks = int(num_forks_arg)
            if num_forks < 1:
                raise ValueError("Number of forks must be positive")
        except ValueError:
            print(f"Invalid number of forks: {num_forks_arg}")
            print("Must be a positive number or 'all'")
            sys.exit(1)

    repo_dir = None
    if repo_url is not None:
        nested = os.path.join(starting_cwd, repo_name)
        if os.path.isdir(os.path.join(nested, '.git')):
            repo_dir = nested
        elif (git_root is not None
              and os.path.basename(git_root.rstrip(os.sep)) == repo_name):
            repo_dir = git_root
        else:
            repo_dir = nested
        need_clone = not os.path.isdir(os.path.join(repo_dir, '.git'))
    else:
        repo_dir = git_root
        need_clone = False

    if username is None:
        if need_clone:
            print("Cannot infer username when cloning a new repository; "
                  "pass your GitHub username as <username>.",
                  file=sys.stderr)
            sys.exit(1)
        infer_base = repo_dir
        if infer_base is None or not os.path.isdir(
                os.path.join(infer_base, '.git')):
            print("Could not locate repository directory for username "
                  "inference.", file=sys.stderr)
            sys.exit(1)
        old_cwd = os.getcwd()
        try:
            os.chdir(infer_base)
            username = infer_username_from_origin()
        except ValueError as e:
            print(str(e), file=sys.stderr)
            sys.exit(1)
        finally:
            os.chdir(old_cwd)

    if repo_url is not None:
        if need_clone:
            parent = os.path.dirname(repo_dir.rstrip(os.sep))
            os.chdir(parent)
            clone_repo(repo_name, username)
        else:
            os.chdir(repo_dir)
    else:
        os.chdir(git_root)

    add_upstream_remote(repo_name, original_owner)
    add_forks_as_remotes(repo_name, original_owner, username, num_forks)


if __name__ == "__main__":
    main()
