from setuptools import setup, find_packages

setup(
    name="aices_plus_one",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.104.0",
        "uvicorn>=0.24.0",
        "pydantic>=2.5.0",
        "sqlalchemy>=2.0.20",
        "GitPython>=3.1.40",
        "tree-sitter>=0.20.0",
        "tree-sitter-python>=0.23.0",
        "tree-sitter-javascript>=0.21.0",
        "tree-sitter-typescript>=0.21.0",
        "tree-sitter-java>=0.23.0",
        "tree-sitter-cpp>=0.23.0",
        "tree-sitter-go>=0.23.0",
        "tree-sitter-rust>=0.23.0",
        "tree-sitter-c-sharp>=0.23.0",
        "cryptography>=41.0.0",
        "paramiko>=3.3.0",
        "httpx>=0.25.0",
        "aiosqlite>=0.19.0"
    ],
    entry_points={
        "console_scripts": [
            "aices-analyzer=aices_plus_one.main:main",
        ],
    },
)
