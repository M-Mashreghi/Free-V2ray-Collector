import git
from datetime import datetime
import os







import git
from datetime import datetime
import os
from urllib.parse import urlparse

def _to_https_url(remote_url: str) -> str:
    """Convert SSH/HTTPS remote to plain HTTPS (no credentials)."""
    if remote_url.startswith("git@github.com:"):
        owner_repo = remote_url.split(":", 1)[1]
        return f"https://github.com/{owner_repo}"
    return remote_url

def _with_token(https_url: str, token: str) -> str:
    """Inject PAT into HTTPS URL."""
    u = urlparse(https_url)
    netloc = f"x-access-token:{token}@{u.netloc}"
    return u._replace(netloc=netloc).geturl()

def update_with_token(remote_name: str = "origin", branch: str | None = None) -> None:
    """Commit & push changes to GitHub using PAT stored in env github_token."""
    token = os.getenv("github_token")
    if not token:
        raise RuntimeError("Environment variable github_token not set!")

    repo_path = os.getcwd()
    repo = git.Repo(repo_path)

    # Stage everything (including deletes)
    repo.git.add(all=True)

    # Commit if there are changes
    if repo.is_dirty(untracked_files=True):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        commit_message = f"✅ {timestamp} ✅"
        repo.index.commit(commit_message)

    # Determine branch
    if repo.head.is_detached:
        default_branch = branch or "main"
    else:
        default_branch = branch or repo.active_branch.name

    remote = repo.remotes[remote_name]
    original_url = remote.url
    https_url = _to_https_url(original_url)
    push_url = _with_token(https_url, token)

    try:
        # Set push URL with token
        remote.set_url(push_url, push=True)

        # Push HEAD to remote branch
        repo.git.push(remote_name, f"HEAD:refs/heads/{default_branch}")
        print(f"Pushed to {remote_name}/{default_branch}.")
    finally:
        # Restore original URL (keep token out of config)
        remote.set_url(original_url, push=True)












def Update():
    # Specify the path to your Git repository
    # repo_path = r'C:\Users\M.M\Documents\GitHub\Free-V2ray-Collector'
    repo_path = os.getcwd()
    # Initialize the Git repository
    repo = git.Repo(repo_path)

    # Check for any changes in the working directory
    if repo.is_dirty():
       # Stage all changes
        repo.index.add('*')

        # Create a commit message with the current date and time and ✅ emoji
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        commit_message = f"✅ {timestamp} ✅"
        repo.index.commit(commit_message)

        # Push the changes to the origin
        origin = repo.remotes['origin']  # Replace 'origin' with the name of your remote
        origin.push()

        print("Changes committed and pushed to the origin.")
    else:
        print("No changes to commit.")
