from dataclasses import dataclass
from typing import Dict, Optional

@dataclass
class ProviderVersion:
    current_version: str
    latest_version: Optional[str]

@dataclass
class RepositoryInfo:
    name: str
    repository: str
    terraform_path: str
    branch: Optional[str] = None

@dataclass
class AnalysisResult:
    repository: RepositoryInfo
    terraform_version: Optional[str]
    provider_versions: Dict[str, ProviderVersion]
    error: Optional[str] = None