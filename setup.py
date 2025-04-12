from setuptools import setup, find_packages

setup(
    name="terraform-analyzer",
    version="1.0.0",  # Updated to match __init__.py version
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "pyyaml>=6.0.1",
        "gitpython>=3.1.41",
        "requests>=2.31.0",
        "packaging>=24.0",
    ],
    python_requires=">=3.8",
)