import git
from datetime import datetime
def Update():
    # Specify the path to your Git repository
    repo_path = r'D:\git project\free-config-collector'

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
