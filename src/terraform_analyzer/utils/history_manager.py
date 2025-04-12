import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from ..models.history import HistoryEntry, RepositoryHistory, VersionChange, ProviderVersionHistory
from ..models.repository import AnalysisResult

class HistoryManager:
    def __init__(self, history_file: str):
        self.history_file = history_file
        self.history: Dict[str, List[HistoryEntry]] = {}
        self._load_history()

    def _load_history(self):
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    data = json.load(f)
                    for repo_name, entries in data.items():
                        self.history[repo_name] = [
                            HistoryEntry.from_dict(entry) for entry in entries
                        ]
            except json.JSONDecodeError:
                self.history = {}
        else:
            self.history = {}

    def _save_history(self):
        with open(self.history_file, 'w') as f:
            json.dump({
                repo: [entry.to_dict() for entry in entries]
                for repo, entries in self.history.items()
            }, f, indent=2)

    def add_entry(self, result: AnalysisResult):
        entry = HistoryEntry.from_analysis_result(result)
        if result.repository.name not in self.history:
            self.history[result.repository.name] = []
        self.history[result.repository.name].append(entry)
        self._save_history()

    def get_repository_names(self) -> List[str]:
        return list(self.history.keys())

    def get_repository_history(self, repo_name: str) -> Optional[RepositoryHistory]:
        if repo_name not in self.history or not self.history[repo_name]:
            return None

        latest_entry = self.history[repo_name][-1]
        if latest_entry.error:
            return None

        provider_versions = {}
        for provider, version_data in latest_entry.provider_versions.items():
            provider_versions[provider] = ProviderVersionHistory(
                current_version=version_data['current_version'],
                latest_version=version_data['latest_version'],
                timestamp=latest_entry.timestamp
            )

        return RepositoryHistory(
            name=repo_name,
            terraform_version=latest_entry.terraform_version,
            provider_versions=provider_versions,
            timestamp=latest_entry.timestamp
        )

    def get_version_changes(self, repo_name: str) -> List[VersionChange]:
        if repo_name not in self.history or len(self.history[repo_name]) < 2:
            return []

        entries = self.history[repo_name]
        changes = []

        # Compare the last two successful entries
        valid_entries = [e for e in entries if not e.error]
        if len(valid_entries) < 2:
            return []

        old_entry = valid_entries[-2]
        new_entry = valid_entries[-1]

        # Find providers that exist in either entry
        all_providers = set(old_entry.provider_versions.keys()) | set(new_entry.provider_versions.keys())

        for provider in all_providers:
            old_version_data = old_entry.provider_versions.get(provider, {})
            new_version_data = new_entry.provider_versions.get(provider, {})

            if old_version_data != new_version_data:
                old_version_hist = ProviderVersionHistory(
                    current_version=old_version_data['current_version'] if 'current_version' in old_version_data else 'N/A',
                    latest_version=old_version_data.get('latest_version'),
                    timestamp=old_entry.timestamp
                )
                
                new_version_hist = ProviderVersionHistory(
                    current_version=new_version_data['current_version'] if 'current_version' in new_version_data else 'N/A',
                    latest_version=new_version_data.get('latest_version'),
                    timestamp=new_entry.timestamp
                )

                changes.append(VersionChange(
                    provider=provider,
                    old_version=old_version_hist,
                    new_version=new_version_hist
                ))

        return changes