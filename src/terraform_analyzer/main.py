import argparse
import yaml
from typing import List
from terraform_analyzer.models.repository import RepositoryInfo
from terraform_analyzer.models.exceptions import RepositoryAnalysisError
from terraform_analyzer.analyzers.repository_analyzer import RepositoryAnalyzer
from terraform_analyzer.formatters.output_formatter import FormatterFactory
from terraform_analyzer.formatters.history_formatter import HistoryFormatter
from terraform_analyzer.utils.history_manager import HistoryManager


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Analyzes Terraform and provider versions in Git repositories"
    )
    parser.add_argument(
        "--output-format",
        choices=["text", "json", "csv", "html", "markdown"],
        default="text",
        help="Output format (text, json, csv, html, markdown)",
    )
    parser.add_argument("--output-file", help="Output file path (optional)")
    parser.add_argument(
        "--config", default="config.yaml", help="Path to the YAML configuration file"
    )
    parser.add_argument(
        "--history-file",
        default="terraform_history.json",
        help="Path to the history file",
    )
    parser.add_argument("--show-history", action="store_true", help="View scan history")
    parser.add_argument(
        "--show-changes", action="store_true", help="Show version changes"
    )
    parser.add_argument(
        "--include-prerelease",
        action="store_true",
        help="Include alpha/beta versions when checking for latest provider versions",
    )
    return parser.parse_args()


def read_config(config_path: str) -> List[RepositoryInfo]:
    try:
        with open(config_path, "r") as file:
            config = yaml.safe_load(file)
            return [
                RepositoryInfo(
                    name=repo["name"],
                    repository=repo["repository"],
                    terraform_path=repo["terraform-path"],
                    branch=repo.get("branch"),  # Optionnel
                )
                for repo in config["repos"]
            ]
    except yaml.YAMLError as e:
        raise RepositoryAnalysisError(f"Error parsing config file: {str(e)}")
    except FileNotFoundError:
        raise RepositoryAnalysisError(f"Config file not found: {config_path}")
    except KeyError as e:
        raise RepositoryAnalysisError(f"Missing required field in config: {str(e)}")


def analyze_repositories(repositories: List[RepositoryInfo]) -> List[dict]:
    results = []
    for repo in repositories:
        try:
            with RepositoryAnalyzer(repo) as analyzer:
                result = analyzer.analyze()
                results.append(result)
        except Exception as e:
            results.append({"repository": repo, "error": str(e)})
    return results


def show_history(history_manager: HistoryManager):
    """Affiche l'historique des analyses."""
    for repo_name in history_manager.get_repository_names():
        history = history_manager.get_repository_history(repo_name)
        print(HistoryFormatter.format_repository_history(history))
        print("\n" + "=" * 80 + "\n")


def show_changes(history_manager: HistoryManager):
    """Affiche les changements de versions."""
    for repo_name in history_manager.get_repository_names():
        changes = history_manager.get_version_changes(repo_name)
        print(HistoryFormatter.format_version_changes(changes))
        print("\n" + "=" * 80 + "\n")


def main():
    args = parse_arguments()

    try:
        # Set include_prerelease flag on TerraformAnalyzer
        from terraform_analyzer.analyzers.terraform_analyzer import TerraformAnalyzer

        TerraformAnalyzer.set_include_prerelease(args.include_prerelease)

        # Initialize history manager
        history_manager = HistoryManager(args.history_file)

        # If we want to see history or changes, do it and exit
        if args.show_history:
            show_history(history_manager)
            return
        if args.show_changes:
            show_changes(history_manager)
            return

        # Read configuration
        repositories = read_config(args.config)

        # Analyze repositories
        results = analyze_repositories(repositories)

        # Add results to history
        for result in results:
            history_manager.add_entry(result)

        # Format and display results
        formatter = FormatterFactory.get_formatter(args.output_format)
        output = formatter.format(results)

        if args.output_file:
            with open(args.output_file, "w") as f:
                f.write(output)
        else:
            print(output)

    except Exception as e:
        print(f"Erreur : {str(e)}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
