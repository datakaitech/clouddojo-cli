# filepath: ./clouddojo/scenarios/nginx-broken-symlink/__init__.py
"""
Nginx Broken Symlink Scenario
A scenario where nginx fails to start due to a broken symlink in sites-enabled
"""

import docker
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from clouddojo.base_scenario import BaseScenario
from clouddojo.scenario_metadata import ScenarioMetadata, StoryContext, Hint, CompanyType


class NginxBrokenMetadata(ScenarioMetadata):
    """Metadata for nginx-broken scenario"""
    
    def get_story_context(self) -> StoryContext:
        return StoryContext(
            company_name="DevStart Solutions",
            company_type=CompanyType.STARTUP,
            your_role="Junior DevOps Engineer",
            situation="The company blog website is down after a server migration. The nginx configuration seems correct but the service won't start properly.",
            urgency="medium",
            stakeholders=["Marketing Team", "Content Writers", "Engineering Manager"],
            business_impact="Blog traffic lost, SEO ranking dropping, content team blocked.",
            success_criteria="Website accessible and serving content correctly"
        )
    
    def get_hints(self) -> List[Hint]:
        return [
            Hint(1, "Check Symlinks", 
                 "Nginx won't start due to configuration issues. Check what the symlink in sites-enabled points to.",
                 "ls -l /etc/nginx/sites-enabled/"),
            
            Hint(2, "Investigate Target", 
                 "The symlink points to a file that doesn't exist. Check what files are available in sites-available.",
                 "ls -la /etc/nginx/sites-available/"),
            
            Hint(3, "Fix the Symlink", 
                 "Remove the broken symlink and create a new one pointing to the working configuration.",
                 "rm /etc/nginx/sites-enabled/default && ln -s /etc/nginx/sites-available/default.working /etc/nginx/sites-enabled/default"),
            
            Hint(4, "Restart Nginx", 
                 "After fixing the symlink, test the configuration and restart nginx to apply changes.",
                 "nginx -t && nginx -s reload")
        ]
    
    def get_learning_path(self) -> str:
        return "docker-basics"
    
    def get_completion_story(self, time_taken: int) -> str:
        time_str = f"{time_taken // 60}m {time_taken % 60}s" if time_taken > 0 else "record time"
        return f"Blog is live again! The marketing team can publish their content and SEO rankings are recovering. Your quick symlink fix impressed the engineering manager. Resolution time: {time_str}"

class NginxBroken(BaseScenario):
    """Nginx broken symlink troubleshooting scenario"""

    def __init__(self, name: str):
        super().__init__(name)
        self.container_name = f"clouddojo-{name}"
        self.docker_client = docker.from_env()
        self.scenario_dir = Path(__file__).parent
        self._metadata = NginxBrokenMetadata()
    
    def get_metadata(self) -> Optional[ScenarioMetadata]:
        """Return embedded metadata"""
        return self._metadata

    @property
    def description(self) -> str:
        return "Nginx fails to start due to a broken symlink between sites-available and sites-enabled"

    @property
    def difficulty(self) -> str:
        return "beginner"

    @property
    def technologies(self) -> list:
        return ["nginx", "docker", "linux", "configuration"]

    def start(self) -> Dict[str, Any]:
        """Start the broken symlink nginx scenario"""
        try:
            # Remove container if it already exists
            try:
                existing_container = self.docker_client.containers.get(self.container_name)
                existing_container.remove(force=True)
            except docker.errors.NotFound:
                pass

            image_tag = f"clouddojo/{self.name}"
            dockerfile_path = self.scenario_dir / "Dockerfile"
            
            # Debug path information
            debug_info = f"""Debug Info:
- __file__: {__file__}
- scenario_dir: {self.scenario_dir}
- dockerfile_path: {dockerfile_path}
- dockerfile_exists: {dockerfile_path.exists()}
- scenario_dir_exists: {self.scenario_dir.exists()}
- scenario_dir_contents: {list(self.scenario_dir.iterdir()) if self.scenario_dir.exists() else 'N/A'}"""

            if not dockerfile_path.exists():
                return {
                    "success": False,
                    "error": f"Scenario Dockerfile not found.\n\n{debug_info}"
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
Access: docker exec -it {self.container_name} sh
Host port mapped: {host_port}
Container ID: {container.id[:12]}"""

            instructions = f"""🔧 TROUBLESHOOTING SCENARIO: Broken Nginx Symlink

📋 SITUATION:
Nginx is installed but fails to start because the configuration in
`/etc/nginx/sites-enabled/default` points to a nonexistent file.

🎯 YOUR MISSION:
1. Exec into the container:
   docker exec -it {self.container_name} sh
2. Investigate symlinks in /etc/nginx/sites-enabled
3. Fix the broken symlink to point to the valid config in /etc/nginx/sites-available/default.working
4. Reload nginx (`nginx -s reload` or restart it)
5. Verify that nginx responds on port 80

💡 HINTS:
• Run `ls -l /etc/nginx/sites-enabled/` to see what the symlink points to
• Test config with `nginx -t`
• Reload nginx after fixing the symlink

🏁 SUCCESS CRITERIA:
• The symlink points to a valid config
• `nginx -t` reports syntax OK
• Web server responds with HTTP 200 on port 80

💡 TIP: Fix the nginx configuration to make the web server work
"""

            return {
                "success": True,
                "connection_info": connection_info,
                "instructions": instructions
            }

        except Exception as e:
            return {"success": False, "error": f"Failed to start scenario: {str(e)}"}

    def stop(self) -> bool:
        try:
            container = self.docker_client.containers.get(self.container_name)
            container.remove(force=True)
            self.clear_state()
            return True
        except docker.errors.NotFound:
            self.clear_state()
            return True
        except Exception:
            return False

    def status(self) -> Dict[str, Any]:
        try:
            container = self.docker_client.containers.get(self.container_name)
            state = self.load_state()

            exec_result = container.exec_run("pgrep nginx", user="root")
            nginx_running = exec_result.exit_code == 0

            details = f"""Container Status: {container.status}
Nginx Running: {'✅ Yes' if nginx_running else '❌ No'}
Container ID: {container.id[:12]}
Host Port: {state.get('host_port', 'N/A')}"""

            return {"running": container.status == "running", "details": details}
        except docker.errors.NotFound:
            return {"running": False, "details": "Container not found"}
        except Exception as e:
            return {"running": False, "details": f"Error: {str(e)}"}

    def check(self) -> Dict[str, Any]:
        try:
            container = self.docker_client.containers.get(self.container_name)

            checks = []
            all_passed = True

            # --- Check symlink properly ---
            exec_result = container.exec_run(
                "readlink -f /etc/nginx/sites-enabled/default", user="root"
            )
            target = exec_result.output.strip().decode("utf-8")
            symlink_ok = target == "/etc/nginx/sites-available/default.working"
            checks.append((f"Symlink fixed (Currently points to: {target})", symlink_ok, ""))

            if not symlink_ok:
                all_passed = False

            # --- Check config syntax ---
            exec_result = container.exec_run("nginx -t", user="root")
            config_ok = exec_result.exit_code == 0
            checks.append(("Config syntax valid", config_ok, ""))
            if not config_ok:
                all_passed = False

            # --- Check HTTP response (200) ---
            exec_result = container.exec_run(
                "curl -s -o /dev/null -w '%{http_code}' http://localhost", user="root"
            )
            http_ok = exec_result.exit_code == 0 and b"200" in exec_result.output
            http_reason = ""
            if not http_ok:
                http_reason = f"(Got {exec_result.output.decode().strip() or 'no response'})"
            checks.append(("Web responds with 200", http_ok, http_reason))
            if not http_ok:
                all_passed = False

            # --- Check page content ---
            exec_result = container.exec_run("curl -s http://localhost/index.html", user="root")
            content_ok = exec_result.exit_code == 0 and b"It works!" in exec_result.output
            content_reason = ""
            if not content_ok:
                content_reason = f"(Got {exec_result.output.decode().strip() or 'no content'})"
            checks.append(("Web serves expected content", content_ok, content_reason))
            if not content_ok:
                all_passed = False

            # --- Feedback formatting ---
            feedback_lines = []
            for name, passed, reason in checks:
                status = "✅ PASS" if passed else "❌ FAIL"
                line = f"{status} {name}"
                if reason and not passed:
                    line += f" {reason}"
                feedback_lines.append(line)

            if all_passed:
                return {
                    "passed": True,
                    "feedback": "\n".join(feedback_lines) + "\n\n🎉 Symlink fixed successfully and page served!"
                }
            else:
                return {
                    "passed": False,
                    "feedback": "\n".join(feedback_lines),
                    "hints": """💡 DEBUGGING HINTS:
• Ensure the symlink points to /etc/nginx/sites-available/default.working
• Run `nginx -t` after fixing
• Reload nginx with `nginx -s reload`
• Verify that /usr/share/nginx/html/index.html contains the expected text
"""
                }

        except docker.errors.NotFound:
            return {
                "passed": False,
                "feedback": "❌ Container not found. Please start the scenario first."
            }
        except Exception as e:
            return {"passed": False, "feedback": f"❌ Error checking solution: {str(e)}"}

    def reset(self) -> bool:
        try:
            container = self.docker_client.containers.get(self.container_name)
            container.exec_run("rm -f /etc/nginx/sites-enabled/default", user="root")
            container.exec_run("ln -s /etc/nginx/sites-available/nonexistent /etc/nginx/sites-enabled/default", user="root")
            container.exec_run("nginx -s stop || true", user="root")
            return True
        except Exception:
            return False


# Export scenario
scenario_class = NginxBroken
