from git import Repo
from git.exc import GitCommandError
import subprocess
import os

def checkout_branch(repo_path, branch_name):
    """
    Check out to a specific branch in a Git repository.

    :param repo_path: Path to the local repository
    :param branch_name: Name of the branch to check out
    """
    try:
        # Open the repository
        repo = Repo(repo_path)

        # Ensure it's a Git repository
        if repo.bare:
            print("Repository is empty or not properly initialized.")
            return

        # Fetch the branch to ensure it exists
        print(f"Fetching branches in repository: {repo_path}")
        repo.remotes.origin.fetch() #--Uncomment

        # Checkout to the branch
        if branch_name in repo.heads:
            print(f"Checking out to local branch: {branch_name}")
            repo.git.checkout(branch_name)
        else:
            print(f"Branch {branch_name} not found locally. Attempting to check out remotely...")
            repo.git.checkout(f'origin/{branch_name}', b=branch_name)

        print(f"Successfully checked out to branch: {branch_name}")

    except GitCommandError as e:
        print(f"Git command failed: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")



def add_to_git(repo_path):
    subprocess.run(["git", "add", "."], cwd=repo_path)
    print(f"Git add done")