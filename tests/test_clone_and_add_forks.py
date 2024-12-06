import os
import subprocess
import sys
import tempfile

import pytest

# Verify that pytest-timeout is installed
try:
    import pytest_timeout
except ImportError:
    pytest.fail("pytest-timeout is required for these tests to prevent infinite downloads")

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


def get_unique_remotes():
    """Get the set of unique remote names from git remote -v output."""
    result = subprocess.run(
        ["git", "remote", "-v"],
        capture_output=True, text=True, check=True
    )
    # Each remote appears twice (fetch/push)
    remote_lines = result.stdout.strip().split('\n')
    unique_remotes = set(line.split()[0] for line in remote_lines)
    # Verify each remote appears exactly twice
    assert len(remote_lines) == len(unique_remotes) * 2
    return unique_remotes


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
    assert "URL must start with 'https://github.com/'" in str(exc_info.value)


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
    unique_remotes = get_unique_remotes()

    # Basic verification
    assert 'origin' in unique_remotes
    assert 'upstream' in unique_remotes
    # Should have upstream + origin + up to 30 forks, depending on whether
    # user's fork was in the first 30
    assert 31 <= len(unique_remotes)


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
    initial_remotes = get_unique_remotes()

    # Run it again
    main()

    # Verify final state
    final_remotes = get_unique_remotes()

    # Verify that:
    # 1. We have the essential remotes
    assert 'origin' in final_remotes
    assert 'upstream' in final_remotes
    # 2. We didn't lose any remotes
    assert initial_remotes.issubset(final_remotes)


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


def test_custom_fork_count(temp_dir, argv):
    """Test that the script respects custom fork count."""
    from clone_and_add_forks import main

    # Set up test with custom fork count
    sys.argv = [
        'clone_and_add_forks.py',
        'https://github.com/octocat/Hello-World',
        'endolith',
        '5'  # Only get 5 forks
    ]
    main()

    # Check what remotes were added
    unique_remotes = get_unique_remotes()

    # Should have upstream, origin, and 4 or 5 forks (depending on whether
    # user's fork was in the first 5)
    assert 6 <= len(unique_remotes) <= 7
    assert 'origin' in unique_remotes
    assert 'upstream' in unique_remotes


def test_invalid_fork_count(temp_dir, argv):
    """Test that the script handles invalid fork counts properly."""
    from clone_and_add_forks import main

    # Test negative number
    sys.argv = [
        'clone_and_add_forks.py',
        'https://github.com/octocat/Hello-World',
        'endolith',
        '-1'
    ]
    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 1

    # Test non-numeric value
    sys.argv = [
        'clone_and_add_forks.py',
        'https://github.com/octocat/Hello-World',
        'endolith',
        'invalid'
    ]
    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 1

@pytest.mark.timeout(15)
def test_all_forks_prompt(temp_dir, argv, monkeypatch):
    """Test that the script prompts for confirmation when fetching all forks."""
    from clone_and_add_forks import main

    # Mock the input function to simulate user saying 'n' to the prompt
    monkeypatch.setattr('builtins.input', lambda _: 'n')

    sys.argv = [
        'clone_and_add_forks.py',
        'https://github.com/octocat/Hello-World',
        'endolith',
        'all'
    ]

    # Should exit gracefully when user declines
    main()

    # Verify only essential remotes were added
    unique_remotes = get_unique_remotes()

    # Should only have origin and upstream
    assert len(unique_remotes) == 2
    assert 'origin' in unique_remotes
    assert 'upstream' in unique_remotes


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
