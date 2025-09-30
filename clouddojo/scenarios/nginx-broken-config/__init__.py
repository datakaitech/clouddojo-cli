# scenarios/nginx-broken-config/__init__.py
"""
Nginx Broken Configuration Scenario
A scenario where nginx fails to start due to configuration errors
"""

import os
import docker
import subprocess
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from clouddojo.base_scenario import BaseScenario
from clouddojo.scenario_metadata import ScenarioMetadata, StoryContext, Hint, CompanyType

class NginxBrokenConfigMetadata(ScenarioMetadata):
    """Metadata for nginx-broken-config scenario"""
    
    def get_story_context(self) -> StoryContext:
        return StoryContext(
            company_name="TechFlow Startup",
            company_type=CompanyType.STARTUP,
            your_role="DevOps Engineer",
            situation="The company website went down right before a major product launch demo to investors. The nginx web server won't start after a configuration update.",
            urgency="critical",
            stakeholders=["CEO", "CTO", "Marketing Team", "Potential Investors"],
            business_impact="$2M funding round at risk. Demo scheduled in 2 hours.",
            success_criteria="Website must be accessible and serving content properly"
        )
    
    def get_hints(self) -> List[Hint]:
        return [
            Hint(1, "Check Nginx Status", 
                 "Nginx won't start. Check what the error logs tell you about the configuration.",
                 "docker exec -it clouddojo-nginx-broken-config nginx -t"),
            
            Hint(2, "Examine Config Files", 
                 "Look at the nginx configuration files to find syntax errors or missing files.",
                 "docker exec -it clouddojo-nginx-broken-config cat /etc/nginx/nginx.conf"),
            
            Hint(3, "Fix Configuration", 
                 "Replace the broken config files with the working versions provided in the scenario.",
                 "docker exec -it clouddojo-nginx-broken-config cp /etc/nginx/nginx.conf.working /etc/nginx/nginx.conf"),
            
            Hint(4, "Restart Service", 
                 "After fixing the configuration, restart nginx to apply the changes.",
                 "docker exec -it clouddojo-nginx-broken-config nginx -s reload")
        ]
    
    def get_learning_path(self) -> str:
        return "docker-basics"
    
    def get_completion_story(self, time_taken: int) -> str:
        time_str = f"{time_taken // 60}m {time_taken % 60}s" if time_taken > 0 else "record time"
        return f"The website is back online! The investor demo went perfectly, and TechFlow secured their $2M funding round. The CEO personally thanked you for saving the company. Time to resolution: {time_str}"

class NginxBrokenConfigScenario(BaseScenario):
    """Nginx broken configuration troubleshooting scenario"""
    
    def __init__(self, name: str):
        super().__init__(name)
        self.container_name = f"clouddojo-{name}"
        self.docker_client = docker.from_env()
        self.scenario_dir = Path(__file__).parent
        self._metadata = NginxBrokenConfigMetadata()
    
    def get_metadata(self) -> Optional[ScenarioMetadata]:
        """Return embedded metadata"""
        return self._metadata
    
    @property
    def description(self) -> str:
        return "Nginx web server fails to start due to configuration syntax errors and permission issues"
    
    @property
    def difficulty(self) -> str:
        return "beginner"
    
    @property
    def technologies(self) -> list:
        return ["nginx", "docker", "linux", "configuration"]
    
    def start(self) -> Dict[str, Any]:
        """Start the broken nginx scenario"""
        try:
            # Remove container if it already exists
            try:
                existing_container = self.docker_client.containers.get(self.container_name)
                existing_container.remove(force=True)
            except docker.errors.NotFound:
                pass
            
            image_tag = f"clouddojo/{self.name}"
            dockerfile_path = self.scenario_dir / "Dockerfile"
            
            if not dockerfile_path.exists():
                return {
                    "success": False,
                    "error": "Scenario Dockerfile not found. Please ensure the scenario is properly installed."
                }
            
            # Verify Docker is accessible
            try:
                self.docker_client.ping()
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Docker daemon not accessible: {e}. Please ensure Docker is running."
                }
            
            # Build the Docker image only if it doesn't exist
            try:
                self.docker_client.images.get(image_tag)
            except docker.errors.ImageNotFound:
                self.docker_client.images.build(
                    path=str(self.scenario_dir),
                    tag=image_tag,
                    rm=True
                )
            
            # Run the container (detached, expose port 80)
            container = self.docker_client.containers.run(
                image_tag,
                name=self.container_name,
                detach=True,
                ports={'80/tcp': None},  # random host port
                tty=True,
                stdin_open=True
            )
            
            time.sleep(2)  # let container boot
            
            container.reload()
            port_mapping = container.attrs['NetworkSettings']['Ports'].get('80/tcp')
            host_port = port_mapping[0]['HostPort'] if port_mapping else 'N/A'
            
            # Save state
            self.save_state({
                'container_id': container.id,
                'container_name': self.container_name,
                'host_port': host_port,
                'started_at': time.time()
            })
            
            connection_info = f"""Container: {self.container_name}
Access: docker exec -it {self.container_name} bash
Host port mapped: {host_port}
Container ID: {container.id[:12]}"""
            
            instructions = f"""🔧 TROUBLESHOOTING SCENARIO: Broken Nginx Configuration

📋 SITUATION:
The nginx web server should be running but has failed to start due to configuration errors.

🎯 YOUR MISSION:
1. Exec into the container:
   docker exec -it {self.container_name} bash
2. Investigate why nginx is not running
3. Fix the configuration issues
4. Start the nginx service successfully
5. Verify it's accessible on port 80

💡 HINTS:
• Check nginx error logs: /var/log/nginx/error.log
• Test config syntax: nginx -t
• Check file permissions on config files
• Look for common nginx config mistakes (missing semicolons, wrong paths, etc.)

🏁 SUCCESS CRITERIA:
• Nginx service is running (systemctl status nginx OR service nginx status)
• Configuration passes syntax check (nginx -t)
• Web server responds on port 80 (curl http://localhost OR wget -qO- http://localhost)

💡 TIP: Fix the nginx configuration syntax errors
"""
            
            return {
                "success": True,
                "connection_info": connection_info,
                "instructions": instructions,
                "container_name": self.container_name,
                "port": host_port
            }
            
        except Exception as e:
            return {"success": False, "error": f"Failed to start scenario: {str(e)}"}
    
    def stop(self) -> bool:
        """Stop and remove the nginx scenario container"""
        try:
            container = self.docker_client.containers.get(self.container_name)
            container.remove(force=True)
            self.clear_state()
            return True
        except docker.errors.NotFound:
            self.clear_state()  # Clear state even if container doesn't exist
            return True
        except Exception:
            return False
    
    def status(self) -> Dict[str, Any]:
        """Get current status of the scenario"""
        try:
            container = self.docker_client.containers.get(self.container_name)
            state = self.load_state()
            
            # Check nginx status inside container
            try:
                exec_result = container.exec_run("pgrep nginx", user="root")
                nginx_running = exec_result.exit_code == 0
            except:
                nginx_running = False
            
            details = f"""Container Status: {container.status}
Nginx Running: {'✅ Yes' if nginx_running else '❌ No'}
Container ID: {container.id[:12]}
Host Port: {state.get('host_port', 'N/A')}"""
            
            return {"running": container.status == "running", "details": details}
        except docker.errors.NotFound:
            return {
                "running": False,
                "details": "Container not found"
            }
        except Exception as e:
            return {
                "running": False,
                "details": f"Error: {str(e)}"
            }
    
    def check(self) -> Dict[str, Any]:
        """Check if the nginx configuration has been fixed"""
        try:
            container = self.docker_client.containers.get(self.container_name)
            
            checks = []
            all_passed = True
            
            # Check 1: Nginx process is running
            exec_result = container.exec_run("pgrep nginx", user="root")
            nginx_running = exec_result.exit_code == 0
            checks.append(("Nginx process running", nginx_running))
            if not nginx_running:
                all_passed = False
            
            # Check 2: Configuration syntax is valid
            exec_result = container.exec_run("nginx -t", user="root")
            config_valid = exec_result.exit_code == 0
            checks.append(("Configuration syntax valid", config_valid))
            if not config_valid:
                all_passed = False
            
            # Check 3: Web server responds on port 80
            exec_result = container.exec_run("curl -s -o /dev/null -w '%{http_code}' http://localhost", user="root")
            web_responds = exec_result.exit_code == 0 and b"200" in exec_result.output
            checks.append(("Web server responding", web_responds))
            if not web_responds:
                all_passed = False
            
            # # Check 4: Nginx service status (if systemd is available)
            # exec_result = container.exec_run("systemctl is-active nginx 2>/dev/null || service nginx status", user="root")
            # service_active = exec_result.exit_code == 0
            # checks.append(("Nginx service active", service_active))
            
            # Generate feedback
            feedback_lines = []
            for check_name, passed in checks:
                status = "✅ PASS" if passed else "❌ FAIL"
                feedback_lines.append(f"{status} {check_name}")
            
            if all_passed:
                feedback = "\n".join(feedback_lines) + "\n\n🎉 Excellent work! You've successfully fixed the nginx configuration!"
                return {
                    "passed": True,
                    "feedback": feedback
                }
            else:
                feedback = "\n".join(feedback_lines)
                
                hints = """💡 DEBUGGING HINTS:
• If nginx process isn't running: Check error logs in /var/log/nginx/error.log
• If config is invalid: Run 'nginx -t' to see specific syntax errors
• If web server not responding: Ensure nginx is bound to port 80 and listening
• Check file permissions on nginx config files (should be readable)
• Look for common issues: missing semicolons, typos in directives, wrong file paths"""
                
                return {
                    "passed": False,
                    "feedback": feedback,
                    "hints": hints
                }
                
        except docker.errors.NotFound:
            return {
                "passed": False,
                "feedback": "❌ Container not found. Please start the scenario first.",
                "hints": "Run 'clouddojo start nginx-broken-config' to start the scenario."
            }
        except Exception as e:
            return {
                "passed": False,
                "feedback": f"❌ Error checking solution: {str(e)}"
            }
    
    def reset(self) -> bool:
        """Reset the scenario to broken state"""
        try:
            container = self.docker_client.containers.get(self.container_name)
            
            # Stop nginx if it's running
            container.exec_run("systemctl stop nginx 2>/dev/null || service nginx stop", user="root")
            
            # Restore broken configuration files
            # Copy the broken config back from backup
            container.exec_run("cp /etc/nginx/nginx.conf.broken /etc/nginx/nginx.conf", user="root")
            container.exec_run("cp /etc/nginx/sites-available/default.broken /etc/nginx/sites-available/default", user="root")
            
            return True
        except Exception:
            return False

# Export the scenario class
scenario_class = NginxBrokenConfigScenario