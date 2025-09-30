#!/usr/bin/env python3
"""
CloudDojo Scenario Template
Copy this template to create new scenarios: cp scenario_template.py clouddojo/scenarios/my-scenario/__init__.py
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
from clouddojo.base_scenario import BaseScenario
# For Kubernetes scenarios, use: from clouddojo.k8s_base_scenario import K8sBaseScenario
from clouddojo.scenario_metadata import ScenarioMetadata, StoryContext, Hint, CompanyType

class MyScenarioMetadata(ScenarioMetadata):
    """Metadata for my-scenario"""
    
    def get_story_context(self) -> StoryContext:
        return StoryContext(
            company_name="TechCorp Inc",
            company_type=CompanyType.STARTUP,
            your_role="DevOps Engineer",
            situation="The production service is down after a deployment. Users can't access the application.",
            urgency="critical",
            stakeholders=["Engineering Team", "Product Manager", "CEO"],
            business_impact="Revenue loss. Customer complaints increasing.",
            success_criteria="Service restored and accessible to users"
        )
    
    def get_hints(self) -> List[Hint]:
        return [
            Hint(1, "Check Service Status", 
                 "First, verify if the service is running and what its current state is.",
                 "systemctl status myservice"),
            
            Hint(2, "Examine Logs", 
                 "Look at the service logs to understand what went wrong during startup.",
                 "journalctl -u myservice -f"),
            
            Hint(3, "Check Configuration", 
                 "The configuration file might have syntax errors from the recent deployment.",
                 "cat /etc/myservice/config.yml"),
            
            Hint(4, "Fix and Restart", 
                 "Fix the configuration issue and restart the service.",
                 "systemctl restart myservice")
        ]
    
    def get_learning_path(self) -> str:
        # Choose from: "docker-basics", "k8s-essentials", "production-sre"
        return "docker-basics"
    
    def get_completion_story(self, time_taken: int) -> str:
        time_str = f"{time_taken // 60}m {time_taken % 60}s" if time_taken > 0 else "record time"
        return f"Service restored! Users can access the application again. The CEO is impressed with your quick response. Resolution time: {time_str}"

class MyScenario(BaseScenario):
    """Template scenario - replace with your scenario description"""
    # For Kubernetes scenarios, inherit from K8sBaseScenario instead:
    # class MyScenario(K8sBaseScenario):

    def __init__(self, name: str):
        super().__init__(name)
        self._metadata = MyScenarioMetadata()
    
    def get_metadata(self) -> Optional[ScenarioMetadata]:
        return self._metadata

    @property
    def description(self) -> str:
        return "Brief description of what's broken in this scenario"

    @property
    def difficulty(self) -> str:
        # Must be: "beginner", "intermediate", or "advanced"
        return "beginner"

    @property
    def technologies(self) -> list:
        # List technologies involved
        return ["docker", "nginx", "linux"]

    def start(self) -> Dict[str, Any]:
        """Start the scenario - set up the broken environment"""
        try:
            # TODO: Implement scenario setup
            # Examples:
            # - Start Docker containers with broken configs
            # - Create files with wrong permissions
            # - Deploy broken Kubernetes manifests
            
            connection_info = """Container: my-broken-service
Access: docker exec -it my-broken-service bash
Port: http://localhost:8080"""
            
            instructions = """🔧 TROUBLESHOOTING SCENARIO: My Broken Service

📋 SITUATION:
The service is down after deployment. Users can't access it.

🎯 YOUR MISSION:
1. Check service status
2. Examine error logs  
3. Fix configuration issues
4. Verify service is accessible

💡 TIP: Start by checking if the service is running"""
            
            return {
                "success": True,
                "connection_info": connection_info,
                "instructions": instructions
            }
            
        except Exception as e:
            return {"success": False, "error": f"Failed to start: {str(e)}"}

    def stop(self) -> bool:
        """Stop and cleanup the scenario"""
        try:
            # TODO: Implement cleanup
            # Examples:
            # - Stop and remove Docker containers
            # - Delete temporary files
            # - Remove Kubernetes resources
            return True
        except Exception:
            return False

    def status(self) -> Dict[str, Any]:
        """Get current scenario status"""
        try:
            # TODO: Check if scenario is running
            # Examples:
            # - Check if Docker container exists
            # - Verify Kubernetes pods are running
            # - Check if files exist
            
            details = "Scenario Status: Active\nService: Running\nPort: 8080"
            return {"running": True, "details": details}
        except Exception as e:
            return {"running": False, "details": f"Error: {str(e)}"}

    def check(self) -> Dict[str, Any]:
        """Check if the scenario has been solved"""
        try:
            # TODO: Implement solution validation
            # Examples:
            # - Test HTTP endpoints return 200
            # - Verify files have correct permissions
            # - Check Kubernetes pods are healthy
            
            # Example checks:
            checks = [
                ("Service is running", True),
                ("Configuration is valid", True), 
                ("Service responds on port 8080", True)
            ]
            
            all_passed = all(passed for _, passed in checks)
            
            feedback_lines = []
            for check_name, passed in checks:
                status = "✅ PASS" if passed else "❌ FAIL"
                feedback_lines.append(f"{status} {check_name}")
            
            if all_passed:
                return {
                    "passed": True,
                    "feedback": "\n".join(feedback_lines) + "\n\n🎉 Scenario completed successfully!"
                }
            else:
                return {
                    "passed": False,
                    "feedback": "\n".join(feedback_lines),
                    "hints": "Check the service logs and configuration files"
                }
                
        except Exception as e:
            return {"passed": False, "feedback": f"❌ Error: {str(e)}"}

    def reset(self) -> bool:
        """Reset scenario to broken state"""
        try:
            # TODO: Reset to broken state
            # Usually: stop() then start()
            return self.stop() and self.start().get("success", False)
        except Exception:
            return False

# REQUIRED: Export the scenario class
scenario_class = MyScenario