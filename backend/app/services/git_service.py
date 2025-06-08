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
        repository_url: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all commits after the specified commit that modified the given source files.
        """
        try:
            if repository_url:
                # Clone repository to temp directory
                self.temp_dir = tempfile.mkdtemp()
                self.repo = Repo.clone_from(repository_url, self.temp_dir)
            else:
                # Use current directory
                self.repo = Repo(os.getcwd())

            # Get all commits after the specified commit
            commits = []
            found_current = False
            for commit in self.repo.iter_commits():
                if not found_current:
                    if commit.hexsha == current_commit:
                        found_current = True
                    continue
                
                # Check if commit modified any of the source files
                if any(file in commit.stats.files for file in source_files):
                    commits.append({
                        'hash': commit.hexsha,
                        'message': commit.message,
                        'author': commit.author.name,
                        'date': commit.committed_datetime.isoformat(),
                        'files': list(commit.stats.files.keys()),
                        'diff': self._get_commit_diff(commit, source_files)
                    })

            return commits

        except Exception as e:
            raise Exception(f"Error getting commits: {str(e)}")
        finally:
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