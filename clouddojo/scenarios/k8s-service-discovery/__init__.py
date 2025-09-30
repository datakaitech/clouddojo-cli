from pathlib import Path
from typing import Dict, Any, List, Optional
import subprocess
import time
from clouddojo.k8s_base_scenario import K8sBaseScenario
from clouddojo.scenario_metadata import ScenarioMetadata, StoryContext, Hint, CompanyType

class K8sServiceDiscoveryMetadata(ScenarioMetadata):
    """Metadata for k8s-service-discovery scenario"""
    
    def get_story_context(self) -> StoryContext:
        return StoryContext(
            company_name="CloudCommerce Ltd",
            company_type=CompanyType.ECOMMERCE,
            your_role="DevOps Engineer", 
            situation="The shopping cart service can't find the payment API. Orders are stuck in 'processing' state.",
            urgency="high",
            stakeholders=["Product Team", "Customer Support", "Engineering Lead"],
            business_impact="Orders not completing. Customer complaints rising.",
            success_criteria="Shopping cart successfully connects to payment service"
        )
    
    def get_hints(self) -> List[Hint]:
        return [
            Hint(1, "Check Service Status", 
                 "Verify the payment service exists and is properly configured.",
                 "kubectl get svc payment-api"),
            
            Hint(2, "Check Service Endpoints", 
                 "See if the service has any backend pods to route traffic to.",
                 "kubectl get endpoints payment-api"),
            
            Hint(3, "Investigate Pod Labels", 
                 "Check if the payment pods have the correct labels for service selection.",
                 "kubectl get pods --show-labels | grep payment"),
            
            Hint(4, "Fix Service Selector", 
                 "The service selector doesn't match the pod labels. Fix the service.",
                 "kubectl patch svc payment-api -p '{\"spec\":{\"selector\":{\"app\":\"payment-service\"}}}'")
        ]
    
    def get_learning_path(self) -> str:
        return "k8s-essentials"
    
    def get_completion_story(self, time_taken: int) -> str:
        time_str = f"{time_taken // 60}m {time_taken % 60}s" if time_taken > 0 else "record time"
        return f"Orders are processing again! The payment service is discoverable and customers can complete purchases. Great service debugging skills! Resolution time: {time_str}"

class K8sServiceDiscovery(K8sBaseScenario):
    """Service discovery failure due to selector mismatch"""

    def __init__(self, name: str):
        super().__init__(name)
        self._description = "Service selector doesn't match pod labels, causing service discovery failure"
        self._difficulty = "intermediate"
        self._metadata = K8sServiceDiscoveryMetadata()
    
    def get_metadata(self) -> Optional[ScenarioMetadata]:
        return self._metadata

    def start(self) -> Dict[str, Any]:
        try:
            result = self.apply_manifest()
            if result["success"]:
                time.sleep(10)
                
                instructions = f"""🔧 TROUBLESHOOTING SCENARIO: Service Discovery Failure

📋 SITUATION:
Shopping cart can't connect to payment API. Service discovery is broken.

🎯 YOUR MISSION:
1. Check service status: kubectl get svc payment-api
2. Check service endpoints: kubectl get endpoints payment-api  
3. Investigate pod labels: kubectl get pods --show-labels
4. Fix service selector to match pod labels

💡 DEBUGGING COMMANDS:
• kubectl describe svc payment-api
• kubectl get pods -l app=payment-service
• kubectl exec cart-app -- nslookup payment-api

🏁 SUCCESS CRITERIA:
• Service has endpoints pointing to payment pods
• Cart can successfully reach payment API
• Service discovery works correctly

💡 TIP: Fix the service configuration to enable proper discovery"""
                
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
            # Check if service has endpoints
            endpoints_result = subprocess.run(
                ["kubectl", "get", "endpoints", "payment-api", "-o", "jsonpath={.subsets[*].addresses[*].ip}"],
                capture_output=True, text=True
            )
            
            has_endpoints = len(endpoints_result.stdout.strip()) > 0
            
            if has_endpoints:
                # Test connectivity
                connectivity_result = subprocess.run(
                    ["kubectl", "exec", "cart-app", "--", "curl", "-s", "-m", "5",
                     "-o", "/dev/null", "-w", "%{http_code}", "payment-api:8080/health"],
                    capture_output=True, text=True
                )
                
                if connectivity_result.returncode == 0 and "200" in connectivity_result.stdout:
                    return {
                        "passed": True,
                        "feedback": "✅ Service discovery working!\n✅ Cart can reach payment API!\n🎉 Orders can process successfully!"
                    }
                else:
                    return {
                        "passed": False,
                        "feedback": "✅ Service has endpoints but connectivity failed",
                        "hints": "Check if payment service is responding on port 8080"
                    }
            else:
                return {
                    "passed": False,
                    "feedback": "❌ Service has no endpoints - selector mismatch",
                    "hints": """💡 Fix the service selector:
kubectl describe svc payment-api
kubectl get pods --show-labels | grep payment
kubectl patch svc payment-api -p '{"spec":{"selector":{"app":"payment-service"}}}'"""
                }
                
        except Exception as e:
            return {"passed": False, "feedback": f"❌ Error: {str(e)}"}

    def stop(self) -> bool:
        return self.delete_manifest()

    def status(self) -> Dict[str, Any]:
        try:
            result = subprocess.run(
                ["kubectl", "get", "pods,svc", "-l", "scenario=service-discovery"],
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
        return "service-discovery"

    def get_resource_type(self) -> str:
        return "service"

    def get_manifest_path(self) -> Path:
        return self.manifests_dir / "service-discovery.yaml"

scenario_class = K8sServiceDiscovery