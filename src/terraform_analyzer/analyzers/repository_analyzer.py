import tempfile
import os
import shutil
import git
from ..models.repository import RepositoryInfo, AnalysisResult, ProviderVersion
from ..models.exceptions import RepositoryAnalysisError
from .terraform_analyzer import TerraformAnalyzer

class RepositoryAnalyzer:
    def __init__(self, repository: RepositoryInfo):
        self.repository = repository
        self.temp_dir = None
        self.repo_path = None

    def __enter__(self):
        self.temp_dir = tempfile.mkdtemp()
        self.repo_path = os.path.join(self.temp_dir, self.repository.name)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def _clone_repository(self):
        try:
            git.Repo.clone_from(
                self.repository.repository,
                self.repo_path,
                branch=self.repository.branch
            )
        except git.exc.GitCommandError as e:
            if "not found" in str(e):
                raise RepositoryAnalysisError(f"Repository not found: {self.repository.repository}")
            elif "authentication" in str(e).lower():
                raise RepositoryAnalysisError(f"Authentication failed for repository: {self.repository.repository}")
            else:
                raise RepositoryAnalysisError(f"Git clone failed: {str(e)}")
        except Exception as e:
            raise RepositoryAnalysisError(f"Unexpected error during clone: {str(e)}")

    def analyze(self) -> AnalysisResult:
        try:
            self._clone_repository()
            
            terraform_path = os.path.join(self.repo_path, self.repository.terraform_path)
            if not os.path.exists(terraform_path):
                raise RepositoryAnalysisError(f"Terraform path does not exist: {terraform_path}")
            
            terraform_version, provider_info = TerraformAnalyzer.analyze_directory(terraform_path)
            
            # Convert provider versions to ProviderVersion objects
            provider_version_objects = {
                provider: ProviderVersion(
                    current_version=version_info['current_version'],
                    latest_version=version_info['latest_version']
                )
                for provider, version_info in provider_info.items()
            }
            
            return AnalysisResult(
                repository=self.repository,
                terraform_version=terraform_version,
                provider_versions=provider_version_objects,
                error=None
            )
            
        except Exception as e:
            return AnalysisResult(
                repository=self.repository,
                terraform_version=None,
                provider_versions={},
                error=str(e)
            )