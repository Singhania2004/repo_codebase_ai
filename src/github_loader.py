from pathlib import Path
from git import Repo


class GitHubLoader:

    def __init__(self, repo_base_dir):
        self.repo_base_dir = Path(repo_base_dir)

    def clone_repo(self, github_url):

        repo_name = github_url.split("/")[-1].replace(".git", "")
        repo_path = self.repo_base_dir / repo_name

        if repo_path.exists():
            print("Repository already exists.")
            return repo_path

        print(f"Cloning {github_url}...")
        Repo.clone_from(github_url, repo_path)

        return repo_path

    def get_python_files(self, repo_path):

        py_files = []

        for path in repo_path.rglob("*.py"):

            if "__pycache__" in str(path):
                continue

            py_files.append(path)

        return py_files