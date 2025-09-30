#!/usr/bin/env python3
"""
Scenario Metadata System - Abstract classes for scenario self-description
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum

class CompanyType(Enum):
    STARTUP = "startup"
    ENTERPRISE = "enterprise" 
    ECOMMERCE = "ecommerce"
    FINTECH = "fintech"
    GAMING = "gaming"
    HEALTHCARE = "healthcare"

@dataclass
class StoryContext:
    """Narrative context for a scenario"""
    company_name: str
    company_type: CompanyType
    your_role: str
    situation: str
    urgency: str  # low, medium, high, critical
    stakeholders: List[str]
    business_impact: str
    success_criteria: str

@dataclass
class Hint:
    """Represents a single hint"""
    level: int  # 1=gentle nudge, 2=specific direction, 3=detailed help, 4=solution
    title: str
    content: str
    command: Optional[str] = None

class ScenarioMetadata(ABC):
    """Abstract base class for scenario metadata"""
    
    @abstractmethod
    def get_story_context(self) -> Optional[StoryContext]:
        """Return story context for this scenario"""
        pass
    
    @abstractmethod
    def get_hints(self) -> List[Hint]:
        """Return progressive hints for this scenario"""
        pass
    
    @abstractmethod
    def get_learning_path(self) -> Optional[str]:
        """Return which learning path this scenario belongs to"""
        pass
    
    @abstractmethod
    def get_completion_story(self, time_taken: int) -> str:
        """Return completion story based on performance"""
        pass

class LearningPathMetadata(ABC):
    """Abstract base class for learning path definitions"""
    
    @abstractmethod
    def get_path_id(self) -> str:
        """Return unique path identifier"""
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Return human-readable path name"""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """Return path description"""
        pass
    
    @abstractmethod
    def get_difficulty(self) -> str:
        """Return difficulty: beginner, intermediate, advanced"""
        pass
    
    @abstractmethod
    def get_estimated_time(self) -> str:
        """Return estimated completion time"""
        pass
    
    @abstractmethod
    def get_prerequisites(self) -> List[str]:
        """Return list of prerequisite path IDs"""
        pass
    
    @abstractmethod
    def get_icon(self) -> str:
        """Return path icon/emoji"""
        pass