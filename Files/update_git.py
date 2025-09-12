# Files/update_git.py
import os, time
from urllib.parse import urlparse
from datetime import datetime
import git
from filelock import FileLock, Timeout  # pip install filelock
import pytz

IRAN_TZ = pytz.timezone("Asia/Tehran")
THREAD_ERR = "getaddrinfo() thread failed to start"

def iran_timestamp(fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    return datetime.now(IRAN_TZ).strftime(fmt)

def _ensure_identity(repo: git.Repo) -> None:
    rw = repo.config_writer()
    try:
        try: repo.config_reader().get_value("user", "name")
        except Exception: rw.set_value("user", "name", os.getenv("GIT_USER_NAME", "automation"))
        try: repo.config_reader().get_value("user", "email")
        except Exception: rw.set_value("user", "email", os.getenv("GIT_USER_EMAIL", "automation@example.com"))
    finally:
        rw.release()

def _remove_stale_index_lock(repo_dir: str, max_age_sec: int = 30*60) -> None:
    lock_path = os.path.join(repo_dir, ".git", "index.lock")
    if not os.path.exists(lock_path):
        return
    try:
        age = time.time() - os.path.getmtime(lock_path)
    except OSError:
        age = max_age_sec + 1
    if age >= max_age_sec:
        os.remove(lock_path)
        print(f"[git] Removed stale index.lock (age {int(age)}s).")
    else:
        raise RuntimeError(f".git/index.lock exists and is recent ({int(age)}s) — another git is likely running.")

def update_with_token(remote_name: str = "origin", branch: str | None = None) -> None:
    if os.getenv("SKIP_PUSH") == "1":
        print("Skipping push because SKIP_PUSH=1"); return

    token = os.getenv("github_token")
    if not token:
        raise RuntimeError("Environment variable github_token not set!")

    repo_dir = os.getcwd()
    proc_lock = FileLock(os.path.join(repo_dir, ".git", "push.lock"))

    try:
        proc_lock.acquire(timeout=10)  # don’t overlap runs
    except Timeout:
        print("Another update is already running; skipping.")
        return

    try:
        _remove_stale_index_lock(repo_dir)

        repo = git.Repo(repo_dir)
        _ensure_identity(repo)

        # Stage & commit
        repo.git.add(all=True)
        if repo.is_dirty(untracked_files=True):
            repo.index.commit(f"✅ {iran_timestamp()} ✅")

        # Determine branch
        default_branch = (branch or
                          (repo.active_branch.name if not repo.head.is_detached else "main"))

        # Fetch + rebase pull
        try:
            os.environ.setdefault("GIT_TERMINAL_PROMPT", "0")
            repo.git.fetch(remote_name)
            repo.git.pull("--rebase", remote_name, default_branch)
        except git.GitCommandError as e:
            msg = str(e.stderr or e)
            if THREAD_ERR in msg:
                print("Low-resources: skipping network Git (will not push)."); return
            if "index.lock" in msg:
                print("Live index.lock during pull; will skip this run."); return
            if "conflict" in msg.lower() or "merge" in msg.lower():
                print("Rebase conflict. Resolve, then: git add -A && git rebase --continue")
                raise

        # Push (token only in push URL)
        remote = repo.remotes[remote_name]
        original = remote.url
        https = original if original.startswith("http") else f"https://github.com/{original.split(':',1)[1]}"
        u = urlparse(https)
        push_url = u._replace(netloc=f"x-access-token:{token}@{u.netloc}").geturl()

        try:
            remote.set_url(push_url, push=True)
            try:
                repo.git.push(remote_name, default_branch)
            except git.GitCommandError:
                repo.git.push(remote_name, f"HEAD:refs/heads/{default_branch}", "-u")
            print(f"Pushed to {remote_name}/{default_branch}.")
        finally:
            remote.set_url(original, push=True)

    finally:
        try: proc_lock.release()
        except Exception: pass

# Legacy alias (so 'from update_git import Update' still works if used elsewhere)
def Update():
    return update_with_token()
