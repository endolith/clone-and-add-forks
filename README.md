# clone_and_add_forks

Clone a GitHub fork as origin, add upstream, and add all other forks as remotes. This essentially mirrors the entire "Network Graph" locally.

## Features

- Clone your fork of a repository as the `origin` remote.
- Add the original repository as the `upstream` remote.
- Automatically add all forks of the original repository as remotes, named as the fork owner's username.

## Usage

```shell
python clone_and_add_forks.py <repo_url> <username>
```

## Example

```shell
λ python clone_and_add_forks\clone_and_add_forks.py https://github.com/pfmonville/whole_history_rating endolith
Cloning repository from https://github.com/endolith/whole_history_rating.git
Cloning into 'whole_history_rating'...
remote: Enumerating objects: 149, done.
remote: Counting objects: 100% (43/43), done.
remote: Compressing objects: 100% (21/21), done.
Receiving objects:  90% (135/149)sed 31 (delta 19), pack-reused 106Receiving objects:  88% (132/149)
Receiving objects: 100% (149/149), 54.02 KiB | 7.72 MiB/s, done.
Resolving deltas: 100% (73/73), done.
Adding upstream remote https://github.com/pfmonville/whole_history_rating.git
remote: Enumerating objects: 2, done.
remote: Counting objects: 100% (2/2), done.
remote: Compressing objects: 100% (2/2), done.
remote: Total 2 (delta 0), reused 2 (delta 0), pack-reused 0
Unpacking objects: 100% (2/2), 300 bytes | 30.00 KiB/s, done.
From https://github.com/pfmonville/whole_history_rating
 * [new branch]      master     -> upstream/master
 * [new tag]         1.6.1      -> 1.6.1
 * [new tag]         1.6.2      -> 1.6.2
Fetching forks from https://api.github.com/repos/pfmonville/whole_history_rating/forks
Adding remote for fork owned by ericwolter: https://github.com/ericwolter/whole_history_rating.git
Adding remote for fork owned by vfg222: https://github.com/vfg222/whole_history_rating.git
Adding remote for fork owned by damienld: https://github.com/damienld/whole_history_rating.git
Adding remote for fork owned by zhaobohan96: https://github.com/zhaobohan96/whole_history_rating.git
Adding remote for fork owned by rymuelle: https://github.com/rymuelle/whole_history_rating.git
Adding remote for fork owned by markpaine: https://github.com/markpaine/whole_history_rating.git
Adding remote for fork owned by glandfried: https://github.com/glandfried/whole_history_rating.git
Adding remote for fork owned by joudinet: https://github.com/joudinet/whole_history_rating.git
Adding remote for fork owned by PaulMainwood: https://github.com/PaulMainwood/whole_history_rating.git
Adding remote for fork owned by domeav: https://github.com/domeav/whole_history_rating.git
Adding remote for fork owned by jesesun: https://github.com/jesesun/whole_history_rating.git
All remotes have been added successfully.
```

## License

This project is licensed under the Unlicense.
