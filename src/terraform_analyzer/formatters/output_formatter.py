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

class HtmlFormatter(OutputFormatter):
    def format(self, results: List[AnalysisResult]) -> str:
        html = ['<!DOCTYPE html>',
               '<html>',
               '<head>',
               '<title>Terraform Analysis Results</title>',
               '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
               '<style>',
               ':root { --primary: #5c4ee5; --success: #28a745; --warning: #ffc107; --danger: #dc3545; --secondary: #6c757d; }',
               'body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; margin: 0; padding: 0; line-height: 1.5; color: #212529; background: #f8f9fa; }',
               '.container { max-width: 1200px; margin: 0 auto; padding: 2rem; }',
               'h1 { text-align: center; color: var(--primary); font-size: 2.5rem; margin-bottom: 2rem; }',
               '.repository-card { background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 2rem; overflow: hidden; }',
               '.repository-header { background: var(--primary); color: white; padding: 1.5rem; position: relative; }',
               '.repository-header h2 { margin: 0; font-size: 1.75rem; }',
               '.repository-header .meta { opacity: 0.9; font-size: 0.9rem; margin-top: 0.5rem; }',
               '.repository-content { padding: 1.5rem; }',
               '.status-badge { display: inline-block; padding: 0.25rem 0.75rem; border-radius: 50px; font-size: 0.875rem; font-weight: 500; }',
               '.status-success { background: var(--success); color: white; }',
               '.status-warning { background: var(--warning); color: black; }',
               '.status-danger { background: var(--danger); color: white; }',
               '.status-error { background: var(--danger); color: white; }',
               '.info-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem; margin: 1rem 0; }',
               '.info-item { background: #f8f9fa; padding: 1rem; border-radius: 6px; }',
               '.info-item h4 { margin: 0 0 0.5rem 0; color: var(--secondary); }',
               '.info-item p { margin: 0; font-size: 1.1rem; }',
               '.provider-table { width: 100%; border-collapse: collapse; margin: 1rem 0; }',
               '.provider-table th { background: #f8f9fa; padding: 0.75rem; text-align: left; border-bottom: 2px solid #dee2e6; }',
               '.provider-table td { padding: 0.75rem; border-bottom: 1px solid #dee2e6; }',
               '.version-bar { background: #e9ecef; height: 6px; border-radius: 3px; margin-top: 0.25rem; }',
               '.version-bar-fill { background: var(--primary); height: 100%; border-radius: 3px; transition: width 0.3s ease; }',
               '.version-outdated .version-bar-fill { background: var(--warning); }',
               '.version-major-update .version-bar-fill { background: var(--danger); }',
               '@media (max-width: 768px) { .info-grid { grid-template-columns: 1fr; } }',
               '</style>',
               '</head>',
               '<body>',
               '<div class="container">',
               '<h1>Terraform Analysis Results</h1>']

        for result in results:
            # Start repository card
            html.append('<div class="repository-card">')
            
            # Repository header
            html.append('<div class="repository-header">')
            html.append(f'<h2>{result.repository.name}</h2>')
            html.append('<div class="meta">')
            html.append(f'<div>Repository: {result.repository.repository}</div>')
            html.append(f'<div>Path: {result.repository.terraform_path}</div>')
            if result.repository.branch:
                html.append(f'<div>Branch: {result.repository.branch}</div>')
            html.append('</div>')
            html.append('</div>')

            # Repository content
            html.append('<div class="repository-content">')

            if result.error:
                html.append('<div class="status-badge status-error">')
                html.append(f'Error: {result.error}')
                html.append('</div>')
            else:
                # Info grid
                html.append('<div class="info-grid">')
                html.append('<div class="info-item">')
                html.append('<h4>Terraform Version</h4>')
                html.append(f'<p>{result.terraform_version}</p>')
                html.append('</div>')
                
                # Add summary info with major updates count
                provider_count = len(result.provider_versions)
                major_updates = 0
                minor_updates = 0
                
                for v in result.provider_versions.values():
                    if v.latest_version and v.current_version != v.latest_version:
                        current_parts = v.current_version.split('.')
                        latest_parts = v.latest_version.split('.')
                        if len(current_parts) > 0 and len(latest_parts) > 0:
                            if int(latest_parts[0]) > int(current_parts[0]):
                                major_updates += 1
                            else:
                                minor_updates += 1
                
                html.append('<div class="info-item">')
                html.append('<h4>Providers</h4>')
                html.append(f'<p>{provider_count} Total / {major_updates} Major Updates / {minor_updates} Minor Updates</p>')
                html.append('</div>')
                html.append('</div>')

                if result.provider_versions:
                    html.append('<table class="provider-table">')
                    html.append('<tr>')
                    html.append('<th>Provider</th>')
                    html.append('<th>Current Version</th>')
                    html.append('<th>Latest Version</th>')
                    html.append('<th>Status</th>')
                    html.append('</tr>')
                    
                    for provider, version in result.provider_versions.items():
                        is_outdated = version.latest_version and version.current_version != version.latest_version
                        
                        if is_outdated:
                            current_parts = version.current_version.split('.')
                            latest_parts = version.latest_version.split('.')
                            is_major_update = False
                            
                            if len(current_parts) > 0 and len(latest_parts) > 0:
                                if int(latest_parts[0]) > int(current_parts[0]):
                                    is_major_update = True
                            
                            version_class = 'version-major-update' if is_major_update else 'version-outdated'
                        else:
                            version_class = ''
                        
                        html.append(f'<tr class="{version_class}">')
                        html.append(f'<td>{provider}</td>')
                        html.append(f'<td>{version.current_version}</td>')
                        html.append(f'<td>{version.latest_version or "N/A"}</td>')
                        
                        if is_outdated:
                            badge_class = 'status-danger' if is_major_update else 'status-warning'
                            badge_text = '🚨 Major Update Required!' if is_major_update else '⚠️ Update Available'
                            
                            html.append('<td>')
                            html.append(f'<div class="status-badge {badge_class}">{badge_text}</div>')
                            
                            # Add version progress bar
                            current_parts = version.current_version.split('.')
                            latest_parts = version.latest_version.split('.')
                            if len(current_parts) >= 3 and len(latest_parts) >= 3:
                                current_val = int(current_parts[0]) * 10000 + int(current_parts[1]) * 100 + int(current_parts[2])
                                latest_val = int(latest_parts[0]) * 10000 + int(latest_parts[1]) * 100 + int(latest_parts[2])
                                if latest_val > 0:
                                    progress = min(100, (current_val / latest_val) * 100)
                                    html.append('<div class="version-bar">')
                                    html.append(f'<div class="version-bar-fill" style="width: {progress}%;"></div>')
                                    html.append('</div>')
                            html.append('</td>')
                        else:
                            html.append('<td><div class="status-badge status-success">✓ Up to date</div></td>')
                        
                        html.append('</tr>')
                    
                    html.append('</table>')
                else:
                    html.append('<p>No provider versions found</p>')
            
            html.append('</div>')  # End repository-content
            html.append('</div>')  # End repository-card

        html.extend(['</div>', '</body>', '</html>'])
        return '\n'.join(html)

class MarkdownFormatter(OutputFormatter):
    def format(self, results: List[AnalysisResult]) -> str:
        md = ['# Terraform Analysis Results\n']

        for result in results:
            md.append(f'## Repository: {result.repository.name}\n')
            md.append(f'- **URL**: {result.repository.repository}')
            md.append(f'- **Terraform Path**: {result.repository.terraform_path}')
            if result.repository.branch:
                md.append(f'- **Branch**: {result.repository.branch}')
            md.append('')

            if result.error:
                md.append(f'**Error**: {result.error}\n')
            else:
                md.append(f'**Terraform Version**: {result.terraform_version}\n')

                if result.provider_versions:
                    # Add summary info
                    provider_count = len(result.provider_versions)
                    major_updates = 0
                    minor_updates = 0
                    
                    for v in result.provider_versions.values():
                        if v.latest_version and v.current_version != v.latest_version:
                            current_parts = v.current_version.split('.')
                            latest_parts = v.latest_version.split('.')
                            if len(current_parts) > 0 and len(latest_parts) > 0:
                                if int(latest_parts[0]) > int(current_parts[0]):
                                    major_updates += 1
                                else:
                                    minor_updates += 1

                    md.append(f'### Provider Summary')
                    md.append(f'- Total Providers: {provider_count}')
                    if major_updates > 0:
                        md.append(f'- 🚨 **Major Updates Required**: {major_updates}')
                    if minor_updates > 0:
                        md.append(f'- ⚠️ Minor Updates Available: {minor_updates}')
                    md.append('')

                    md.append('### Provider Versions\n')
                    md.append('| Provider | Current Version | Latest Version | Status |')
                    md.append('|----------|-----------------|----------------|---------|')
                    
                    for provider, version in result.provider_versions.items():
                        status = '✓ Up to date'
                        if version.latest_version and version.current_version != version.latest_version:
                            current_parts = version.current_version.split('.')
                            latest_parts = version.latest_version.split('.')
                            if len(current_parts) > 0 and len(latest_parts) > 0:
                                if int(latest_parts[0]) > int(current_parts[0]):
                                    status = '🚨 **Major Update Required!**'
                                else:
                                    status = '⚠️ Update Available'
                        
                        md.append(f'| {provider} | {version.current_version} | {version.latest_version or "N/A"} | {status} |')
                else:
                    md.append('No provider versions found\n')
            
            md.append('\n---\n')

        return '\n'.join(md)

class FormatterFactory:
    _formatters = {
        'text': TextFormatter,
        'json': JsonFormatter,
        'csv': CsvFormatter,
        'html': HtmlFormatter,
        'markdown': MarkdownFormatter
    }
    
    @classmethod
    def get_formatter(cls, format_type: str) -> OutputFormatter:
        formatter_class = cls._formatters.get(format_type.lower())
        if not formatter_class:
            raise ValueError(f"Unsupported format type: {format_type}")
        return formatter_class()