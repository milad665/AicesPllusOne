import tree_sitter_python as tspython
import tree_sitter_javascript as tsjavascript
import tree_sitter_typescript as tstypescript
import tree_sitter_java as tsjava
import tree_sitter_cpp as tscpp
import tree_sitter_go as tsgo
import tree_sitter_rust as tsrust
import tree_sitter_c_sharp as tscsharp
from tree_sitter import Language, Parser, Node
from pathlib import Path
from typing import List, Dict, Optional, Set, Tuple
import json
import re
import logging
from datetime import datetime
from .models import ProjectInfo, EntryPoint, ProjectLanguage, ProjectType

logger = logging.getLogger(__name__)


class TreeSitterAnalyzer:
    """Analyzes code using Tree-sitter to extract project metadata and entry points"""
    
    def __init__(self):
        self.languages = {}
        self.parsers = {}
        self._setup_languages()
    
    def _setup_languages(self):
        """Setup Tree-sitter languages and parsers"""
        language_configs = {}
        
        # Try to import and setup each language
        try:
            language_configs[ProjectLanguage.PYTHON] = tspython.language()
        except:
            logger.warning("Failed to setup Python Tree-sitter language")
        
        try:
            language_configs[ProjectLanguage.JAVASCRIPT] = tsjavascript.language()
        except:
            logger.warning("Failed to setup JavaScript Tree-sitter language")
        
        try:
            language_configs[ProjectLanguage.TYPESCRIPT] = tstypescript.language()
        except:
            logger.debug("Skipping TypeScript Tree-sitter language - version compatibility issue")
        
        try:
            language_configs[ProjectLanguage.JAVA] = tsjava.language()
        except:
            logger.warning("Failed to setup Java Tree-sitter language")
        
        try:
            language_configs[ProjectLanguage.CPP] = tscpp.language()
        except:
            logger.warning("Failed to setup C++ Tree-sitter language")
        
        try:
            language_configs[ProjectLanguage.GO] = tsgo.language()
        except:
            logger.warning("Failed to setup Go Tree-sitter language")
        
        try:
            language_configs[ProjectLanguage.RUST] = tsrust.language()
        except:
            logger.warning("Failed to setup Rust Tree-sitter language")
        
        try:
            language_configs[ProjectLanguage.CSHARP] = tscsharp.language()
        except:
            logger.warning("Failed to setup C# Tree-sitter language")
        
        for lang, tree_sitter_lang in language_configs.items():
            try:
                # Try to wrap the language properly
                language_obj = Language(tree_sitter_lang)
                self.languages[lang] = language_obj
                parser = Parser()
                parser.language = language_obj
                self.parsers[lang] = parser
                logger.debug(f"Initialized Tree-sitter for {lang}")
            except Exception as e:
                logger.debug(f"Skipping Tree-sitter for {lang}: {e}")
                # Continue without this language - graceful degradation
    
    def _detect_language(self, file_path: Path) -> ProjectLanguage:
        """Detect programming language from file extension"""
        extension_map = {
            '.py': ProjectLanguage.PYTHON,
            '.js': ProjectLanguage.JAVASCRIPT,
            '.jsx': ProjectLanguage.JAVASCRIPT,
            '.ts': ProjectLanguage.TYPESCRIPT,
            '.tsx': ProjectLanguage.TYPESCRIPT,
            '.java': ProjectLanguage.JAVA,
            '.cpp': ProjectLanguage.CPP,
            '.cc': ProjectLanguage.CPP,
            '.cxx': ProjectLanguage.CPP,
            '.c': ProjectLanguage.C,
            '.h': ProjectLanguage.C,
            '.hpp': ProjectLanguage.CPP,
            '.go': ProjectLanguage.GO,
            '.rs': ProjectLanguage.RUST,
            '.cs': ProjectLanguage.CSHARP,
        }
        return extension_map.get(file_path.suffix.lower(), ProjectLanguage.UNKNOWN)
    
    def _detect_project_type(self, project_path: Path, language: ProjectLanguage) -> ProjectType:
        """Detect project type based on files and structure"""
        files = list(project_path.rglob('*'))
        file_names = {f.name.lower() for f in files}
        
        # C# specific project type detection
        if language == ProjectLanguage.CSHARP:
            has_public_classes = False
            has_interfaces = False
            has_api_controllers = False
            has_main_method = False
            
            # Check for ASP.NET Core Web API patterns
            for file in files:
                if file.suffix == '.cs':
                    try:
                        content = file.read_text(encoding='utf-8')
                        
                        # Check for API patterns
                        if any(keyword in content for keyword in ['[ApiController]', '[Route', '[HttpGet]', '[HttpPost]', 'ControllerBase']):
                            has_api_controllers = True
                        
                        # Check for public classes and interfaces
                        if 'public class' in content:
                            has_public_classes = True
                        if 'public interface' in content or 'interface I' in content:
                            has_interfaces = True
                        
                        # Check for Main method (CLI entry point)
                        if 'static void Main' in content or 'static async Task Main' in content:
                            has_main_method = True
                            
                    except:
                        continue
            
            # Determine project type based on findings (prioritize by complexity)
            if has_api_controllers:
                return ProjectType.API
            elif has_interfaces and has_public_classes:
                # Library with public interfaces and classes (even if it has a CLI wrapper)
                return ProjectType.LIBRARY
            elif has_main_method and not has_public_classes:
                # Pure CLI application without library components
                return ProjectType.CLI
            
            # Check .csproj files for additional clues
            for file in files:
                if file.suffix == '.csproj':
                    try:
                        content = file.read_text(encoding='utf-8')
                        if '<OutputType>Library</OutputType>' in content or 'netstandard' in content:
                            return ProjectType.LIBRARY
                        elif '<OutputType>Exe</OutputType>' in content or 'netcoreapp' in content:
                            return ProjectType.CLI
                    except:
                        continue
        
        # Web application indicators
        if any(f in file_names for f in ['package.json', 'index.html', 'app.js', 'server.js']):
            return ProjectType.WEB_APP
        
        # Python API indicators
        if any(f in file_names for f in ['app.py', 'main.py', 'server.py', 'api.py']):
            # Check for Flask/FastAPI/Django patterns
            for file in files:
                if file.suffix == '.py':
                    try:
                        content = file.read_text(encoding='utf-8')
                        if any(keyword in content for keyword in ['@app.route', 'FastAPI', 'Django']):
                            return ProjectType.API
                    except:
                        continue
        
        # CLI indicators
        if any(f in file_names for f in ['cli.py', 'main.py', 'cmd.py']) or 'bin/' in str(project_path):
            return ProjectType.CLI
        
        # Library indicators
        if any(f in file_names for f in ['setup.py', 'pyproject.toml', 'cargo.toml', 'pom.xml']):
            return ProjectType.LIBRARY
        
        # Microservice indicators
        if any(f in file_names for f in ['dockerfile', 'docker-compose.yml', 'k8s.yml']):
            return ProjectType.MICROSERVICE
        
        return ProjectType.UNKNOWN
    
    def _extract_python_entry_points(self, source_code: str, file_path: str) -> List[EntryPoint]:
        """Extract entry points from Python code"""
        if ProjectLanguage.PYTHON not in self.parsers:
            return []
        
        parser = self.parsers[ProjectLanguage.PYTHON]
        tree = parser.parse(source_code.encode('utf-8'))
        
        entry_points = []
        
        def has_api_decorator(node: Node) -> bool:
            """Check if function has API route decorators"""
            # Look for decorators before the function
            parent = node.parent
            if parent and parent.type == 'decorated_definition':
                for child in parent.children:
                    if child.type == 'decorator':
                        decorator_text = source_code[child.start_byte:child.end_byte]
                        if any(api_dec in decorator_text for api_dec in ['@app.route', '@router.', '@get', '@post', '@put', '@delete']):
                            return True
            return False
        
        def is_public_function(func_name: str) -> bool:
            """Check if function is public (doesn't start with _)"""
            return not func_name.startswith('_')
        
        def traverse_node(node: Node, depth: int = 0):
            if node.type == 'function_definition':
                func_name = None
                parameters = []
                
                for child in node.children:
                    if child.type == 'identifier':
                        func_name = source_code[child.start_byte:child.end_byte]
                    elif child.type == 'parameters':
                        for param_child in child.children:
                            if param_child.type == 'identifier':
                                parameters.append(source_code[param_child.start_byte:param_child.end_byte])
                
                if func_name:
                    # Determine entry point type
                    entry_type = 'function'
                    if has_api_decorator(node):
                        entry_type = 'api_endpoint'
                    elif is_public_function(func_name):
                        entry_type = 'public_function'
                    else:
                        entry_type = 'private_function'
                    
                    entry_point = EntryPoint(
                        name=func_name,
                        file_path=file_path,
                        line_number=node.start_point[0] + 1,
                        type=entry_type,
                        parameters=parameters
                    )
                    entry_points.append(entry_point)
            
            elif node.type == 'class_definition':
                class_name = None
                for child in node.children:
                    if child.type == 'identifier':
                        class_name = source_code[child.start_byte:child.end_byte]
                        break
                
                if class_name:
                    entry_type = 'public_class' if is_public_function(class_name) else 'private_class'
                    entry_point = EntryPoint(
                        name=class_name,
                        file_path=file_path,
                        line_number=node.start_point[0] + 1,
                        type=entry_type
                    )
                    entry_points.append(entry_point)
            
            for child in node.children:
                traverse_node(child, depth + 1)
        
        traverse_node(tree.root_node)
        return entry_points
    
    def _extract_javascript_entry_points(self, source_code: str, file_path: str) -> List[EntryPoint]:
        """Extract entry points from JavaScript/TypeScript code"""
        lang = ProjectLanguage.TYPESCRIPT if file_path.endswith(('.ts', '.tsx')) else ProjectLanguage.JAVASCRIPT
        
        if lang not in self.parsers:
            return []
        
        parser = self.parsers[lang]
        tree = parser.parse(source_code.encode('utf-8'))
        
        entry_points = []
        
        def traverse_node(node: Node):
            if node.type == 'function_declaration':
                func_name = None
                parameters = []
                
                for child in node.children:
                    if child.type == 'identifier':
                        func_name = source_code[child.start_byte:child.end_byte]
                    elif child.type == 'formal_parameters':
                        for param_child in child.children:
                            if param_child.type == 'identifier':
                                parameters.append(source_code[param_child.start_byte:param_child.end_byte])
                
                if func_name:
                    entry_points.append(EntryPoint(
                        name=func_name,
                        file_path=file_path,
                        line_number=node.start_point[0] + 1,
                        type='function',
                        parameters=parameters
                    ))
            
            elif node.type == 'class_declaration':
                class_name = None
                for child in node.children:
                    if child.type == 'identifier':
                        class_name = source_code[child.start_byte:child.end_byte]
                        break
                
                if class_name:
                    entry_points.append(EntryPoint(
                        name=class_name,
                        file_path=file_path,
                        line_number=node.start_point[0] + 1,
                        type='class'
                    ))
            
            for child in node.children:
                traverse_node(child)
        
        traverse_node(tree.root_node)
        return entry_points
    
    def _extract_csharp_entry_points(self, source_code: str, file_path: str) -> List[EntryPoint]:
        """Extract entry points from C# code"""
        if ProjectLanguage.CSHARP not in self.parsers:
            return []
        
        parser = self.parsers[ProjectLanguage.CSHARP]
        tree = parser.parse(source_code.encode('utf-8'))
        
        entry_points = []
        
        def get_modifiers(node: Node) -> List[str]:
            """Extract modifiers (public, private, etc.) from a node"""
            modifiers = []
            for child in node.children:
                if child.type == 'modifier':
                    modifier_text = source_code[child.start_byte:child.end_byte].strip()
                    modifiers.append(modifier_text)
            return modifiers
        
        def get_attributes(node: Node) -> List[str]:
            """Extract attributes from a node"""
            attributes = []
            for child in node.children:
                if child.type == 'attribute_list':
                    attr_text = source_code[child.start_byte:child.end_byte]
                    attributes.append(attr_text)
            return attributes
        
        def is_api_endpoint(attributes: List[str], modifiers: List[str]) -> bool:
            """Check if this is a Web API endpoint"""
            attr_text = ' '.join(attributes)
            return any(api_attr in attr_text for api_attr in ['[HttpGet]', '[HttpPost]', '[HttpPut]', '[HttpDelete]', '[Route'])
        
        def is_public_method(modifiers: List[str]) -> bool:
            """Check if method is public"""
            return 'public' in modifiers
        
        def traverse_node(node: Node):
            if node.type == 'method_declaration':
                method_name = None
                parameters = []
                modifiers = get_modifiers(node)
                attributes = get_attributes(node)
                
                for child in node.children:
                    if child.type == 'identifier':
                        method_name = source_code[child.start_byte:child.end_byte]
                    elif child.type == 'parameter_list':
                        for param_child in child.children:
                            if param_child.type == 'parameter':
                                for param_part in param_child.children:
                                    if param_part.type == 'identifier':
                                        parameters.append(source_code[param_part.start_byte:param_part.end_byte])
                
                if method_name:
                    # Determine entry point type based on attributes and modifiers
                    entry_type = 'method'
                    if is_api_endpoint(attributes, modifiers):
                        entry_type = 'api_endpoint'
                    elif is_public_method(modifiers):
                        entry_type = 'public_method'
                    else:
                        entry_type = 'private_method'
                    
                    entry_point = EntryPoint(
                        name=method_name,
                        file_path=file_path,
                        line_number=node.start_point[0] + 1,
                        type=entry_type,
                        parameters=parameters
                    )
                    
                    # Add documentation from attributes
                    if attributes:
                        entry_point.documentation = ', '.join(attributes)
                    
                    entry_points.append(entry_point)
            
            elif node.type == 'class_declaration':
                class_name = None
                modifiers = get_modifiers(node)
                
                for child in node.children:
                    if child.type == 'identifier':
                        class_name = source_code[child.start_byte:child.end_byte]
                        break
                
                if class_name:
                    entry_type = 'public_class' if 'public' in modifiers else 'internal_class'
                    entry_points.append(EntryPoint(
                        name=class_name,
                        file_path=file_path,
                        line_number=node.start_point[0] + 1,
                        type=entry_type
                    ))
            
            elif node.type == 'interface_declaration':
                interface_name = None
                modifiers = get_modifiers(node)
                
                for child in node.children:
                    if child.type == 'identifier':
                        interface_name = source_code[child.start_byte:child.end_byte]
                        break
                
                if interface_name:
                    entry_type = 'public_interface' if 'public' in modifiers else 'internal_interface'
                    entry_points.append(EntryPoint(
                        name=interface_name,
                        file_path=file_path,
                        line_number=node.start_point[0] + 1,
                        type=entry_type
                    ))
            
            for child in node.children:
                traverse_node(child)
        
        traverse_node(tree.root_node)
        return entry_points
    
    def _count_lines_of_code(self, file_path: Path) -> int:
        """Count lines of code in a file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return sum(1 for line in f if line.strip() and not line.strip().startswith('#'))
        except:
            return 0
    
    def _extract_dependencies(self, project_path: Path, language: ProjectLanguage) -> List[str]:
        """Extract project dependencies"""
        dependencies = []
        
        # Python dependencies
        if language == ProjectLanguage.PYTHON:
            req_files = ['requirements.txt', 'pyproject.toml', 'setup.py', 'Pipfile']
            for req_file in req_files:
                file_path = project_path / req_file
                if file_path.exists():
                    try:
                        content = file_path.read_text()
                        if req_file == 'requirements.txt':
                            deps = [line.split('==')[0].split('>=')[0].split('<=')[0].strip() 
                                   for line in content.split('\n') 
                                   if line.strip() and not line.startswith('#')]
                            dependencies.extend(deps)
                    except:
                        continue
        
        # JavaScript/TypeScript dependencies
        elif language in [ProjectLanguage.JAVASCRIPT, ProjectLanguage.TYPESCRIPT]:
            package_json = project_path / 'package.json'
            if package_json.exists():
                try:
                    package_data = json.loads(package_json.read_text())
                    deps = list(package_data.get('dependencies', {}).keys())
                    dev_deps = list(package_data.get('devDependencies', {}).keys())
                    dependencies.extend(deps + dev_deps)
                except:
                    pass
        
        # Java dependencies
        elif language == ProjectLanguage.JAVA:
            pom_xml = project_path / 'pom.xml'
            if pom_xml.exists():
                try:
                    content = pom_xml.read_text()
                    # Simple regex to extract artifactId from dependencies
                    import re
                    artifacts = re.findall(r'<artifactId>([^<]+)</artifactId>', content)
                    dependencies.extend(artifacts)
                except:
                    pass
        
        return dependencies[:50]  # Limit to first 50 dependencies
    
    def analyze_project(self, project_path: Path, repository_name: str) -> ProjectInfo:
        """Analyze a project and extract metadata"""
        # Determine primary language
        language_counts = {}
        total_files = 0
        total_loc = 0
        
        for file_path in project_path.rglob('*'):
            if file_path.is_file() and not any(part.startswith('.') for part in file_path.parts):
                lang = self._detect_language(file_path)
                if lang != ProjectLanguage.UNKNOWN:
                    language_counts[lang] = language_counts.get(lang, 0) + 1
                    total_files += 1
                    total_loc += self._count_lines_of_code(file_path)
        
        # Determine primary language
        primary_language = ProjectLanguage.UNKNOWN
        if language_counts:
            primary_language = max(language_counts, key=language_counts.get)
        
        # Detect project type
        project_type = self._detect_project_type(project_path, primary_language)
        
        # Extract dependencies
        dependencies = self._extract_dependencies(project_path, primary_language)
        
        # Extract version from common files
        version = self._extract_version(project_path, primary_language)
        
        # Extract description
        description = self._extract_description(project_path)
        
        project_info = ProjectInfo(
            id=f"{repository_name}_{project_path.name}",
            name=project_path.name,
            repository_name=repository_name,
            language=primary_language,
            project_type=project_type,
            description=description,
            version=version,
            dependencies=dependencies,
            file_count=total_files,
            lines_of_code=total_loc,
            last_updated=datetime.now(),
            entry_points_count=0  # Will be updated when entry points are extracted
        )
        
        return project_info
    
    def extract_entry_points(self, project_path: Path) -> List[EntryPoint]:
        """Extract entry points from a project"""
        all_entry_points = []
        
        # First get the project info to know the project type
        project_language = self._get_primary_language(project_path)
        project_type = self._detect_project_type(project_path, project_language)
        
        for file_path in project_path.rglob('*'):
            if file_path.is_file() and not any(part.startswith('.') for part in file_path.parts):
                lang = self._detect_language(file_path)
                
                if lang == ProjectLanguage.UNKNOWN:
                    continue
                
                try:
                    # Handle UTF-8 BOM properly
                    with open(file_path, 'rb') as f:
                        raw_content = f.read()
                    
                    # Decode with BOM handling
                    if raw_content.startswith(b'\xef\xbb\xbf'):
                        source_code = raw_content.decode('utf-8-sig')
                    else:
                        source_code = raw_content.decode('utf-8')
                        
                    relative_path = str(file_path.relative_to(project_path))
                    
                    if lang == ProjectLanguage.PYTHON:
                        file_entry_points = self._extract_python_entry_points(source_code, relative_path)
                    elif lang in [ProjectLanguage.JAVASCRIPT, ProjectLanguage.TYPESCRIPT]:
                        file_entry_points = self._extract_javascript_entry_points(source_code, relative_path)
                    elif lang == ProjectLanguage.JAVA:
                        file_entry_points = self._extract_java_entry_points(source_code, relative_path)
                    elif lang == ProjectLanguage.CSHARP:
                        file_entry_points = self._extract_csharp_entry_points(source_code, relative_path)
                    else:
                        continue
                    
                    all_entry_points.extend(file_entry_points)
                    
                except Exception as e:
                    logger.warning(f"Failed to analyze file {file_path}: {e}")
                    continue
        
        # Filter entry points based on project type
        return self._filter_entry_points_by_project_type(all_entry_points, project_type)
    
    def _get_primary_language(self, project_path: Path) -> ProjectLanguage:
        """Get the primary language of the project"""
        language_counts = {}
        
        for file_path in project_path.rglob('*'):
            if file_path.is_file() and not any(part.startswith('.') for part in file_path.parts):
                lang = self._detect_language(file_path)
                if lang != ProjectLanguage.UNKNOWN:
                    language_counts[lang] = language_counts.get(lang, 0) + 1
        
        if language_counts:
            return max(language_counts, key=language_counts.get)
        return ProjectLanguage.UNKNOWN
    
    def _filter_entry_points_by_project_type(self, entry_points: List[EntryPoint], project_type: ProjectType) -> List[EntryPoint]:
        """Filter entry points based on project type to show only external interaction points"""
        
        if project_type == ProjectType.API:
            # For APIs, show only API endpoints (public HTTP endpoints)
            return [ep for ep in entry_points if ep.type == 'api_endpoint']
        
        elif project_type == ProjectType.LIBRARY:
            # For libraries, show only public classes, interfaces, and methods
            return [ep for ep in entry_points if ep.type in [
                'public_class', 'public_interface', 'public_method', 'public_function'
            ]]
        
        elif project_type == ProjectType.CLI:
            # For CLI applications, show main entry points and public command methods
            cli_entry_points = []
            for ep in entry_points:
                # Main methods or public methods that could be CLI commands
                if (ep.name.lower() in ['main', 'run', 'execute', 'cli', 'command'] or 
                    ep.type in ['public_method', 'public_function'] and 
                    any(keyword in ep.name.lower() for keyword in ['command', 'cmd', 'execute', 'run', 'parse', 'handle'])):
                    cli_entry_points.append(ep)
            return cli_entry_points
        
        elif project_type == ProjectType.WEB_APP:
            # For web apps, show routes, controllers, and public API methods
            return [ep for ep in entry_points if ep.type in [
                'api_endpoint', 'public_method', 'public_function', 'route'
            ]]
        
        elif project_type == ProjectType.MICROSERVICE:
            # For microservices, show API endpoints and service interfaces
            return [ep for ep in entry_points if ep.type in [
                'api_endpoint', 'public_interface', 'service_method', 'public_method'
            ]]
        
        else:
            # For unknown project types, show only clearly public interfaces
            return [ep for ep in entry_points if ep.type in [
                'public_class', 'public_interface', 'public_method', 'public_function', 'api_endpoint'
            ]]
    
    def _extract_version(self, project_path: Path, language: ProjectLanguage) -> Optional[str]:
        """Extract version from project files"""
        try:
            if language == ProjectLanguage.PYTHON:
                # Check setup.py, pyproject.toml, __init__.py
                version_files = ['setup.py', 'pyproject.toml', '__init__.py']
                for file_name in version_files:
                    file_path = project_path / file_name
                    if file_path.exists():
                        content = file_path.read_text()
                        version_match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
                        if version_match:
                            return version_match.group(1)
            
            elif language in [ProjectLanguage.JAVASCRIPT, ProjectLanguage.TYPESCRIPT]:
                package_json = project_path / 'package.json'
                if package_json.exists():
                    package_data = json.loads(package_json.read_text())
                    return package_data.get('version')
            
        except:
            pass
        
        return None
    
    def _extract_description(self, project_path: Path) -> Optional[str]:
        """Extract description from README or package files"""
        try:
            # Check README files
            readme_files = ['README.md', 'README.txt', 'README', 'readme.md']
            for readme_name in readme_files:
                readme_path = project_path / readme_name
                if readme_path.exists():
                    content = readme_path.read_text(encoding='utf-8')
                    lines = content.split('\n')
                    for line in lines:
                        line = line.strip()
                        if line and not line.startswith('#') and len(line) > 20:
                            return line[:200]  # First meaningful line, truncated
            
            # Check package.json
            package_json = project_path / 'package.json'
            if package_json.exists():
                package_data = json.loads(package_json.read_text())
                return package_data.get('description')
            
        except:
            pass
        
        return None
