# scenarios/process-zombie/__init__.py
"""
Process Zombie Scenario
A scenario where stuck processes are consuming system resources
"""

import os
import subprocess
import time
import signal
from pathlib import Path
from typing import Dict, Any, List, Optional
from clouddojo.base_scenario import BaseScenario
from clouddojo.scenario_metadata import ScenarioMetadata, StoryContext, Hint, CompanyType

class ProcessZombieMetadata(ScenarioMetadata):
    """Metadata for process-zombie scenario"""
    
    def get_story_context(self) -> StoryContext:
        return StoryContext(
            company_name="DataFlow Analytics",
            company_type=CompanyType.ENTERPRISE,
            your_role="System Administrator",
            situation="The production server is running slowly. Multiple stuck processes are consuming CPU and memory, affecting application performance.",
            urgency="high",
            stakeholders=["Development Team", "Operations Manager", "End Users"],
            business_impact="Application response time degraded. Customer complaints increasing.",
            success_criteria="System performance restored by eliminating stuck processes"
        )
    
    def get_hints(self) -> List[Hint]:
        return [
            Hint(1, "List Running Processes", 
                 "Check what processes are currently running on the system.",
                 "ps aux | grep sleep"),
            
            Hint(2, "Identify Problem Processes", 
                 "Look for the specific sleep processes that need to be terminated.",
                 "ps aux | grep 'sleep 3600'"),
            
            Hint(3, "Find Process IDs", 
                 "Get the process IDs (PIDs) of the problematic processes.",
                 "pgrep -f 'sleep 3600'"),
            
            Hint(4, "Kill the Processes", 
                 "Terminate the stuck processes using their PIDs.",
                 "kill -9 <PID>")
        ]
    
    def get_learning_path(self) -> str:
        return "production-sre"
    
    def get_completion_story(self, time_taken: int) -> str:
        time_str = f"{time_taken // 60}m {time_taken % 60}s" if time_taken > 0 else "record time"
        return f"System performance restored! The stuck processes are gone and applications are responding normally. The operations team is impressed with your process management skills. Resolution time: {time_str}"

class ProcessZombieScenario(BaseScenario):
    """Process management troubleshooting scenario"""
    
    def __init__(self, name: str):
        super().__init__(name)
        self.process_pids = []
        self._metadata = ProcessZombieMetadata()
    
    def get_metadata(self) -> Optional[ScenarioMetadata]:
        """Return embedded metadata"""
        return self._metadata
    
    @property
    def description(self) -> str:
        return "Stuck processes consuming system resources need to be identified and terminated"
    
    @property
    def difficulty(self) -> str:
        return "beginner"
    
    @property
    def technologies(self) -> list:
        return ["linux", "processes", "system-administration", "performance"]
    
    def start(self) -> Dict[str, Any]:
        """Start the process zombie scenario"""
        try:
            # Clean up any existing processes
            self._cleanup_processes()
            
            # Create simple long-running processes that can be easily identified
            for i in range(3):
                try:
                    # Create a simple sleep process
                    proc = subprocess.Popen(
                        ["sleep", "3600"],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                    self.process_pids.append(proc.pid)
                except Exception as e:
                    print(f"Warning: Could not create process {i}: {e}")
            
            # Save state
            self.save_state({
                'process_pids': self.process_pids,
                'started_at': time.time()
            })
            
            connection_info = f"""Stuck Processes: {len(self.process_pids)} processes running
Check processes: ps aux | grep sleep
Process PIDs: {', '.join(map(str, self.process_pids))}"""
            
            instructions = f"""🔧 TROUBLESHOOTING SCENARIO: Stuck Processes

📋 SITUATION:
Multiple stuck processes (sleep commands) are consuming system resources.

🎯 YOUR MISSION:
1. List all running processes:
   ps aux
2. Identify the problematic sleep processes:
   ps aux | grep sleep
3. Find the specific PIDs: {', '.join(map(str, self.process_pids))}
4. Terminate the stuck processes:
   kill -9 <PID>

💡 HINTS:
• Use 'ps aux' to see all processes
• Look for long-running 'sleep 3600' processes
• The PIDs you need to kill are: {', '.join(map(str, self.process_pids))}
• Use 'kill -9 PID' for each process

🏁 SUCCESS CRITERIA:
• All specified sleep processes are terminated
• PIDs {', '.join(map(str, self.process_pids))} no longer exist

💡 TIP: Use kill command to terminate the stuck processes
"""
            
            return {
                "success": True,
                "connection_info": connection_info,
                "instructions": instructions,
                "process_count": len(self.process_pids)
            }
            
        except Exception as e:
            return {"success": False, "error": f"Failed to start scenario: {str(e)}"}
    
    def stop(self) -> bool:
        """Stop and cleanup the scenario"""
        try:
            self._cleanup_processes()
            self.clear_state()
            return True
        except Exception:
            return False
    
    def _cleanup_processes(self):
        """Clean up all scenario processes"""
        try:
            # Kill processes by PID
            for pid in self.process_pids:
                try:
                    os.kill(pid, signal.SIGKILL)
                except (ProcessLookupError, PermissionError):
                    pass
                
            self.process_pids = []
        except Exception:
            pass
    
    def status(self) -> Dict[str, Any]:
        """Get current status of the scenario"""
        try:
            # Check how many processes are still running
            running_count = 0
            for pid in self.process_pids:
                try:
                    os.kill(pid, 0)  # Check if process exists
                    running_count += 1
                except (ProcessLookupError, PermissionError):
                    pass
            
            details = f"""Scenario Status: Active
Stuck Processes: {running_count} still running
Total Created: {len(self.process_pids)}
Check with: ps aux | grep sleep"""
            
            return {"running": running_count > 0, "details": details}
        except Exception as e:
            return {"running": False, "details": f"Error: {str(e)}"}
    
    def check(self) -> Dict[str, Any]:
        """Check if stuck processes have been eliminated"""
        try:
            checks = []
            all_passed = True
            
            # Check if our created processes are still running
            still_running = []
            for pid in self.process_pids:
                try:
                    os.kill(pid, 0)  # Check if process exists
                    still_running.append(pid)
                except (ProcessLookupError, PermissionError):
                    pass
            
            checks.append(("All stuck processes terminated", len(still_running) == 0))
            if len(still_running) > 0:
                all_passed = False
            
            if all_passed:
                feedback = "✅ All stuck processes eliminated! System performance restored."
            else:
                feedback = f"❌ {len(still_running)} processes still running. PIDs: {still_running}"
            
            return {
                "passed": all_passed,
                "checks": checks,
                "feedback": feedback,
                "remaining_pids": still_running
            }
            
        except Exception as e:
            return {
                "passed": False,
                "feedback": f"Error checking scenario: {str(e)}",
                "checks": [("Check failed", False)]
            }
    
    def reset(self) -> bool:
        """Reset the scenario"""
        return self.stop() and self.start().get('success', False)

# Export the scenario class
scenario_class = ProcessZombieScenario