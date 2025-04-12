from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional
from .repository import RepositoryInfo, ProviderVersion

@dataclass
class ProviderVersionHistory:
    current_version: str
    latest_version: Optional[str]
    timestamp: datetime

@dataclass
class RepositoryHistory:
    name: str
    terraform_version: Optional[str]
    provider_versions: Dict[str, ProviderVersionHistory]
    timestamp: datetime

@dataclass
class VersionChange:
    provider: str
    old_version: ProviderVersionHistory
    new_version: ProviderVersionHistory
    is_upgrade_available: bool = False

    def __post_init__(self):
        if (self.new_version.latest_version and 
            self.new_version.current_version != self.new_version.latest_version):
            self.is_upgrade_available = True

@dataclass
class HistoryEntry:
    timestamp: datetime
    repository: RepositoryInfo
    terraform_version: Optional[str]
    provider_versions: Dict[str, Dict[str, str]]  # Store as dict for JSON serialization
    error: Optional[str]

    @classmethod
    def from_analysis_result(cls, result, timestamp=None):
        if timestamp is None:
            timestamp = datetime.now()
            
        # Convert ProviderVersion objects to dictionary format
        provider_versions = {
            provider: {
                'current_version': version.current_version,
                'latest_version': version.latest_version
            }
            for provider, version in result.provider_versions.items()
        }
        
        return cls(
            timestamp=timestamp,
            repository=result.repository,
            terraform_version=result.terraform_version,
            provider_versions=provider_versions,
            error=result.error
        )

    def to_dict(self) -> dict:
        return {
            'timestamp': self.timestamp.isoformat(),
            'repository': {
                'name': self.repository.name,
                'repository': self.repository.repository,
                'terraform_path': self.repository.terraform_path,
                'branch': self.repository.branch
            },
            'terraform_version': self.terraform_version,
            'provider_versions': self.provider_versions,
            'error': self.error
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'HistoryEntry':
        return cls(
            timestamp=datetime.fromisoformat(data['timestamp']),
            repository=RepositoryInfo(
                name=data['repository']['name'],
                repository=data['repository']['repository'],
                terraform_path=data['repository']['terraform_path'],
                branch=data['repository'].get('branch')
            ),
            terraform_version=data['terraform_version'],
            provider_versions=data['provider_versions'],
            error=data['error']
        )