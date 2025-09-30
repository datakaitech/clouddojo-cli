"""
Base class for Kubernetes scenarios that provides common functionality
"""

import subprocess
from pathlib import Path
from typing import Dict, Any
from abc import abstractmethod
from .base_scenario import BaseScenario

class K8sBaseScenario(BaseScenario):
    """Base class for all Kubernetes scenarios"""
    
    def __init__(self, name: str):
        super().__init__(name)
        # Get manifests directory relative to scenario directory
        self.manifests_dir = Path(__file__).parent / 'scenarios' / name / 'manifests'

    @abstractmethod
    def start(self) -> Dict[str, Any]:
        """
        Start the Kubernetes scenario.
        
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
        Stop the Kubernetes scenario and cleanup resources.
        
        Returns:
            bool: True if cleanup successful, False otherwise
        """
        pass

    @abstractmethod 
    def status(self) -> Dict[str, Any]:
        """
        Get current status of Kubernetes resources.
        
        Returns:
            Dict with keys:
            - running (bool): Whether resources are running
            - details (str): Additional status information
        """
        pass

    @abstractmethod
    def check(self) -> Dict[str, Any]:
        """
        Check if scenario is solved correctly.
        
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
        Reset Kubernetes resources to original state.
        
        Returns:
            bool: True if reset successful, False otherwise
        """
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Brief description of what's broken in this K8s scenario"""
        pass

    @property
    @abstractmethod
    def difficulty(self) -> str:
        """Scenario difficulty: 'beginner', 'intermediate', or 'advanced'"""
        pass

    @property
    def technologies(self) -> list:
        """List of technologies involved"""
        return ["kubernetes"]

    # Helper methods that K8s scenarios must implement
    @abstractmethod
    def get_resource_name(self) -> str:
        """Get the main Kubernetes resource name"""
        pass

    @abstractmethod
    def get_resource_type(self) -> str:
        """Get the Kubernetes resource type (pod, deployment, etc)"""
        pass

    @abstractmethod
    def get_manifest_path(self) -> Path:
        """Get path to the main Kubernetes manifest file"""
        pass

    # Default implementations that scenarios can use
    def apply_manifest(self) -> Dict[str, Any]:
        """Helper to apply a Kubernetes manifest"""
        try:
            manifest = self.get_manifest_path()
            result = subprocess.run(
                ["kubectl", "apply", "-f", str(manifest)],
                check=True,
                capture_output=True,
                text=True
            )
            return {
                "success": True,
                "output": result.stdout
            }
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "error": e.stderr
            }

    def delete_manifest(self) -> bool:
        """Helper to delete resources from a manifest"""
        try:
            manifest = self.get_manifest_path()
            subprocess.run(
                ["kubectl", "delete", "-f", str(manifest), "--ignore-not-found"],
                check=True
            )
            return True
        except subprocess.CalledProcessError:
            return False