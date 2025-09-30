#!/usr/bin/env python3
"""
CloudDojo Learning Paths - Structured learning progression
"""

from typing import Dict, List, Optional
from enum import Enum
from dataclasses import dataclass
from clouddojo.metadata_registry import registry
from clouddojo.scenario_metadata import LearningPathMetadata

class PathStatus(Enum):
    LOCKED = "locked"
    AVAILABLE = "available" 
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

@dataclass
class LearningPath:
    """Represents a structured learning path"""
    id: str
    name: str
    description: str
    difficulty: str  # beginner, intermediate, advanced
    estimated_time: str  # "2-3 hours"
    scenarios: List[str]  # List of scenario names in order
    prerequisites: List[str] = None  # Other path IDs required
    icon: str = "🎯"

class LearningPathManager:
    """Manages learning paths and progression using metadata registry"""
    
    def __init__(self):
        pass  # Paths now come from registry
    
    # Removed hardcoded paths - now using registry
    
    def get_path(self, path_id: str):
        """Get a specific learning path"""
        path_metadata = registry.get_learning_paths().get(path_id)
        if not path_metadata:
            return None
        
        scenarios = registry.get_scenarios_for_path(path_id)
        return {
            "id": path_metadata.get_path_id(),
            "name": path_metadata.get_name(),
            "description": path_metadata.get_description(),
            "difficulty": path_metadata.get_difficulty(),
            "estimated_time": path_metadata.get_estimated_time(),
            "scenarios": scenarios,
            "prerequisites": path_metadata.get_prerequisites(),
            "icon": path_metadata.get_icon()
        }
    
    def get_available_paths(self, completed_scenarios: List[str] = None):
        """Get paths available to the user based on their progress"""
        if completed_scenarios is None:
            completed_scenarios = []
        
        available = []
        for path_id in registry.get_learning_paths():
            path = self.get_path(path_id)
            if path and self._is_path_available(path, completed_scenarios):
                available.append(path)
        
        return sorted(available, key=lambda p: ["beginner", "intermediate", "advanced"].index(p["difficulty"]))
    
    def _is_path_available(self, path: dict, completed_scenarios: List[str]) -> bool:
        """Check if a path is available based on prerequisites"""
        if not path["prerequisites"]:
            return True
        
        # Check if all prerequisite paths are completed
        for prereq_id in path["prerequisites"]:
            prereq_path = self.get_path(prereq_id)
            if not prereq_path:
                continue
            
            # Check if all scenarios in prerequisite path are completed
            prereq_completed = all(scenario in completed_scenarios for scenario in prereq_path["scenarios"])
            if not prereq_completed:
                return False
        
        return True
    
    def get_path_progress(self, path_id: str, completed_scenarios: List[str]) -> Dict:
        """Get progress information for a specific path"""
        path = self.get_path(path_id)
        if not path:
            return {}
        
        completed_in_path = [s for s in path["scenarios"] if s in completed_scenarios]
        total_scenarios = len(path["scenarios"])
        progress_percent = (len(completed_in_path) / total_scenarios) * 100 if total_scenarios > 0 else 0
        
        if progress_percent == 0:
            status = PathStatus.AVAILABLE if self._is_path_available(path, completed_scenarios) else PathStatus.LOCKED
        elif progress_percent == 100:
            status = PathStatus.COMPLETED
        else:
            status = PathStatus.IN_PROGRESS
        
        return {
            "path": path,
            "status": status,
            "completed_scenarios": completed_in_path,
            "total_scenarios": total_scenarios,
            "progress_percent": progress_percent,
            "next_scenario": self._get_next_scenario(path, completed_scenarios)
        }
    
    def _get_next_scenario(self, path: dict, completed_scenarios: List[str]) -> Optional[str]:
        """Get the next scenario to complete in a path"""
        for scenario in path["scenarios"]:
            if scenario not in completed_scenarios:
                return scenario
        return None
    
    def get_recommended_next_step(self, completed_scenarios: List[str]) -> Optional[Dict]:
        """Get recommended next step for the user"""
        # Find paths in progress
        for path_id in registry.get_learning_paths():
            path = self.get_path(path_id)
            if not path:
                continue
                
            progress = self.get_path_progress(path_id, completed_scenarios)
            if progress.get("status") == PathStatus.IN_PROGRESS:
                return {
                    "type": "continue_path",
                    "path": path,
                    "next_scenario": progress.get("next_scenario"),
                    "message": f"Continue your {path['name']} journey"
                }
        
        # Find available paths to start
        available_paths = self.get_available_paths(completed_scenarios)
        if available_paths:
            path = available_paths[0]  # Recommend easiest available
            return {
                "type": "start_path", 
                "path": path,
                "next_scenario": path["scenarios"][0] if path["scenarios"] else None,
                "message": f"Start your {path['name']} journey"
            }
        
        return None