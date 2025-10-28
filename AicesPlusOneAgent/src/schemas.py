"""
C4 Architecture JSON Schema Definitions
"""
from typing import List
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum


class PersonTypes(str, Enum):
    """Types of persons/actors"""
    END_USER = "EndUser"
    ADMINISTRATOR = "Administrator"
    STAKEHOLDER = "Stakeholder"
    EXTERNAL_PARTNER = "ExternalPartner"
    SYSTEM_DEVELOPER = "SystemDeveloper"


class ContainerTypes(str, Enum):
    """Types of containers"""
    APPLICATION = "Application"
    DATASTORE = "Datastore"


class Person(BaseModel):
    """Person/Actor in the system"""
    Id: str
    Name: str
    PersonType: PersonTypes
    Exists: bool


class SoftwareSystem(BaseModel):
    """Software System in the context view"""
    Id: str
    Name: str
    Description: str
    IsExternalSoftwareSystem: bool
    Exists: bool


class Relationship(BaseModel):
    """Relationship between components"""
    FromId: str
    ToId: str
    Name: str


class ContextView(BaseModel):
    """System Context View (C4 Level 1)"""
    Actors: List[Person] = []
    SoftwareSystems: List[SoftwareSystem] = []
    Relationships: List[Relationship] = []
    C4PlantUmlScript: str


class Container(BaseModel):
    """Container in the container view"""
    Id: str
    Name: str
    ContainerType: ContainerTypes
    Description: str
    ContainerTechnology: str
    ParentSoftwareSystemId: str
    CorrespondingProjectId: str
    TechnologyOrLanguage: str
    Exists: bool


class ContainerView(BaseModel):
    """Container View (C4 Level 2)"""
    Actors: List[Person] = []
    Containers: List[Container] = []
    Relationships: List[Relationship] = []
    C4PlantUmlScript: str


class Component(BaseModel):
    """Component in the component view"""
    Id: str
    Name: str
    Description: str
    ComponentTechnology: str
    ParentContainerId: str
    CorrespondingProjectId: str
    TechnologyOrLanguage: str
    Exists: bool


class ComponentView(BaseModel):
    """Component View (C4 Level 3)"""
    Actors: List[Person] = []
    Components: List[Component] = []
    Relationships: List[Relationship] = []
    C4PlantUmlScript: str


class C4Architecture(BaseModel):
    """Complete C4 Architecture Model"""
    ContextView: ContextView
    ContainerView: ContainerView
    ComponentView: ComponentView
    ArchitectureExplanation: str
