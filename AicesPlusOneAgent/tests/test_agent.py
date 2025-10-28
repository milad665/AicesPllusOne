"""
Unit tests for C4 Architecture Agent

Run with: python -m pytest tests/test_agent.py
"""

import pytest
import json
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.schemas import (
    C4Architecture, ContextView, ContainerView, ComponentView,
    Person, PersonTypes, SoftwareSystem, Container, ContainerTypes,
    Component, Relationship
)
from src.memory_store import MemoryStore


class TestSchemas:
    """Test C4 schema models"""
    
    def test_person_creation(self):
        """Test creating a Person"""
        person = Person(
            Id="user1",
            Name="Test User",
            PersonType=PersonTypes.END_USER,
            Exists=True
        )
        assert person.Id == "user1"
        assert person.PersonType == PersonTypes.END_USER
    
    def test_software_system_creation(self):
        """Test creating a SoftwareSystem"""
        system = SoftwareSystem(
            Id="sys1",
            Name="Test System",
            Description="A test system",
            IsExternalSoftwareSystem=False,
            Exists=True
        )
        assert system.Id == "sys1"
        assert not system.IsExternalSoftwareSystem
    
    def test_relationship_creation(self):
        """Test creating a Relationship"""
        rel = Relationship(
            FromId="user1",
            ToId="sys1",
            Name="Uses"
        )
        assert rel.FromId == "user1"
        assert rel.ToId == "sys1"
    
    def test_context_view_creation(self):
        """Test creating a ContextView"""
        person = Person(
            Id="user1",
            Name="User",
            PersonType=PersonTypes.END_USER,
            Exists=True
        )
        system = SoftwareSystem(
            Id="sys1",
            Name="System",
            Description="Test",
            IsExternalSoftwareSystem=False,
            Exists=True
        )
        rel = Relationship(FromId="user1", ToId="sys1", Name="Uses")
        
        context = ContextView(
            Actors=[person],
            SoftwareSystems=[system],
            Relationships=[rel],
            C4PlantUmlScript="@startuml\n@enduml"
        )
        
        assert len(context.Actors) == 1
        assert len(context.SoftwareSystems) == 1
        assert len(context.Relationships) == 1
    
    def test_full_architecture_creation(self):
        """Test creating a complete C4Architecture"""
        context = ContextView(
            Actors=[],
            SoftwareSystems=[],
            Relationships=[],
            C4PlantUmlScript="@startuml\n@enduml"
        )
        container = ContainerView(
            Actors=[],
            Containers=[],
            Relationships=[],
            C4PlantUmlScript="@startuml\n@enduml"
        )
        component = ComponentView(
            Actors=[],
            Components=[],
            Relationships=[],
            C4PlantUmlScript="@startuml\n@enduml"
        )
        
        arch = C4Architecture(
            ContextView=context,
            ContainerView=container,
            ComponentView=component,
            ArchitectureExplanation="Test architecture"
        )
        
        assert arch.ArchitectureExplanation == "Test architecture"
        assert isinstance(arch.ContextView, ContextView)
    
    def test_architecture_json_serialization(self):
        """Test that C4Architecture can be serialized to JSON"""
        context = ContextView(
            Actors=[],
            SoftwareSystems=[],
            Relationships=[],
            C4PlantUmlScript="@startuml\n@enduml"
        )
        container = ContainerView(
            Actors=[],
            Containers=[],
            Relationships=[],
            C4PlantUmlScript="@startuml\n@enduml"
        )
        component = ComponentView(
            Actors=[],
            Components=[],
            Relationships=[],
            C4PlantUmlScript="@startuml\n@enduml"
        )
        
        arch = C4Architecture(
            ContextView=context,
            ContainerView=container,
            ComponentView=component,
            ArchitectureExplanation="Test"
        )
        
        # Should serialize without errors
        json_str = arch.model_dump_json()
        assert json_str
        
        # Should be valid JSON
        json_data = json.loads(json_str)
        assert "ContextView" in json_data
        assert "ContainerView" in json_data
        assert "ComponentView" in json_data


class TestMemoryStore:
    """Test memory store functionality"""
    
    @pytest.fixture
    def temp_memory(self, tmp_path):
        """Create a temporary memory store"""
        memory_path = tmp_path / "test_memory.json"
        return MemoryStore(str(memory_path))
    
    def test_init_creates_storage(self, temp_memory):
        """Test that initialization creates storage file"""
        assert temp_memory.storage_path.exists()
    
    def test_save_and_load_architecture(self, temp_memory):
        """Test saving and loading architecture"""
        # Create test architecture
        context = ContextView(
            Actors=[],
            SoftwareSystems=[],
            Relationships=[],
            C4PlantUmlScript="@startuml\n@enduml"
        )
        container = ContainerView(
            Actors=[],
            Containers=[],
            Relationships=[],
            C4PlantUmlScript="@startuml\n@enduml"
        )
        component = ComponentView(
            Actors=[],
            Components=[],
            Relationships=[],
            C4PlantUmlScript="@startuml\n@enduml"
        )
        
        arch = C4Architecture(
            ContextView=context,
            ContainerView=container,
            ComponentView=component,
            ArchitectureExplanation="Test save/load"
        )
        
        # Save
        temp_memory.save_architecture(arch)
        
        # Load
        loaded = temp_memory.load_architecture()
        
        assert loaded is not None
        assert loaded.ArchitectureExplanation == "Test save/load"
    
    def test_load_empty_returns_none(self, temp_memory):
        """Test that loading from empty storage returns None"""
        loaded = temp_memory.load_architecture()
        assert loaded is None
    
    def test_clear(self, temp_memory):
        """Test clearing memory"""
        # Create and save architecture
        context = ContextView(
            Actors=[],
            SoftwareSystems=[],
            Relationships=[],
            C4PlantUmlScript="@startuml\n@enduml"
        )
        container = ContainerView(
            Actors=[],
            Containers=[],
            Relationships=[],
            C4PlantUmlScript="@startuml\n@enduml"
        )
        component = ComponentView(
            Actors=[],
            Components=[],
            Relationships=[],
            C4PlantUmlScript="@startuml\n@enduml"
        )
        
        arch = C4Architecture(
            ContextView=context,
            ContainerView=container,
            ComponentView=component,
            ArchitectureExplanation="To be cleared"
        )
        
        temp_memory.save_architecture(arch)
        
        # Clear
        temp_memory.clear()
        
        # Should be empty
        loaded = temp_memory.load_architecture()
        assert loaded is None
    
    def test_get_metadata(self, temp_memory):
        """Test getting metadata"""
        metadata = temp_memory.get_metadata()
        assert "created_at" in metadata
        assert "version" in metadata


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
