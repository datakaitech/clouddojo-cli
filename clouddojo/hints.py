#!/usr/bin/env python3
"""
CloudDojo Hints System - Progressive help for learners
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from clouddojo.metadata_registry import registry

@dataclass
class Hint:
    """Represents a single hint"""
    level: int  # 1=gentle nudge, 2=specific direction, 3=detailed help, 4=solution
    title: str
    content: str
    command: Optional[str] = None  # Optional command to run

class HintsManager:
    """Manages progressive hints for scenarios using metadata registry"""
    
    def __init__(self):
        pass  # No longer need to load hardcoded hints
    
    def get_hint(self, scenario_name: str, hint_level: int):
        """Get a specific hint for a scenario"""
        return registry.get_hint(scenario_name, hint_level)
    
    def get_next_hint(self, scenario_name: str, current_level: int):
        """Get the next available hint"""
        return self.get_hint(scenario_name, current_level + 1)
    
    def get_max_hint_level(self, scenario_name: str) -> int:
        """Get the maximum hint level available for a scenario"""
        return registry.get_max_hint_level(scenario_name)
    
    def has_hints(self, scenario_name: str) -> bool:
        """Check if a scenario has hints available"""
        return registry.has_hints(scenario_name)
    
    def add_scenario_hints(self, scenario_name: str, hints):
        """Add hints for a new scenario (deprecated - use scenario metadata)"""
        pass  # Hints now come from scenario metadata