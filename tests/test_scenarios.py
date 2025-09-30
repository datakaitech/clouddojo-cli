#!/usr/bin/env python3
"""
CloudDojo Scenario Testing Framework
Tests all scenarios for proper implementation and integration
"""

import sys
import os
import importlib.util
import inspect
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add clouddojo to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from clouddojo.base_scenario import BaseScenario
from clouddojo.scenario_metadata import ScenarioMetadata, StoryContext, Hint
from clouddojo.metadata_registry import registry
from clouddojo.learning_path_definitions import LEARNING_PATH_CLASSES

try:
    from clouddojo.k8s_base_scenario import K8sBaseScenario
except ImportError:
    K8sBaseScenario = None

class ScenarioTester:
    """Test framework for CloudDojo scenarios"""
    
    def __init__(self):
        self.scenarios_dir = Path(__file__).parent.parent / 'clouddojo' / 'scenarios'
        self.errors = []
        self.warnings = []
        
        # Register learning paths
        for path_class in LEARNING_PATH_CLASSES:
            registry.register_learning_path(path_class())
    
    def run_all_tests(self) -> bool:
        """Run all scenario tests"""
        print("CloudDojo Scenario Testing Framework")
        print("=" * 50)
        
        scenarios = self._discover_scenarios()
        if not scenarios:
            self._error("No scenarios found!")
            return False
        
        print(f"Found {len(scenarios)} scenarios to test")
        print()
        
        all_passed = True
        for scenario_name, scenario_class in scenarios.items():
            print(f"Testing: {scenario_name}")
            if not self._test_scenario(scenario_name, scenario_class):
                all_passed = False
            print()
        
        self._print_summary()
        return all_passed and len(self.errors) == 0
    
    def _discover_scenarios(self) -> Dict[str, type]:
        """Discover all scenario classes"""
        scenarios = {}
        
        if not self.scenarios_dir.exists():
            self._error(f"Scenarios directory not found: {self.scenarios_dir}")
            return scenarios
        
        for scenario_dir in self.scenarios_dir.iterdir():
            if not scenario_dir.is_dir() or scenario_dir.name.startswith('.'):
                continue
                
            init_file = scenario_dir / '__init__.py'
            if not init_file.exists():
                self._warning(f"Scenario {scenario_dir.name} missing __init__.py")
                continue
            
            try:
                spec = importlib.util.spec_from_file_location(
                    f"scenarios.{scenario_dir.name}",
                    init_file
                )
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                if hasattr(module, 'scenario_class'):
                    scenarios[scenario_dir.name] = module.scenario_class
                else:
                    self._error(f"Scenario {scenario_dir.name} missing 'scenario_class' export")
                    
            except Exception as e:
                self._error(f"Failed to load scenario {scenario_dir.name}: {e}")
        
        return scenarios
    
    def _test_scenario(self, name: str, scenario_class: type) -> bool:
        """Test a single scenario"""
        passed = True
        
        # Test 1: Class inheritance
        if not self._test_inheritance(name, scenario_class):
            passed = False
        
        # Test 2: Required methods
        if not self._test_required_methods(name, scenario_class):
            passed = False
        
        # Test 3: Properties
        if not self._test_properties(name, scenario_class):
            passed = False
        
        # Test 4: Metadata implementation
        if not self._test_metadata(name, scenario_class):
            passed = False
        
        # Test 5: Learning path assignment
        if not self._test_learning_path(name, scenario_class):
            passed = False
        
        # Test 6: Instantiation
        if not self._test_instantiation(name, scenario_class):
            passed = False
        
        status = "PASS" if passed else "FAIL"
        print(f"  {status}")
        
        return passed
    
    def _test_inheritance(self, name: str, scenario_class: type) -> bool:
        """Test proper inheritance from BaseScenario or K8sBaseScenario"""
        valid_bases = [BaseScenario]
        if K8sBaseScenario:
            valid_bases.append(K8sBaseScenario)
        
        if not any(issubclass(scenario_class, base) for base in valid_bases):
            self._error(f"{name}: Must inherit from BaseScenario or K8sBaseScenario")
            return False
        return True
    
    def _test_required_methods(self, name: str, scenario_class: type) -> bool:
        """Test all required abstract methods are implemented"""
        required_methods = ['start', 'stop', 'status', 'check', 'reset']
        passed = True
        
        # Check if it's a K8s scenario
        is_k8s = K8sBaseScenario and issubclass(scenario_class, K8sBaseScenario)
        if is_k8s:
            required_methods.extend(['get_manifest_path', 'get_resource_name', 'get_resource_type'])
        
        for method_name in required_methods:
            if not hasattr(scenario_class, method_name):
                self._error(f"{name}: Missing required method '{method_name}'")
                passed = False
        
        return passed
    
    def _test_properties(self, name: str, scenario_class: type) -> bool:
        """Test required properties are implemented"""
        required_props = ['description', 'difficulty', 'technologies']
        passed = True
        
        try:
            instance = scenario_class(name)
            
            for prop_name in required_props:
                if not hasattr(instance, prop_name):
                    self._error(f"{name}: Missing required property '{prop_name}'")
                    passed = False
                else:
                    value = getattr(instance, prop_name)
                    if prop_name == 'difficulty' and value not in ['beginner', 'intermediate', 'advanced']:
                        self._error(f"{name}: Invalid difficulty '{value}'. Must be: beginner, intermediate, or advanced")
                        passed = False
                    elif prop_name == 'technologies' and not isinstance(value, list):
                        self._error(f"{name}: Property 'technologies' must be a list")
                        passed = False
                        
        except Exception as e:
            self._error(f"{name}: Error testing properties: {e}")
            passed = False
        
        return passed
    
    def _test_metadata(self, name: str, scenario_class: type) -> bool:
        """Test metadata implementation"""
        passed = True
        
        try:
            instance = scenario_class(name)
            metadata = instance.get_metadata()
            
            if metadata is None:
                self._warning(f"{name}: No metadata implemented (optional but recommended)")
                return True
            
            if not isinstance(metadata, ScenarioMetadata):
                self._error(f"{name}: Metadata must inherit from ScenarioMetadata")
                return False
            
            # Test metadata methods
            try:
                story = metadata.get_story_context()
                if story and not isinstance(story, StoryContext):
                    self._error(f"{name}: get_story_context() must return StoryContext or None")
                    passed = False
            except Exception as e:
                self._error(f"{name}: Error in get_story_context(): {e}")
                passed = False
            
            try:
                hints = metadata.get_hints()
                if not isinstance(hints, list):
                    self._error(f"{name}: get_hints() must return a list")
                    passed = False
                elif hints and not all(isinstance(h, Hint) for h in hints):
                    self._error(f"{name}: All hints must be Hint objects")
                    passed = False
            except Exception as e:
                self._error(f"{name}: Error in get_hints(): {e}")
                passed = False
            
            try:
                completion = metadata.get_completion_story(60)
                if not isinstance(completion, str):
                    self._error(f"{name}: get_completion_story() must return a string")
                    passed = False
            except Exception as e:
                self._error(f"{name}: Error in get_completion_story(): {e}")
                passed = False
                
        except Exception as e:
            self._error(f"{name}: Error testing metadata: {e}")
            passed = False
        
        return passed
    
    def _test_learning_path(self, name: str, scenario_class: type) -> bool:
        """Test learning path assignment"""
        passed = True
        
        try:
            instance = scenario_class(name)
            metadata = instance.get_metadata()
            
            if metadata is None:
                self._warning(f"{name}: No learning path assignment (metadata not implemented)")
                return True
            
            learning_path = metadata.get_learning_path()
            if not learning_path:
                self._warning(f"{name}: No learning path assigned")
                return True
            
            # Check if learning path exists
            available_paths = list(registry.get_learning_paths().keys())
            if learning_path not in available_paths:
                self._error(f"{name}: Invalid learning path '{learning_path}'. Available: {available_paths}")
                passed = False
            
        except Exception as e:
            self._error(f"{name}: Error testing learning path: {e}")
            passed = False
        
        return passed
    
    def _test_instantiation(self, name: str, scenario_class: type) -> bool:
        """Test scenario can be instantiated"""
        try:
            instance = scenario_class(name)
            
            # Test basic method calls don't crash
            instance.description
            instance.difficulty
            instance.technologies
            
            return True
        except Exception as e:
            self._error(f"{name}: Cannot instantiate scenario: {e}")
            return False
    
    def _error(self, message: str):
        """Record an error"""
        self.errors.append(message)
        print(f"    ERROR: {message}")
    
    def _warning(self, message: str):
        """Record a warning"""
        self.warnings.append(message)
        print(f"    WARNING: {message}")
    
    def _print_summary(self):
        """Print test summary"""
        print("=" * 50)
        print("TEST SUMMARY")
        print("=" * 50)
        
        if self.errors:
            print(f"ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"  - {error}")
            print()
        
        if self.warnings:
            print(f"WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  - {warning}")
            print()
        
        if not self.errors and not self.warnings:
            print("All tests passed! No issues found.")
        elif not self.errors:
            print("All critical tests passed! Only warnings found.")
        else:
            print("Tests failed! Please fix the errors above.")

def main():
    """Run scenario tests"""
    tester = ScenarioTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()