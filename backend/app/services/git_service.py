import os
from typing import List, Dict, Any, Optional
from git import Repo, Commit
import tempfile
import shutil

class GitService:
    def __init__(self):
        self.temp_dir = None
        self.repo = None

    async def get_commits_after(
        self,
        current_commit: str,
        source_files: List[str],
        repository_url: Optional[str] = None,
        local_directory: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all commits after the specified commit that modified the given source files.
        """
        try:
            if repository_url:
                if local_directory:
                    # Use specified local directory
                    if os.path.exists(local_directory):
                        print(f"Using existing repository in: {local_directory}")
                        self.repo = Repo(local_directory)
                        # Update the repository if it exists
                        try:
                            origin = self.repo.remotes.origin
                            origin.pull()
                            print("Repository updated successfully")
                        except Exception as e:
                            print(f"Warning: Could not update repository: {str(e)}")
                    else:
                        # Clone to specified directory
                        print(f"Cloning repository to: {local_directory}")
                        os.makedirs(local_directory, exist_ok=True)
                        self.repo = Repo.clone_from(repository_url, local_directory)
                else:
                    # Clone to temp directory
                    self.temp_dir = tempfile.mkdtemp()
                    print(f"Cloning repository to temp directory: {self.temp_dir}")
                    self.repo = Repo.clone_from(repository_url, self.temp_dir)
            else:
                # Use current directory
                print(f"Using current directory: {os.getcwd()}")
                self.repo = Repo(os.getcwd())

            # Get all commits after the specified commit
            commits = []
            for commit in self.repo.iter_commits():
                if commit.hexsha == current_commit:
                    break
                
                # Check if commit modified any of the source files
                if any(file in commit.stats.files for file in source_files):
                    print(f"Found relevant commit: {commit.hexsha}")
                    commits.append({
                        'hash': commit.hexsha,
                        'message': commit.message,
                        'author': commit.author.name,
                        'date': commit.committed_datetime.isoformat(),
                        'files': list(commit.stats.files.keys()),
                        'diff': self._get_commit_diff(commit, source_files)
                    })
                    print(f"diff: {self._get_commit_diff(commit, source_files)}")

            print(f"Total commits found: {len(commits)}")
            return commits

        except Exception as e:
            print(f"Error getting commits: {str(e)}")
            raise Exception(f"Error getting commits: {str(e)}")
        finally:
            # Only cleanup temp directory if we created one
            if self.temp_dir:
                self._cleanup()

    def _get_commit_diff(self, commit: Commit, source_files: List[str]) -> Dict[str, str]:
        """
        Get the diff for specified files in the commit.
        """
        diffs = {}
        for file in source_files:
            try:
                if file in commit.stats.files:
                    diffs[file] = self.repo.git.diff(
                        f"{commit.hexsha}^",
                        commit.hexsha,
                        "--",
                        file
                    )
            except Exception:
                continue
        return diffs

    def _cleanup(self):
        """
        Clean up temporary directory if it exists.
        """
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            self.temp_dir = None
            self.repo = None 