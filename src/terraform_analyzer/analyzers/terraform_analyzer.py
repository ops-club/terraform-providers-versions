import json
import subprocess
import requests
from packaging import version
from typing import Dict, Tuple, Optional
from ..models.exceptions import TerraformAnalysisError

class RepositoryAnalysisError(Exception):
    """Custom exception for repository analysis errors"""
    pass

class TerraformAnalyzer:
    REGISTRY_API_URL = "https://registry.terraform.io/v1/providers"
    include_prerelease = False  # Class level flag to control prerelease versions

    @classmethod
    def set_include_prerelease(cls, value: bool):
        """Set whether to include prerelease versions."""
        cls.include_prerelease = value

    @staticmethod
    def analyze_directory(terraform_path: str) -> Tuple[Optional[str], Dict[str, Dict[str, str]]]:
        """Analyze a Terraform directory to extract version information."""
        try:
            terraform_init_result = TerraformAnalyzer._terraform_init(terraform_path)
            terraform_version = TerraformAnalyzer._get_terraform_version(terraform_path)
            provider_versions = TerraformAnalyzer._get_provider_versions(terraform_path)
            latest_versions = TerraformAnalyzer._get_latest_provider_versions(provider_versions)
            
            # Combine current and latest versions
            provider_info = {}
            for provider, current_version in provider_versions.items():
                provider_info[provider] = {
                    "current_version": current_version,
                    "latest_version": latest_versions.get(provider)
                }

            return terraform_version, provider_info
        except Exception as e:
            raise TerraformAnalysisError(f"Failed to analyze Terraform directory: {str(e)}")

    @staticmethod
    def _terraform_init(terraform_path: str) -> Optional[str]:
        """Init Terraform version from the directory."""
        init_result = subprocess.run(
            ['terraform', 'init', '-backend=false'],
            cwd=terraform_path,
            capture_output=True,
            text=True
        )
        
        if init_result.returncode != 0:
            raise TerraformAnalysisError(f"Terraform init failed: {init_result.stderr}")
        
        return True
    
    @staticmethod
    def _load_terraform_version(terraform_path: str) -> Optional[str]:
        """Load terraform version information."""
        version_result = subprocess.run(
            ['terraform', 'version', '-json'],
            cwd=terraform_path,
            capture_output=True,
            text=True
        )
        
        if version_result.returncode != 0:
            raise RepositoryAnalysisError(f"Failed to get terraform version info: {version_result.stderr}")
        
        version_data = json.loads(version_result.stdout)
        return version_data
        
    @staticmethod
    def _get_terraform_version(terraform_path: str) -> Optional[str]:
        """Get Terraform version from the json."""
        _terraform_version_data = TerraformAnalyzer._load_terraform_version(terraform_path)
        
        terraform_version = _terraform_version_data.get('terraform_version')
        if terraform_version:
            return terraform_version
        return None

    @staticmethod
    def _get_provider_versions(terraform_path: str) -> Dict[str, str]:
        """Get current provider versions from terraform version command."""
        _terraform_version_data = TerraformAnalyzer._load_terraform_version(terraform_path)
        
        if not _terraform_version_data:
            return {}
            
        provider_versions = {}
        for provider, version in _terraform_version_data.get('provider_selections', {}).items():
            if provider and version:
                provider_versions[provider] = version
                
        return provider_versions

    @classmethod
    def _is_prerelease(cls, ver_str: str) -> bool:
        """Check if a version string represents a prerelease version."""
        return any(x in ver_str.lower() for x in ['alpha', 'beta', 'rc'])

    @classmethod
    def _get_latest_provider_versions(cls, current_providers: Dict[str, str]) -> Dict[str, str]:
        """Get latest versions for all providers from Terraform Registry."""
        latest_versions = {}
        
        for provider in current_providers.keys():
            try:
                # Extract namespace and name from provider string (e.g., "registry.terraform.io/hashicorp/aws")
                parts = provider.split('/')
                if len(parts) >= 3:
                    namespace = parts[-2]
                    name = parts[-1]
                    
                    # Query the registry API
                    response = requests.get(f"{cls.REGISTRY_API_URL}/{namespace}/{name}/versions")
                    if response.status_code == 200:
                        versions_data = response.json().get('versions', [])
                        if versions_data:
                            # Find the highest version using semantic versioning comparison
                            highest_version = None
                            highest_version_obj = None
                            
                            for ver in versions_data:
                                ver_str = ver.get('version')
                                if ver_str:
                                    # Skip prerelease versions unless explicitly included
                                    if not cls.include_prerelease and cls._is_prerelease(ver_str):
                                        continue
                                        
                                    try:
                                        ver_obj = version.parse(ver_str)
                                        if (highest_version_obj is None or 
                                            ver_obj > highest_version_obj):
                                            highest_version = ver_str
                                            highest_version_obj = ver_obj
                                    except version.InvalidVersion:
                                        # Skip invalid versions
                                        continue
                            
                            if highest_version:
                                latest_versions[provider] = highest_version
            except Exception as e:
                # Log error but continue with other providers
                print(f"Failed to get latest version for provider {provider}: {str(e)}")
                
        return latest_versions