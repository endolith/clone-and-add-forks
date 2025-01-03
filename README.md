# clone-and-add-forks

Clones your fork of a repository as the `origin` remote, adds the original repository as the `upstream` remote, and then adds all (or some) forks of the original repository as remotes, named as the fork owner's username.  This essentially mirrors the entire "Network Graph" locally.

## Installation

### Using pipx (recommended)
```shell
pipx install git+https://github.com/endolith/clone-and-add-forks.git
```

### Using pip
```shell
pip install git+https://github.com/endolith/clone-and-add-forks.git
```

## Usage

After installation:
```shell
clone-and-add-forks <repo_url> <username> [num_forks]
```

Or run the script directly:
```shell
python clone_and_add_forks.py <repo_url> <username> [num_forks]
```

Where:

- `<repo_url>`: The full URL of the upstream GitHub repository (e.g., `https://github.com/owner/repo`)
- `<username>`: Your GitHub username (the owner of the origin fork you want to clone)
- `[num_forks]`: Optional. Number of forks to add (default: ~30, use 'all' for all forks)

## Example

```shell
λ clone-and-add-forks https://github.com/octocat/Hello-World.git endolith 8
Cloning repository from https://github.com/endolith/Hello-World.git

Cloning into 'Hello-World'...
remote: Enumerating objects: 7, done.
remote: Total 7 (delta 0), reused 0 (delta 0), pack-reused 7 (from 1)
Receiving objects: 100% (7/7), done.
Adding upstream remote https://github.com/octocat/Hello-World.git
remote: Enumerating objects: 6, done.
remote: Counting objects: 100% (1/1), done.
remote: Total 6 (delta 0), reused 0 (delta 0), pack-reused 5 (from 1)
Unpacking objects: 100% (6/6), 898 bytes | 2.00 KiB/s, done.
From https://github.com/octocat/Hello-World
 * [new branch]      master          -> upstream/master
 * [new branch]      octocat-patch-1 -> upstream/octocat-patch-1
 * [new branch]      test            -> upstream/test

Repository has 2485 forks total.
Fetching up to 8 forks...
Adding remote for fork owned by palvevaibhav: https://github.com/palvevaibhav/Hello-World.git
Adding remote for fork owned by sirflyzoner76zzz: https://github.com/sirflyzoner76zzz/Hello-World.git
Adding remote for fork owned by ruizseh: https://github.com/ruizseh/Hello-World.git
Adding remote for fork owned by n0orw: https://github.com/n0orw/Hello-wor.git
Adding remote for fork owned by RamsesAupart: https://github.com/RamsesAupart/Hello-World.git
Adding remote for fork owned by idforclass: https://github.com/idforclass/Hello-World.git
Skipping endolith (already exists)
Adding remote for fork owned by clementjue: https://github.com/clementjue/Hello-World.git
Processed 8 forks (7 added, 1 skipped).
```
