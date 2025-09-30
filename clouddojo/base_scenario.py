"""
Base scenario class that all scenarios must inherit from
""" 

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
from clouddojo.scenario_metadata import ScenarioMetadata

class BaseScenario(ABC):
    """Base class for all scenarios"""
    
    def __init__(self, name: str):
        self.name = name
        # self.state_file = Path.home() / '.sadservers' / f'{name}.json'
        self.state_file = Path.home() / '.clouddojo' / f'{name}.json'
        self.state_file.parent.mkdir(exist_ok=True)
    
    @abstractmethod
    def start(self) -> Dict[str, Any]:
        """
        Start the scenario. 
        
        Returns:
            Dict with keys:
            - success (bool): Whether startup was successful
            - connection_info (str, optional): How to connect to the environment
            - instructions (str, optional): What the user should do
            - error (str, optional): Error message if success=False
        """
        pass
    
    @abstractmethod
    def stop(self) -> bool:
        """
        Stop the scenario and clean up resources.
        
        Returns:
            bool: True if cleanup was successful, False otherwise
        """
        pass
    
    @abstractmethod
    def status(self) -> Dict[str, Any]:
        """
        Get current status of the scenario.
        
        Returns:
            Dict with keys:
            - running (bool): Whether the scenario is currently running
            - details (str): Additional status information
        """
        pass
    
    @abstractmethod
    def check(self) -> Dict[str, Any]:
        """
        Check if the scenario has been solved correctly.
        
        Returns:
            Dict with keys:
            - passed (bool): Whether all checks passed
            - feedback (str): Feedback on current state
            - hints (str, optional): Hints for solving if not passed
        """
        pass
    
    @abstractmethod
    def reset(self) -> bool:
        """
        Reset the scenario to its original broken state.
        
        Returns:
            bool: True if reset was successful, False otherwise
        """
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Brief description of what's broken in this scenario"""
        pass
    
    @property
    @abstractmethod
    def difficulty(self) -> str:
        """Scenario difficulty: 'beginner', 'intermediate', or 'advanced'"""
        pass
    
    @property
    @abstractmethod
    def technologies(self) -> list:
        """List of technologies involved (e.g., ['nginx', 'docker', 'linux'])"""
        pass
    
    def get_metadata(self) -> Optional[ScenarioMetadata]:
        """Get scenario metadata if implemented"""
        return None
    
    def save_state(self, state: Dict[str, Any]):
        """Save scenario state to disk"""
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)
    
    def load_state(self) -> Dict[str, Any]:
        """Load scenario state from disk"""
        if self.state_file.exists():
            with open(self.state_file, 'r') as f:
                return json.load(f)
        return {}
    
    def clear_state(self):
        """Clear scenario state"""
        if self.state_file.exists():
            self.state_file.unlink()