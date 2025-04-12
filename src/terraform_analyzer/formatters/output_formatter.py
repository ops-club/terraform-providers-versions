import json
import csv
from abc import ABC, abstractmethod
from typing import List
from io import StringIO
from ..models.repository import RepositoryInfo, AnalysisResult

class OutputFormatter(ABC):
    @abstractmethod
    def format(self, results: List[AnalysisResult]) -> str:
        pass

class TextFormatter(OutputFormatter):
    def format(self, results: List[AnalysisResult]) -> str:
        output = []
        for result in results:
            output.append(f"Repository: {result.repository.name}")
            output.append(f"URL: {result.repository.repository}")
            output.append(f"Terraform Path: {result.repository.terraform_path}")
            if result.repository.branch:
                output.append(f"Branch: {result.repository.branch}")
            
            if result.error:
                output.append(f"Error: {result.error}")
            else:
                output.append(f"Terraform Version: {result.terraform_version}")
                if result.provider_versions:
                    output.append("\nProvider Versions:")
                    for provider, version in result.provider_versions.items():
                        output.append(f"  - {provider}:")
                        output.append(f"      Current version: {version.current_version}")
                        output.append(f"      Latest version: {version.latest_version or 'N/A'}")
                        if version.latest_version and version.current_version != version.latest_version:
                            output.append("      ⚠️ Upgrade available!")
                else:
                    output.append("\nNo provider versions found")
            
            output.append("")
        return "\n".join(output)

class JsonFormatter(OutputFormatter):
    def format(self, results: List[AnalysisResult]) -> str:
        output = []
        for result in results:
            entry = {
                'repository': {
                    'name': result.repository.name,
                    'url': result.repository.repository,
                    'terraform_path': result.repository.terraform_path,
                    'branch': result.repository.branch
                },
                'terraform_version': result.terraform_version,
                'provider_versions': {
                    provider: {
                        'current_version': version.current_version,
                        'latest_version': version.latest_version
                    }
                    for provider, version in result.provider_versions.items()
                },
                'error': result.error
            }
            output.append(entry)
        return json.dumps(output, indent=2)

class CsvFormatter(OutputFormatter):
    def format(self, results: List[AnalysisResult]) -> str:
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['repository', 'repository_url', 'terraform_path', 'branch', 
                        'terraform_version', 'provider', 'current_version', 'latest_version', 'error'])
        
        # Write data
        for result in results:
            if result.error:
                writer.writerow([
                    result.repository.name,
                    result.repository.repository,
                    result.repository.terraform_path,
                    result.repository.branch or '',
                    '',  # terraform_version
                    '',  # provider
                    '',  # current_version
                    '',  # latest_version
                    result.error
                ])
            else:
                if not result.provider_versions:
                    writer.writerow([
                        result.repository.name,
                        result.repository.repository,
                        result.repository.terraform_path,
                        result.repository.branch or '',
                        result.terraform_version,
                        '',  # provider
                        '',  # current_version
                        '',  # latest_version
                        ''   # error
                    ])
                else:
                    for provider, version in result.provider_versions.items():
                        writer.writerow([
                            result.repository.name,
                            result.repository.repository,
                            result.repository.terraform_path,
                            result.repository.branch or '',
                            result.terraform_version,
                            provider,
                            version.current_version,
                            version.latest_version or 'N/A',
                            ''  # error
                        ])
        
        return output.getvalue()

class FormatterFactory:
    _formatters = {
        'text': TextFormatter,
        'json': JsonFormatter,
        'csv': CsvFormatter
    }
    
    @classmethod
    def get_formatter(cls, format_type: str) -> OutputFormatter:
        formatter_class = cls._formatters.get(format_type.lower())
        if not formatter_class:
            raise ValueError(f"Unsupported format type: {format_type}")
        return formatter_class()