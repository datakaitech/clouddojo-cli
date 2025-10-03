#!/usr/bin/env python3
"""
No Space Left Scenario - Inode Exhaustion Troubleshooting
"""

import docker
from pathlib import Path
from typing import Dict, Any, List, Optional
from clouddojo.base_scenario import BaseScenario
from clouddojo.scenario_metadata import ScenarioMetadata, StoryContext, Hint, CompanyType

class NoSpaceLeftMetadata(ScenarioMetadata):
    """Metadata for no-space-left scenario"""
    
    def get_story_context(self) -> StoryContext:
        return StoryContext(
            company_name="DataKai INC",
            company_type=CompanyType.STARTUP,
            your_role="Site Reliability Engineer",
            situation="Black Friday sale is ongoing. Suddenly you see no logs on Grafana dashboard. The monitoring service can't create new log files in /mnt/small_fs/ despite having disk space available. The error says 'No space left on device' but df -h shows space available.",
            urgency="very-critical",
            stakeholders=["Engineering Team", "SRE Team", "Business Operations"],
            business_impact="No monitoring data during peak sales period. Revenue at risk.",
            success_criteria="Monitoring service can create files in /mnt/small_fs/"
        )
    
    def get_hints(self) -> List[Hint]:
        return [
            Hint(1, "Check All Filesystems", 
                 "Check disk space on all mounted filesystems.",
                 "df -h"),
            
            Hint(2, "Focus on the Problem Filesystem", 
                 "Look at /mnt/small_fs - notice the high inode usage. full space usage always dont means df -h ",
                 "df -i /mnt/small_fs"),
            
            Hint(3, "Find the Culprit Directory", 
                 "Look for directories with many small files in the problematic filesystem.",
                 "ls -la /mnt/small_fs/ && find /mnt/small_fs/logs -type f | wc -l"),
            
            Hint(4, "Clean Up Files", 
                 "Remove the excessive log files to free up inodes.",
                 "rm -rf /mnt/small_fs/logs/*")
        ]
    
    def get_learning_path(self) -> str:
        # This scenrio is running in docker but falls under production-sre, could be implemented without 
        # docker but need to play with the host machine so choose docker 
        return "production-sre"
    
    def get_completion_story(self, time_taken: int) -> str:
        time_str = f"{time_taken // 60}m {time_taken % 60}s" if time_taken > 0 else "record time"
        return f"Excellent work! You've successfully resolved the inode exhaustion issue on /mnt/small_fs/. The monitoring service can now create log files again and Black Friday metrics are flowing. You learned that 'No space left on device' can mean inode exhaustion, not just disk space! Resolution time: {time_str}"

class NoSpaceLeft(BaseScenario):
    """No space left on device - inode exhaustion scenario"""

    def __init__(self, name: str):
        super().__init__(name)
        self._metadata = NoSpaceLeftMetadata()
        self.docker_client = docker.from_env()
        self.container_name = f"clouddojo-{name}"
    
    def get_metadata(self) -> Optional[ScenarioMetadata]:
        return self._metadata

    @property
    def description(self) -> str:
        return "Troubleshoot inode exhaustion causing 'No space left on device' errors despite available disk space"

    @property
    def difficulty(self) -> str:
        return "intermediate"

    @property
    def technologies(self) -> list:
        return ["docker", "linux"]

    def start(self) -> Dict[str, Any]:
        """Start the scenario - set up the broken environment"""
        try:
            self.stop()
            
            # Build image from scenario directory
            image_name = "clouddojo-no-space-left"
            if not self._image_exists(image_name):
                scenario_dir = Path(__file__).parent
                self.docker_client.images.build(
                    path=str(scenario_dir),
                    tag=image_name,
                    rm=True,
                    forcerm=True
                )
            
            # Run container with privileged mode for mounting
            container = self.docker_client.containers.run(
                image_name,
                name=self.container_name,
                detach=True,
                tty=True,
                privileged=True
            )
            
            # Execute the inode filling script with privileged mode for mounting
            container.exec_run("/usr/local/bin/fill_inodes.sh", privileged=True)
            
            connection_info = f"""Container: {self.container_name}
Access: docker exec -it {self.container_name} bash"""
            
            instructions = """🔧 TROUBLESHOOTING SCENARIO: No Space Left on Device

📋 SITUATION:
The monitoring service can't create new log files in /mnt/small_fs/. You're getting "No space left on device" errors,
but when you check disk space with 'df -h', there seems to be plenty available. This is confusing!

🎯 YOUR MISSION:
1. Check disk space usage on ALL filesystems
2. Try creating a file: touch /mnt/small_fs/test.txt
3. Investigate why files can't be created 
4. Find and clean up the problematic files
5. Verify you can create files again

🔍 TEST THE PROBLEM: touch /mnt/small_fs/newfile.txt"""
            
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
            # Stop and remove container
            try:
                container = self.docker_client.containers.get(self.container_name)
                container.stop()
                container.remove()
            except docker.errors.NotFound:
                pass
            
            # No temporary files to clean up
            
            return True
        except Exception:
            return False

    def status(self) -> Dict[str, Any]:
        """Get current scenario status"""
        try:
            container = self.docker_client.containers.get(self.container_name)
            if container.status == "running":
                # Check inode usage
                result = container.exec_run("df -i")
                details = f"Container Status: Running\nInode Status:\n{result.output.decode()}"
                return {"running": True, "details": details}
            else:
                return {"running": False, "details": "Container not running"}
        except docker.errors.NotFound:
            return {"running": False, "details": "Container not found"}
        except Exception as e:
            return {"running": False, "details": f"Error: {str(e)}"}

    def check(self) -> Dict[str, Any]:
        """Check if the scenario has been solved"""
        try:
            container = self.docker_client.containers.get(self.container_name)
            
            # Check if container is running
            container_running = container.status == "running"
            
            # Check if we can create files (inodes available)
            can_create_files = False
            inode_usage_ok = False
            
            if container_running:
                # Try to create a test file on the small filesystem
                result = container.exec_run("touch /mnt/small_fs/test_file.txt")
                can_create_files = result.exit_code == 0
                
            
            checks = [
                ("Container is running", container_running),
                ("Can create new files", can_create_files),
            ]
            
            all_passed = all(passed for _, passed in checks)
            
            feedback_lines = []
            for check_name, passed in checks:
                status = " PASS" if passed else " FAIL"
                feedback_lines.append(f"{status} {check_name}")
            
            if all_passed:
                return {
                    "passed": True,
                    "feedback": "\n".join(feedback_lines) + "\n\n🎉 Scenario completed successfully! You've resolved the inode exhaustion issue!"
                }
            else:
                return {
                    "passed": False,
                    "feedback": "\n".join(feedback_lines),
                    "hints": "Check inode usage with 'df -i /mnt/small_fs' and look in /mnt/small_fs/logs/ for many small files"
                }
                
        except docker.errors.NotFound:
            return {"passed": False, "feedback": " Container not found"}
        except Exception as e:
            return {"passed": False, "feedback": f" Error: {str(e)}"}

    def reset(self) -> bool:
        """Reset scenario to broken state"""
        try:
            # TODO: Reset to broken state
            # Usually: stop() then start()
            return self.stop() and self.start().get("success", False)
        except Exception:
            return False

    def _image_exists(self, image_name: str) -> bool:
        """Check if Docker image exists"""
        try:
            self.docker_client.images.get(image_name)
            return True
        except docker.errors.ImageNotFound:
            return False

# REQUIRED: Export the scenario class
scenario_class = NoSpaceLeft