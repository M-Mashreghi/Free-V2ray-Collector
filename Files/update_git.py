import os
from datetime import datetime
from urllib.parse import urlparse

import git

def _to_https_url(remote_url: str) -> str:
    # Normalize SSH → HTTPS for token injection
    if remote_url.startswith("git@github.com:"):
        owner_repo = remote_url.split(":", 1)[1]
        return f"https://github.com/{owner_repo}"
    return remote_url

def _with_token(https_url: str, token: str) -> str:
    u = urlparse(https_url)
    netloc = f"x-access-token:{token}@{u.netloc}"
    return u._replace(netloc=netloc).geturl()

def _ensure_identity(repo: git.Repo) -> None:
    # Ensure commits won’t fail due to missing user.name/email
    rw = repo.config_writer()
    try:
        try:
            repo.config_reader().get_value("user", "name")
        except Exception:
            rw.set_value("user", "name", os.getenv("GIT_USER_NAME", "automation"))
        try:
            repo.config_reader().get_value("user", "email")
        except Exception:
            rw.set_value("user", "email", os.getenv("GIT_USER_EMAIL", "automation@example.com"))
    finally:
        rw.release()

def _detect_default_branch(repo: git.Repo, remote_name: str = "origin") -> str:
    """Try to detect origin’s default branch (main/master), else fall back."""
    remote = repo.remotes[remote_name]
    # Prefer origin/HEAD target if available
    try:
        head_ref = next(r for r in remote.refs if r.name.endswith("origin/HEAD"))
        target = repo.git.symbolic_ref(head_ref.path, q=True)  # refs/remotes/origin/<name>
        return target.split("/")[-1]
    except StopIteration:
        pass
    # Fallbacks
    remote_heads = {r.remote_head for r in remote.refs if hasattr(r, "remote_head")}
    if "main" in remote_heads:
        return "main"
    if "master" in remote_heads:
        return "master"
    # Last resort: current branch if not detached, else main
    if not repo.head.is_detached:
        return repo.active_branch.name
    return "main"

def update_with_token(remote_name: str = "origin", branch: str | None = None) -> None:
    """
    Stage+commit local changes (if any), pull --rebase to integrate remote,
    and push using a token injected only into the push URL.
    Obeys SKIP_PUSH=1 to allow running without pushing on constrained hosts.
    """
    if os.getenv("SKIP_PUSH") == "1":
        print("Skipping push because SKIP_PUSH=1")
        return

    token = os.getenv("github_token")
    if not token:
        raise RuntimeError("Environment variable github_token not set!")

    repo = git.Repo(os.getcwd())
    _ensure_identity(repo)

    remote = repo.remotes[remote_name]
    original_fetch_url = remote.url
    https_url = _to_https_url(original_fetch_url)
    push_url = _with_token(https_url, token)

    # 1) Make sure we’re on a local branch (not detached)
    default_branch = branch or _detect_default_branch(repo, remote_name)
    if repo.head.is_detached:
        # If remote branch exists, create/switch to local tracking branch
        try:
            repo.git.checkout("-B", default_branch, f"{remote_name}/{default_branch}")
        except git.GitCommandError:
            repo.git.checkout("-B", default_branch)

    # 2) Stage + commit local changes (if any)
    repo.git.add(all=True)
    if repo.is_dirty(untracked_files=True):
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        repo.index.commit(f"✅ {ts} ✅")

    # 3) Pull --rebase to avoid non-fast-forward errors (remote ahead)
    try:
        # Keep fetch URL unauthenticated (public reads); rebase integrates remote work
        repo.git.fetch(remote_name)
        repo.git.pull("--rebase", remote_name, default_branch)
    except git.GitCommandError as e:
        # If conflicts: surface clear message; user must resolve, then re-run
        print("Pull with rebase failed (likely merge conflicts). "
              "Resolve conflicts, then run: git add -A && git rebase --continue")
        raise

    # 4) Temporarily inject token into the push URL only, then push
    try:
        remote.set_url(push_url, push=True)
        try:
            repo.git.push(remote_name, default_branch)
        except git.GitCommandError:
            # First push on a new branch or after upstream change
            repo.git.push(remote_name, f"HEAD:refs/heads/{default_branch}", "-u")
        print(f"Pushed to {remote_name}/{default_branch}.")
    finally:
        # 5) Restore original push URL so the token is not persisted
        remote.set_url(original_fetch_url, push=True)

# Backwards-compatible alias
def Update():
    return update_with_token()
