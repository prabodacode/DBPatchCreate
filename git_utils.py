import subprocess

from git import Repo
from git.exc import GitCommandError


def git_checkout_and_pull(branch_name: str, repo_path: str = '.'):
    try:
        repo = Repo(repo_path)

        # Fetch latest from origin
        repo.remotes.origin.fetch()

        # Checkout the branch (create if not exists locally)
        if branch_name in repo.heads:
            repo.git.checkout(branch_name)
        else:
            repo.git.checkout('-b', branch_name, f'origin/{branch_name}')

        # Pull latest changes
        repo.remotes.origin.pull(branch_name)

        print(f"Checked out and pulled branch '{branch_name}' successfully.")

    except GitCommandError as e:
        print(f"Git error: {e}")
    except Exception as e:
        print(f"Error: {e}")


def add_to_git(repo_path):
    subprocess.run(["git", "add", "."], cwd=repo_path)
    print(f"Git add done")