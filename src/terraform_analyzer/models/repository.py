from dataclasses import dataclass, field
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
    terraform_version: Optional[str] = None
    installed_terraform_version: Optional[str] = None  # Added field for installed version
    provider_versions: Dict[str, ProviderVersion] = field(default_factory=dict)
    error: Optional[str] = None