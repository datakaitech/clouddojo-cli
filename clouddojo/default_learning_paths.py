#!/usr/bin/env python3
"""
Default Learning Paths - Self-contained path definitions
"""

from clouddojo.scenario_metadata import LearningPathMetadata
from typing import List

class DockerBasicsPath(LearningPathMetadata):
    """Container Fundamentals learning path"""
    
    def get_path_id(self) -> str:
        return "docker-basics"
    
    def get_name(self) -> str:
        return "Container Fundamentals"
    
    def get_description(self) -> str:
        return "Master Docker containers and basic troubleshooting"
    
    def get_difficulty(self) -> str:
        return "beginner"
    
    def get_estimated_time(self) -> str:
        return "2-3 hours"
    
    def get_prerequisites(self) -> List[str]:
        return []
    
    def get_icon(self) -> str:
        return "🐋"

class K8sEssentialsPath(LearningPathMetadata):
    """Kubernetes Warrior learning path"""
    
    def get_path_id(self) -> str:
        return "k8s-essentials"
    
    def get_name(self) -> str:
        return "Kubernetes Warrior"
    
    def get_description(self) -> str:
        return "Debug pods, services, and resource issues"
    
    def get_difficulty(self) -> str:
        return "intermediate"
    
    def get_estimated_time(self) -> str:
        return "3-4 hours"
    
    def get_prerequisites(self) -> List[str]:
        return ["docker-basics"]
    
    def get_icon(self) -> str:
        return "⚓"

class ProductionSREPath(LearningPathMetadata):
    """Production SRE Master learning path"""
    
    def get_path_id(self) -> str:
        return "production-sre"
    
    def get_name(self) -> str:
        return "Production SRE Master"
    
    def get_description(self) -> str:
        return "Handle real-world production incidents"
    
    def get_difficulty(self) -> str:
        return "advanced"
    
    def get_estimated_time(self) -> str:
        return "4-6 hours"
    
    def get_prerequisites(self) -> List[str]:
        return ["k8s-essentials"]
    
    def get_icon(self) -> str:
        return "🔥"

def register_default_paths():
    """Register default learning paths"""
    from clouddojo.metadata_registry import registry
    
    registry.register_learning_path(DockerBasicsPath())
    registry.register_learning_path(K8sEssentialsPath())
    registry.register_learning_path(ProductionSREPath())