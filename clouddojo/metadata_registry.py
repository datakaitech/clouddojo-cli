#!/usr/bin/env python3
"""
Dynamic Metadata Registry - Discovers scenario metadata automatically
"""

from typing import Dict, List, Optional, Any
from clouddojo.scenario_metadata import ScenarioMetadata, StoryContext, Hint, LearningPathMetadata

class MetadataRegistry:
    """Centralized registry that discovers metadata from scenarios"""
    
    def __init__(self):
        self._scenario_metadata: Dict[str, ScenarioMetadata] = {}
        self._learning_paths: Dict[str, LearningPathMetadata] = {}
    
    def register_scenario(self, scenario_name: str, scenario_instance):
        """Register a scenario and its metadata"""
        metadata = scenario_instance.get_metadata()
        if metadata:
            self._scenario_metadata[scenario_name] = metadata
    
    def register_learning_path(self, path_metadata: LearningPathMetadata):
        """Register a learning path"""
        self._learning_paths[path_metadata.get_path_id()] = path_metadata
    
    def get_story_context(self, scenario_name: str) -> Optional[StoryContext]:
        """Get story context for a scenario"""
        metadata = self._scenario_metadata.get(scenario_name)
        return metadata.get_story_context() if metadata else None
    
    def get_hints(self, scenario_name: str) -> List[Hint]:
        """Get hints for a scenario"""
        metadata = self._scenario_metadata.get(scenario_name)
        return metadata.get_hints() if metadata else []
    
    def get_completion_story(self, scenario_name: str, time_taken: int) -> Optional[str]:
        """Get completion story for a scenario"""
        metadata = self._scenario_metadata.get(scenario_name)
        return metadata.get_completion_story(time_taken) if metadata else None
    
    def get_scenarios_for_path(self, path_id: str) -> List[str]:
        """Get all scenarios that belong to a learning path"""
        scenarios = []
        for scenario_name, metadata in self._scenario_metadata.items():
            if metadata.get_learning_path() == path_id:
                scenarios.append(scenario_name)
        return scenarios
    
    def get_learning_paths(self) -> Dict[str, LearningPathMetadata]:
        """Get all registered learning paths"""
        return self._learning_paths.copy()
    
    def has_hints(self, scenario_name: str) -> bool:
        """Check if scenario has hints"""
        return len(self.get_hints(scenario_name)) > 0
    
    def get_max_hint_level(self, scenario_name: str) -> int:
        """Get maximum hint level for scenario"""
        hints = self.get_hints(scenario_name)
        return max(hint.level for hint in hints) if hints else 0
    
    def get_hint(self, scenario_name: str, level: int) -> Optional[Hint]:
        """Get specific hint level for scenario"""
        hints = self.get_hints(scenario_name)
        for hint in hints:
            if hint.level == level:
                return hint
        return None

# Global registry instance
registry = MetadataRegistry()