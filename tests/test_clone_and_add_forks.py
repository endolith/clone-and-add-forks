import os
import subprocess
import sys
import tempfile

import pytest

from clone_and_add_forks import add_upstream_remote, main


@pytest.fixture
def temp_dir():
    """Create a temporary directory and change to it."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        original_dir = os.getcwd()
        os.chdir(tmpdirname)
        yield tmpdirname
        os.chdir(original_dir)


@pytest.fixture
def argv():
    """Temporarily modify sys.argv and restore it after the test."""
    original_argv = sys.argv
    yield
    sys.argv = original_argv


def test_no_arguments(temp_dir, capsys, argv):
    """Test that the script shows usage when no arguments are given."""
    sys.argv = ['clone_and_add_forks.py']
    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 1

    # Check that usage message was printed
    captured = capsys.readouterr()
    assert "Usage: python clone_and_add_forks.py <repo_url> <username>" in captured.out
    assert "<repo_url>: The full URL of the upstream GitHub repository" in captured.out
    assert "<username>: Your GitHub username" in captured.out


def test_invalid_url(temp_dir, argv):
    """Test that the script handles invalid URLs gracefully."""
    sys.argv = [
        'clone_and_add_forks.py',
        'not_a_url',
        'username'
    ]
    with pytest.raises(ValueError) as exc_info:
        main()
    assert "Invalid GitHub URL" in str(exc_info.value)
    assert "URL must start with 'https://github.com/'" in str(
        exc_info.value)


def test_hello_world_integration(temp_dir, argv):
    """
    Integration test using the famous octocat/Hello-World repository.
    This tests how the script handles a repository with thousands of forks.
    """
    # Set up test arguments
    sys.argv = [
        'clone_and_add_forks.py',
        'https://github.com/octocat/Hello-World',
        'endolith'  # Using your fork
    ]

    # Run the script
    main()

    # Verify the clone worked (using full path)
    repo_path = os.path.join(temp_dir, 'Hello-World')
    assert os.path.exists(repo_path)
    assert os.path.exists(os.path.join(repo_path, '.git'))

    # Check what remotes were added
    os.chdir(repo_path)
    result = subprocess.run(
        ["git", "remote", "-v"],
        capture_output=True, text=True, check=True
    )
    remotes = result.stdout.strip()

    # Print all remotes for inspection
    print("\nRemotes added by script:")
    print(remotes)

    # Basic verification
    assert 'origin' in remotes
    assert 'upstream' in remotes
    assert 'https://github.com/octocat/Hello-World.git' in remotes

    # Count how many remotes were added
    # Each remote appears twice (fetch/push)
    remote_count = len(result.stdout.strip().split('\n')) // 2
    print(f"\nTotal remotes added: {remote_count}")

    # Verify we got a reasonable number of remotes (at least origin + upstream + some forks)
    assert remote_count > 3, "Expected more remotes to be added"


def test_existing_repository(temp_dir, argv):
    """Test that the script handles existing repositories correctly."""
    # First run to create the repo
    sys.argv = [
        'clone_and_add_forks.py',
        'https://github.com/octocat/Hello-World',
        'endolith'
    ]
    main()

    # Capture the initial state
    result = subprocess.run(
        ["git", "remote", "-v"],
        capture_output=True, text=True, check=True
    )
    initial_remotes = set(line.split()[0]
                          for line in result.stdout.strip().split('\n'))

    # Run it again
    main()

    # Verify final state
    result = subprocess.run(
        ["git", "remote", "-v"],
        capture_output=True, text=True, check=True
    )
    final_remotes = set(line.split()[0]
                        for line in result.stdout.strip().split('\n'))

    # Verify that:
    # 1. We have the essential remotes
    assert 'origin' in final_remotes
    assert 'upstream' in final_remotes
    # 2. We didn't lose any remotes
    assert initial_remotes.issubset(final_remotes)
    # 3. Each remote appears exactly twice (fetch and push)
    remote_lines = result.stdout.strip().split('\n')
    assert len(remote_lines) == len(final_remotes) * 2


def test_mismatched_upstream(temp_dir):
    """Test that the script detects mismatched upstream URLs."""

    # Set up a repo with wrong upstream
    os.makedirs('Hello-World')
    os.chdir('Hello-World')
    subprocess.run(['git', 'init'], check=True)
    subprocess.run(['git', 'remote', 'add', 'upstream',
                   'https://github.com/wrong/repo.git'], check=True)

    with pytest.raises(ValueError) as exc_info:
        add_upstream_remote('Hello-World', 'octocat')
    assert "doesn't match expected" in str(exc_info.value)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
