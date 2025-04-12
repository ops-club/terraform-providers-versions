from typing import List
from ..models.history import RepositoryHistory, VersionChange

class HistoryFormatter:
    @staticmethod
    def format_repository_history(history: RepositoryHistory) -> str:
        if not history:
            return "No history available"

        output = []
        output.append(f"Repository: {history.name}")
        output.append(f"Last analyzed: {history.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        output.append(f"Terraform version: {history.terraform_version}")
        
        if history.provider_versions:
            output.append("\nProvider versions:")
            for provider, version in history.provider_versions.items():
                output.append(f"  - {provider}:")
                output.append(f"      Current version: {version.current_version}")
                output.append(f"      Latest version: {version.latest_version or 'N/A'}")
                if version.latest_version and version.current_version != version.latest_version:
                    output.append("      ⚠️ Upgrade available!")
        else:
            output.append("\nNo provider versions found")

        return "\n".join(output)

    @staticmethod
    def format_version_changes(changes: List[VersionChange]) -> str:
        if not changes:
            return "No version changes detected"

        output = []
        output.append("Version changes detected:")
        
        for change in changes:
            output.append(f"\nProvider: {change.provider}")
            output.append("Previous version:")
            output.append(f"  Current: {change.old_version.current_version}")
            output.append(f"  Latest available: {change.old_version.latest_version or 'N/A'}")
            output.append(f"  Timestamp: {change.old_version.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
            
            output.append("New version:")
            output.append(f"  Current: {change.new_version.current_version}")
            output.append(f"  Latest available: {change.new_version.latest_version or 'N/A'}")
            output.append(f"  Timestamp: {change.new_version.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
            
            if change.is_upgrade_available:
                output.append("  ⚠️ Newer version available!")

        return "\n".join(output)