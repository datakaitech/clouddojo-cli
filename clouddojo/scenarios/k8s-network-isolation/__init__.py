from pathlib import Path
from typing import Dict, Any, List, Optional
import subprocess
import time
from clouddojo.k8s_base_scenario import K8sBaseScenario
from clouddojo.scenario_metadata import ScenarioMetadata, StoryContext, Hint, CompanyType

class K8sNetworkIsolationMetadata(ScenarioMetadata):
    """Metadata for k8s-network-isolation scenario"""
    
    def get_story_context(self) -> StoryContext:
        return StoryContext(
            company_name="SecureBank Corp",
            company_type=CompanyType.FINTECH,
            your_role="Platform Engineer",
            situation="After implementing network security policies, the frontend can't communicate with the backend API. Customer transactions are failing.",
            urgency="critical",
            stakeholders=["Security Team", "Engineering Manager", "Compliance Officer"],
            business_impact="All transactions blocked. Regulatory compliance at risk.",
            success_criteria="Restore frontend-backend communication while maintaining security"
        )
    
    def get_hints(self) -> List[Hint]:
        return [
            Hint(1, "Check Pod Status", 
                 "Verify both frontend and backend pods are running and ready.",
                 "kubectl get pods -l tier=frontend,backend"),
            
            Hint(2, "Test Direct Connectivity", 
                 "Try to reach the backend from frontend pod using curl.",
                 "kubectl exec frontend-app -- curl -m 5 backend-service:8080/api/health"),
            
            Hint(3, "Check Network Policies", 
                 "Network policies might be blocking communication. Check what policies exist.",
                 "kubectl get networkpolicy"),
            
            Hint(4, "Fix Network Policy", 
                 "The network policy is too restrictive. Allow frontend to communicate with backend.",
                 "kubectl label pod frontend-app role=frontend")
        ]
    
    def get_learning_path(self) -> str:
        return "k8s-essentials"
    
    def get_completion_story(self, time_taken: int) -> str:
        time_str = f"{time_taken // 60}m {time_taken % 60}s" if time_taken > 0 else "record time"
        return f"Transactions are flowing again! Network security is maintained while allowing necessary communication. The security team approves of your solution. Resolution time: {time_str}"

class K8sNetworkIsolation(K8sBaseScenario):
    """Pod-to-pod communication blocked by network policies"""

    def __init__(self, name: str):
        super().__init__(name)
        self._description = "Frontend pod cannot reach backend due to restrictive network policies"
        self._difficulty = "intermediate"
        self._metadata = K8sNetworkIsolationMetadata()
    
    def get_metadata(self) -> Optional[ScenarioMetadata]:
        return self._metadata

    def start(self) -> Dict[str, Any]:
        try:
            result = self.apply_manifest()
            if result["success"]:
                time.sleep(15)  # Wait for pods and policies
                
                instructions = f"""🔧 TROUBLESHOOTING SCENARIO: Network Policy Isolation

📋 SITUATION:
Network policies were implemented for security, but now frontend can't reach backend API.

🎯 YOUR MISSION:
1. Check pod status: kubectl get pods
2. Test connectivity: kubectl exec frontend-app -- curl backend-service:8080/api/health
3. Investigate network policies: kubectl get networkpolicy
4. Fix communication by adding proper labels to frontend pod

💡 DEBUGGING COMMANDS:
• kubectl describe networkpolicy backend-netpol
• kubectl get pods --show-labels
• kubectl exec frontend-app -- nslookup backend-service

🏁 SUCCESS CRITERIA:
• Frontend can successfully reach backend API
• Network policy allows communication
• Security restrictions remain in place

💡 TIP: Fix the Kubernetes resources to complete the challenge"""
                
                return {
                    "success": True,
                    "instructions": instructions,
                    "namespace": "default"
                }
            return {"success": False, "error": result["error"]}
        except Exception as e:
            return {"success": False, "error": f"Failed to start: {str(e)}"}

    def check(self) -> Dict[str, Any]:
        try:
            # Test connectivity from frontend to backend
            connectivity_result = subprocess.run(
                ["kubectl", "exec", "frontend-app", "--", "curl", "-s", "-m", "5", 
                 "-o", "/dev/null", "-w", "%{http_code}", "backend-service:8080/api/health"],
                capture_output=True, text=True
            )
            
            if connectivity_result.returncode == 0 and "200" in connectivity_result.stdout:
                return {
                    "passed": True,
                    "feedback": "✅ Frontend successfully communicates with backend!\n🎉 Network policy configured correctly!"
                }
            else:
                return {
                    "passed": False,
                    "feedback": "❌ Frontend cannot reach backend API",
                    "hints": """💡 Check if frontend pod has the correct label:
kubectl get pods --show-labels
kubectl describe networkpolicy backend-netpol
kubectl label pod frontend-app role=frontend"""
                }
                
        except Exception as e:
            return {"passed": False, "feedback": f"❌ Error: {str(e)}"}

    def stop(self) -> bool:
        return self.delete_manifest()

    def status(self) -> Dict[str, Any]:
        try:
            result = subprocess.run(
                ["kubectl", "get", "pods", "-l", "app in (frontend,backend)"],
                capture_output=True, text=True
            )
            return {"running": result.returncode == 0, "details": result.stdout}
        except Exception as e:
            return {"running": False, "details": f"Error: {str(e)}"}

    def reset(self) -> bool:
        return self.stop() and bool(self.start()["success"])

    @property
    def description(self) -> str:
        return self._description

    @property
    def difficulty(self) -> str:
        return self._difficulty

    def get_resource_name(self) -> str:
        return "network-isolation"

    def get_resource_type(self) -> str:
        return "pods"

    def get_manifest_path(self) -> Path:
        return self.manifests_dir / "network-isolation.yaml"

scenario_class = K8sNetworkIsolation