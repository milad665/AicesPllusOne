import pytest
from pathlib import Path
import tempfile
from aices_plus_one.tree_sitter_analyzer import TreeSitterAnalyzer
from aices_plus_one.models import ProjectLanguage, ProjectType


@pytest.fixture
def analyzer():
    """Create a TreeSitterAnalyzer instance"""
    return TreeSitterAnalyzer()


@pytest.fixture
def temp_python_project():
    """Create a temporary Python project for testing"""
    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir) / "test_project"
        project_path.mkdir()
        
        # Create a simple Python file
        python_file = project_path / "main.py"
        python_code = '''
def hello_world(name="World"):
    """Say hello to someone"""
    return f"Hello, {name}!"

class Calculator:
    """A simple calculator class"""
    
    def add(self, a, b):
        return a + b
    
    def multiply(self, a, b):
        return a * b

if __name__ == "__main__":
    calc = Calculator()
    print(hello_world())
    print(calc.add(2, 3))
'''
        python_file.write_text(python_code)
        
        # Create requirements.txt
        requirements = project_path / "requirements.txt"
        requirements.write_text("fastapi==0.104.1\nuvicorn==0.24.0\n")
        
        # Create README.md
        readme = project_path / "README.md"
        readme.write_text("# Test Project\nA simple test project for demonstration.")
        
        yield project_path


def test_detect_language(analyzer):
    """Test language detection from file extensions"""
    assert analyzer._detect_language(Path("test.py")) == ProjectLanguage.PYTHON
    assert analyzer._detect_language(Path("test.js")) == ProjectLanguage.JAVASCRIPT
    assert analyzer._detect_language(Path("test.ts")) == ProjectLanguage.TYPESCRIPT
    assert analyzer._detect_language(Path("test.java")) == ProjectLanguage.JAVA
    assert analyzer._detect_language(Path("test.cpp")) == ProjectLanguage.CPP
    assert analyzer._detect_language(Path("test.go")) == ProjectLanguage.GO
    assert analyzer._detect_language(Path("test.rs")) == ProjectLanguage.RUST
    assert analyzer._detect_language(Path("test.cs")) == ProjectLanguage.CSHARP
    assert analyzer._detect_language(Path("test.unknown")) == ProjectLanguage.UNKNOWN


def test_extract_python_entry_points(analyzer, temp_python_project):
    """Test extracting entry points from Python code"""
    entry_points = analyzer.extract_entry_points(temp_python_project)
    
    # Should find the function and class
    assert len(entry_points) >= 2
    
    # Check for function
    function_entry = next((ep for ep in entry_points if ep.name == "hello_world"), None)
    assert function_entry is not None
    assert function_entry.type == "function"
    assert "name" in function_entry.parameters
    
    # Check for class
    class_entry = next((ep for ep in entry_points if ep.name == "Calculator"), None)
    assert class_entry is not None
    assert class_entry.type == "class"


def test_analyze_project(analyzer, temp_python_project):
    """Test analyzing a complete project"""
    project_info = analyzer.analyze_project(temp_python_project, "test-repo")
    
    assert project_info.name == "test_project"
    assert project_info.repository_name == "test-repo"
    assert project_info.language == ProjectLanguage.PYTHON
    assert project_info.file_count > 0
    assert project_info.lines_of_code > 0
    assert len(project_info.dependencies) > 0
    assert "fastapi" in project_info.dependencies
    assert project_info.description is not None


def test_extract_dependencies(analyzer, temp_python_project):
    """Test extracting dependencies from project files"""
    dependencies = analyzer._extract_dependencies(temp_python_project, ProjectLanguage.PYTHON)
    
    assert "fastapi" in dependencies
    assert "uvicorn" in dependencies
