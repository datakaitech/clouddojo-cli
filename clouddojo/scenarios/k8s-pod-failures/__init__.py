from pathlib import Path
from typing import Dict, Any, List, Optional
import subprocess
from clouddojo.k8s_base_scenario import K8sBaseScenario
from clouddojo.scenario_metadata import ScenarioMetadata, StoryContext, Hint, CompanyType

class K8sPodFailuresMetadata(ScenarioMetadata):
    """Metadata for k8s-pod-failures scenario"""
    
    def get_story_context(self) -> StoryContext:
        return StoryContext(
            company_name="FinSecure Bank",
            company_type=CompanyType.FINTECH,
            your_role="Platform Engineer", 
            situation="Critical payment processing pods are failing to start in production. Transactions are being queued but not processed.",
            urgency="critical",
            stakeholders=["Head of Engineering", "Compliance Team", "Operations Director"],
            business_impact="Regulatory compliance at risk. Customer funds frozen.",
            success_criteria="Payment processing restored within SLA"
        )
    
    def get_hints(self) -> List[Hint]:
        return [
            Hint(1, "Check Pod Status", 
                 "The pod is stuck in a crash loop. Check its current status and recent events.",
                 "kubectl get pod crashloop-init-demo"),
            
            Hint(2, "Examine Events", 
                 "Look at the pod events to understand why it's failing to start.",
                 "kubectl describe pod crashloop-init-demo"),
            
            Hint(3, "InitContainer Issue", 
                 "The problem is with the initContainer. Check the image name in the pod specification.",
                 "kubectl get pod crashloop-init-demo -o yaml | grep -A 10 initContainers"),
            
            Hint(4, "Fix the Image", 
                 "The initContainer is using a non-existent image. Edit the pod to use a valid image like 'busybox:latest'.",
                 "kubectl edit pod crashloop-init-demo")
        ]
    
    def get_learning_path(self) -> str:
        return "k8s-essentials"
    
    def get_completion_story(self, time_taken: int) -> str:
        time_str = f"{time_taken // 60}m {time_taken % 60}s" if time_taken > 0 else "record time"
        return f"Payment processing restored! All queued transactions processed successfully. The compliance team is relieved and your manager is considering you for a promotion. Fixed in: {time_str}"

class K8sPodFailures(K8sBaseScenario):
    """Kubernetes pod with a broken initContainer"""

    def __init__(self, name: str):
        super().__init__(name)
        self._description = "A pod stuck in CrashLoopBackOff due to invalid initContainer image"
        self._difficulty = "intermediate"
        self._metadata = K8sPodFailuresMetadata()
    
    def get_metadata(self) -> Optional[ScenarioMetadata]:
        """Return embedded metadata"""
        return self._metadata

    def start(self) -> Dict[str, Any]:
        """Start the scenario"""
        try:
            # Verify kubectl is accessible
            try:
                subprocess.run(["kubectl", "version", "--client"], capture_output=True, check=True)
            except Exception as e:
                return {
                    "success": False,
                    "error": f"kubectl not accessible: {e}. Please ensure kubectl is installed and configured."
                }
            
            result = self.apply_manifest()
            if result["success"]:
                connection_info = f"""Pod: crashloop-init-demo
Namespace: default
Monitor: kubectl get pod crashloop-init-demo -w
Resource ID: {self.get_resource_name()}"""
                
                instructions = f"""🔧 TROUBLESHOOTING SCENARIO: Pod Startup Failures

📋 SITUATION:
Critical payment processing pods are failing to start due to initContainer issues.

🎯 YOUR MISSION:
1. Check the pod status:
   kubectl get pod crashloop-init-demo
2. Investigate why it's failing:
   kubectl describe pod crashloop-init-demo
3. Fix the initContainer configuration
4. Verify the pod reaches Running state

💡 HINTS:
• Look for CrashLoopBackOff or Init:Error status
• Check initContainer events and logs
• Verify the initContainer image exists

🏁 SUCCESS CRITERIA:
• Pod is in Running state
• All containers are ready
• No crash loops or init failures

💡 TIP: Fix the initContainer image name to resolve the issue
"""
                
                return {
                    "success": True,
                    "connection_info": connection_info,
                    "instructions": instructions,
                    "namespace": "default",
                    "pod_name": "crashloop-init-demo"
                }
            return {
                "success": False,
                "error": result["error"]
            }
        except Exception as e:
            return {"success": False, "error": f"Failed to start scenario: {str(e)}"}

    def stop(self) -> bool:
        return self.delete_manifest()

    def status(self) -> Dict[str, Any]:
        """Get current scenario status"""
        try:
            result = subprocess.run(
                ["kubectl", "get", "pod", self.get_resource_name(), "-o", "wide"],
                capture_output=True,
                text=True
            )
            
            details = f"""Pod Status: {result.stdout if result.returncode == 0 else 'Not found'}
Namespace: default
Resource: {self.get_resource_name()}"""
            
            return {"running": result.returncode == 0, "details": details}
        except Exception as e:
            return {"running": False, "details": f"Error: {str(e)}"}

    def check(self) -> Dict[str, Any]:
        result = subprocess.run(
            ["kubectl", "get", "pod", self.get_resource_name(), "-o", "jsonpath={.status.phase}"],
            capture_output=True,
            text=True
        )
        
        if "Running" in result.stdout:
            return {
                "passed": True,
                "feedback": "✅ Pod is running successfully!"
            }
        return {
            "passed": False,
            "feedback": f"❌ Pod not running. Current phase: {result.stdout}",
            "hints": "Check the initContainer image name. Is it valid?"
        }

    def reset(self) -> bool:
        return self.stop() and bool(self.start()["success"])

    @property
    def description(self) -> str:
        return self._description

    @property
    def difficulty(self) -> str:
        return self._difficulty

    def get_resource_name(self) -> str:
        return "crashloop-init-demo"

    def get_resource_type(self) -> str:
        return "pod"

    def get_manifest_path(self) -> Path:
        return self.manifests_dir / "pod.yaml"

# Expose for scenario loader
scenario_class = K8sPodFailures