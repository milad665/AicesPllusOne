"""
C4 Architecture Agent using Google's ADK

This agent uses Gemini 2.5 to generate C4 architecture diagrams
from code analysis data.
"""

import os
import json
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv
import google.generativeai as genai

from .schemas import C4Architecture, ContextView, ContainerView, ComponentView
from .code_analyzer import CodeAnalyzer


load_dotenv()


class C4ArchitectureAgent:
    """
    AI Agent for generating C4 architecture diagrams
    
    Uses Google's Gemini 2.5 model and code analysis service to
    generate structured C4 architecture diagrams.
    """
    
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the C4 Architecture Agent
        
        Args:
            api_key: Google API key for Gemini
        """
        # Configure Gemini API
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY is required")
        
        # For google-generativeai 0.3.2, must set env var before importing
        # The configure() method doesn't work reliably in this version
        os.environ["GOOGLE_API_KEY"] = self.api_key
        genai.configure(api_key=self.api_key)
        
        # Initialize Gemini model (using gemini-2.0-flash-exp as 2.5 proxy)
        # Note: Adjust model name based on actual availability
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Initialize components
        self.code_analyzer = CodeAnalyzer()
        
        # Initialize storage
        storage_type = os.getenv("STORAGE_TYPE", "local")
        from .storage import get_storage_provider
        self.storage = get_storage_provider(storage_type)
        
        # System prompt for C4 generation
        self.system_prompt = self._build_system_prompt()
    
    def _build_system_prompt(self) -> str:
        """Build the system prompt for the agent"""
        return """You are an expert software architect specializing in C4 architecture diagrams.

Your role is to analyze code projects and generate comprehensive C4 architecture diagrams at three levels:
1. Context View - Shows the system in its environment with users and external systems
2. Container View - Shows the high-level technology choices and responsibilities
3. Component View - Shows the internal structure of containers

You must generate output in strict JSON format following the provided schema.
Each view must include:
- Relevant actors/persons
- System elements (systems, containers, or components)
- Relationships between elements
- PlantUML C4 script for visualization

When generating PlantUML scripts, use proper C4-PlantUML syntax:
- Use @startuml and @enduml tags
- Include !include statements for C4 libraries
- Use Person(), System(), Container(), Component() macros appropriately
- Use Rel() for relationships

Always ensure IDs are unique and relationships reference valid IDs.
Provide clear, technical descriptions for all elements.
Before returning the final result, filter out unrelated classes, methods and components. 
Based on the programming language and service type, only include relevant elements that contribute to the architecture.
For example in the container view, only include services and processes that are visible from outside not the internal components.
"""
    
    async def generate_c4_architecture(self) -> C4Architecture:
        """
        Generate C4 architecture from code analysis and save to storage.
        This forces a fresh analysis and AI generation.
        
        Returns:
            Complete C4 architecture
        """
        # Get projects from code analyzer
        print("Fetching projects from code analyzer...")
        projects = await self.code_analyzer.get_projects()
        print(f"Found {len(projects)} projects")
        
        # Collect detailed project information
        project_details = []
        for project in projects:
            project_id = project.get('id')
            print(f"Processing project: {project.get('name', 'Unknown')}")
            if project_id:
                try:
                    print(f"  Fetching entrypoints for {project_id}...")
                    entrypoints = await self.code_analyzer.get_project_entrypoints(project_id)
                    print(f"  Found {len(entrypoints)} entrypoints")
                    project['entrypoints'] = entrypoints
                except Exception as e:
                    print(f"Warning: Could not get entrypoints for {project_id}: {e}")
                    project['entrypoints'] = []
            project_details.append(project)
        
        print("Sending to Gemini for architecture generation...")
        
        # Generate architecture using Gemini
        architecture = await self._generate_with_gemini(project_details)
        
        # Save to storage
        self.storage.save(architecture)
        
        return architecture
    
    async def _generate_with_gemini(
        self,
        project_details: List[Dict[str, Any]]
    ) -> C4Architecture:
        """
        Generate C4 architecture using Gemini
        
        Args:
            project_details: List of project information
            
        Returns:
            Generated C4 architecture
        """
        # Get the JSON schema example
        schema_example = """{
  "ContextView": {
    "Actors": [
      {
        "Id": "user1",
        "Name": "Customer",
        "PersonType": "EndUser",
        "Exists": true
      }
    ],
    "SoftwareSystems": [
      {
        "Id": "sys1",
        "Name": "Main System",
        "Description": "The primary software system",
        "IsExternalSoftwareSystem": false,
        "Exists": true
      }
    ],
    "Relationships": [
      {
        "FromId": "user1",
        "ToId": "sys1",
        "Name": "Uses"
      }
    ],
    "C4PlantUmlScript": "@startuml\\n!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Context.puml\\nPerson(user1, \\"Customer\\", \\"EndUser\\")\\nSystem(sys1, \\"Main System\\", \\"The primary software system\\")\\nRel(user1, sys1, \\"Uses\\")\\n@enduml"
  },
  "ContainerView": {
    "Actors": [],
    "Containers": [
      {
        "Id": "cont1",
        "Name": "Web Application",
        "ContainerType": "Application",
        "Description": "Web frontend",
        "ContainerTechnology": "React",
        "ParentSoftwareSystemId": "sys1",
        "CorrespondingProjectId": "",
        "TechnologyOrLanguage": "JavaScript",
        "Exists": true
      }
    ],
    "Relationships": [],
    "C4PlantUmlScript": "@startuml\\n!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Container.puml\\n@enduml"
  },
  "ComponentView": {
    "Actors": [],
    "Components": [
      {
        "Id": "comp1",
        "Name": "User Controller",
        "Description": "Handles user requests",
        "ComponentTechnology": "Spring MVC",
        "ParentContainerId": "cont1",
        "CorrespondingProjectId": "",
        "TechnologyOrLanguage": "Java",
        "Exists": true
      }
    ],
    "Relationships": [],
    "C4PlantUmlScript": "@startuml\\n!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Component.puml\\n@enduml"
  },
  "ArchitectureExplanation": "This is the system architecture"
}"""
        
        # Prepare the prompt
        prompt = f"""{self.system_prompt}

Based on the following code analysis data, generate a complete C4 architecture diagram.

CODE ANALYSIS DATA:
{json.dumps(project_details, indent=2)}

You MUST return JSON in EXACTLY this structure (use the same field names with exact capitalization):
{schema_example}

IMPORTANT REQUIREMENTS:
- Use "Actors", "SoftwareSystems", "Containers", "Components", "Relationships" (capital letters!)
- Each field name MUST match exactly as shown in the example
- PersonType must be one of: "EndUser", "Administrator", "Stakeholder", "ExternalPartner", "SystemDeveloper"
- ContainerType must be either "Application" or "Datastore"
- All IDs must be unique strings
- C4PlantUmlScript must be valid PlantUML syntax
- Return ONLY valid JSON matching the exact structure above. No additional text or markdown.
"""
        
        # Generate content
        # Note: response_mime_type not supported in google-generativeai 0.3.2
        response = await self.model.generate_content_async(
            prompt,
            generation_config=genai.GenerationConfig(
                temperature=0.2
            )
        )
        
        # Log the response for debugging
        print(f"Gemini response text: {response.text[:500] if response.text else 'EMPTY'}")
        
        # Parse response - handle markdown code blocks
        response_text = response.text.strip()
        
        # Remove markdown code block markers if present
        if response_text.startswith("```json"):
            response_text = response_text[7:]  # Remove ```json
        elif response_text.startswith("```"):
            response_text = response_text[3:]  # Remove ```
        
        if response_text.endswith("```"):
            response_text = response_text[:-3]  # Remove trailing ```
        
        response_text = response_text.strip()
        
        try:
            architecture_data = json.loads(response_text)
            
            # Handle if Gemini wraps response in "C4Architecture" key
            if "C4Architecture" in architecture_data and isinstance(architecture_data["C4Architecture"], dict):
                architecture_data = architecture_data["C4Architecture"]
            
            return C4Architecture(**architecture_data)
        except json.JSONDecodeError as e:
            # Fallback: create a minimal valid architecture
            print(f"Warning: Failed to parse Gemini response: {e}")
            print(f"Response was: {response.text[:1000] if response.text else 'EMPTY'}")
            return self._create_minimal_architecture(project_details)
    
    def _create_minimal_architecture(
        self,
        project_details: List[Dict[str, Any]]
    ) -> C4Architecture:
        """
        Create a minimal valid C4 architecture from project data
        
        Args:
            project_details: List of project information
            
        Returns:
            Minimal C4 architecture
        """
        from .schemas import Person, PersonTypes, SoftwareSystem, Container, ContainerTypes, Component, Relationship
        
        # Create basic context view
        context_view = ContextView(
            Actors=[
                Person(Id="user1", Name="User", PersonType=PersonTypes.END_USER, Exists=True)
            ],
            SoftwareSystems=[
                SoftwareSystem(
                    Id=f"sys_{i}",
                    Name=p.get('name', 'Unknown'),
                    Description=p.get('description', 'Software System'),
                    IsExternalSoftwareSystem=False,
                    Exists=True
                ) for i, p in enumerate(project_details[:3])
            ],
            Relationships=[],
            C4PlantUmlScript="@startuml\n!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Context.puml\n@enduml"
        )
        
        # Create basic container view
        container_view = ContainerView(
            Actors=[],
            Containers=[
                Container(
                    Id=f"cont_{i}",
                    Name=p.get('name', 'Unknown'),
                    ContainerType=ContainerTypes.APPLICATION,
                    Description=p.get('description', 'Container'),
                    ContainerTechnology=p.get('language', 'unknown'),
                    ParentSoftwareSystemId=f"sys_{i}",
                    CorrespondingProjectId=p.get('id', ''),
                    TechnologyOrLanguage=p.get('language', 'unknown'),
                    Exists=True
                ) for i, p in enumerate(project_details[:3])
            ],
            Relationships=[],
            C4PlantUmlScript="@startuml\n!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Container.puml\n@enduml"
        )
        
        # Create basic component view
        component_view = ComponentView(
            Actors=[],
            Components=[],
            Relationships=[],
            C4PlantUmlScript="@startuml\n!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Component.puml\n@enduml"
        )
        
        return C4Architecture(
            ContextView=context_view,
            ContainerView=container_view,
            ComponentView=component_view,
            ArchitectureExplanation="Architecture generated from code analysis"
        )
    
    async def update_from_plantuml(
        self,
        plantuml_script: str,
        view_type: str = "all"
    ) -> C4Architecture:
        """
        Update C4 architecture from PlantUML script
        
        Args:
            plantuml_script: PlantUML script to parse and update
            view_type: Which view to update ("context", "container", "component", or "all")
            
        Returns:
            Updated C4 architecture
        """
        # Get current architecture or create new one
        current = self.storage.load()
        
        # Use Gemini to parse PlantUML and update architecture
        prompt = f"""{self.system_prompt}

Update the C4 architecture based on the following PlantUML script.

PLANTUML SCRIPT:
{plantuml_script}

VIEW TO UPDATE: {view_type}

CURRENT ARCHITECTURE:
{current.model_dump_json(indent=2) if current else "None"}

Parse the PlantUML script and update the appropriate view(s) in the C4 architecture.
Return the complete updated architecture in JSON format.
"""
        
        # Note: response_mime_type not supported in google-generativeai 0.3.2
        response = await self.model.generate_content_async(
            prompt,
            generation_config=genai.GenerationConfig(
                temperature=0.2
            )
        )
        
        try:
            architecture_data = json.loads(response.text)
            updated_architecture = C4Architecture(**architecture_data)
            
            # Save to storage
            self.storage.save(updated_architecture)
            
            return updated_architecture
        except (json.JSONDecodeError, Exception) as e:
            print(f"Error updating from PlantUML: {e}")
            if current:
                return current
            raise
    
    async def find_relevant_element(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Find the architectural element relevant to a specific file.
        
        Args:
            file_path: Absolute or relative path to the file.
            
        Returns:
            Dictionary containing the element and its view script, or None.
        """
        architecture = await self.get_current_architecture()
        if not architecture:
            return None
            
        file_path_lower = file_path.lower()
        
        # Strategy 1: Check Components (Level 3)
        # We look for fuzzy matches in Description or Name, or implicit project ID match?
        # Since we don't store file paths in C4, we use heuristics.
        
        for component in architecture.ComponentView.Components:
            # Heuristic: If component name appears in file path (e.g., "AuthController" in "auth_controller.py")
            if component.Name.lower().replace(" ", "") in file_path_lower.replace("_", ""):
                 return {
                     "element": component.model_dump(mode='json'),
                     "view_type": "component",
                     "uml": architecture.ComponentView.C4PlantUmlScript
                 }
                 
        # Strategy 2: Check Containers (Level 2)
        for container in architecture.ContainerView.Containers:
            # Heuristic: Match project ID or name
            # E.g., if file path contains "AicesPlusOneAgent" and container name matches
            if container.Name.lower().replace(" ", "") in file_path_lower.replace("_", ""):
                 return {
                     "element": container.model_dump(mode='json'),
                     "view_type": "container",
                     "uml": architecture.ContainerView.C4PlantUmlScript
                 }

        # Strategy 3: Default to Container View if file seems to belong to a known project
        # This part requires knowing the ProjectRoot, which we might not have perfect access to.
        # For now, we return None if no strict heuristic match.
        return None

    async def get_current_architecture(self) -> Optional[C4Architecture]:
        """
        Get the current C4 architecture from memory
        
        Returns:
            Current architecture or None
        """
        return self.storage.load()
    
    async def close(self):
        """Clean up resources"""
        await self.code_analyzer.close()
