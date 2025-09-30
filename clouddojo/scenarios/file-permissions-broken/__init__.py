# scenarios/file-permissions-broken/__init__.py
"""
File Permissions Broken Scenario
A scenario where website files have wrong permissions preventing web server access
"""

import os
import subprocess
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from clouddojo.base_scenario import BaseScenario
from clouddojo.scenario_metadata import ScenarioMetadata, StoryContext, Hint, CompanyType

class FilePermissionsBrokenMetadata(ScenarioMetadata):
    """Metadata for file-permissions-broken scenario"""
    
    def get_story_context(self) -> StoryContext:
        return StoryContext(
            company_name="WebCraft Agency",
            company_type=CompanyType.STARTUP,
            your_role="Junior System Administrator",
            situation="After a server migration, the company website shows '403 Forbidden' errors. The web server can't access the website files due to incorrect permissions.",
            urgency="high",
            stakeholders=["Web Development Team", "Project Manager", "Client"],
            business_impact="Client website down. Reputation and contract at risk.",
            success_criteria="Website accessible with proper file permissions"
        )
    
    def get_hints(self) -> List[Hint]:
        return [
            Hint(1, "Check File Permissions", 
                 "Look at the current permissions on the website files. What do you see?",
                 "ls -la /tmp/clouddojo-website/"),
            
            Hint(2, "Identify the Problem", 
                 "The files have no read permissions for others. Web servers need to read these files.",
                 "ls -la /tmp/clouddojo-website/index.html"),
            
            Hint(3, "Fix File Permissions", 
                 "Make the files readable by the web server. Use chmod to set proper permissions.",
                 "chmod 644 /tmp/clouddojo-website/*"),
            
            Hint(4, "Fix Directory Permissions", 
                 "Don't forget the directory needs execute permissions for traversal.",
                 "chmod 755 /tmp/clouddojo-website/")
        ]
    
    def get_learning_path(self) -> str:
        return "docker-basics"
    
    def get_completion_story(self, time_taken: int) -> str:
        time_str = f"{time_taken // 60}m {time_taken % 60}s" if time_taken > 0 else "record time"
        return f"Website is back online! The client is happy and the project manager is relieved. You've learned the importance of proper file permissions in web hosting. Resolution time: {time_str}"

class FilePermissionsBrokenScenario(BaseScenario):
    """File permissions troubleshooting scenario"""
    
    def __init__(self, name: str):
        super().__init__(name)
        self.scenario_dir = Path("/tmp/clouddojo-website")
        self._metadata = FilePermissionsBrokenMetadata()
    
    def get_metadata(self) -> Optional[ScenarioMetadata]:
        """Return embedded metadata"""
        return self._metadata
    
    @property
    def description(self) -> str:
        return "Website files have wrong permissions causing 403 Forbidden errors"
    
    @property
    def difficulty(self) -> str:
        return "beginner"
    
    @property
    def technologies(self) -> list:
        return ["linux", "permissions", "filesystem", "web-server"]
    
    def start(self) -> Dict[str, Any]:
        """Start the file permissions scenario"""
        try:
            # Clean up any existing scenario
            if self.scenario_dir.exists():
                subprocess.run(["rm", "-rf", str(self.scenario_dir)], check=True)
            
            # Create scenario directory and files
            self.scenario_dir.mkdir(parents=True, exist_ok=True)
            
            # Create website files
            (self.scenario_dir / "index.html").write_text("""<!DOCTYPE html>
<html>
<head><title>WebCraft Agency</title></head>
<body>
    <h1>Welcome to WebCraft Agency!</h1>
    <p>Your website is working correctly.</p>
</body>
</html>""")
            
            (self.scenario_dir / "style.css").write_text("""
body { font-family: Arial, sans-serif; margin: 40px; }
h1 { color: #333; }
""")
            
            (self.scenario_dir / "script.js").write_text("""
console.log('WebCraft Agency website loaded successfully!');
""")
            
            # Set broken permissions (no read access for others)
            subprocess.run(["chmod", "000", str(self.scenario_dir / "index.html")], check=True)
            subprocess.run(["chmod", "000", str(self.scenario_dir / "style.css")], check=True)
            subprocess.run(["chmod", "000", str(self.scenario_dir / "script.js")], check=True)
            subprocess.run(["chmod", "600", str(self.scenario_dir)], check=True)
            
            # Save state
            self.save_state({
                'scenario_path': str(self.scenario_dir),
                'started_at': time.time()
            })
            
            connection_info = f"""Files Location: {self.scenario_dir}
Check permissions: ls -la {self.scenario_dir}/
Files affected: index.html, style.css, script.js"""
            
            instructions = f"""🔧 TROUBLESHOOTING SCENARIO: Broken File Permissions

📋 SITUATION:
Website files have incorrect permissions after server migration, causing 403 Forbidden errors.

🎯 YOUR MISSION:
1. Check current file permissions:
   ls -la {self.scenario_dir}/
2. Identify what's wrong with the permissions
3. Fix file permissions to allow web server access
4. Verify files are readable

💡 HINTS:
• Web servers need read (r) permission on files
• Directories need execute (x) permission for traversal
• Use chmod to modify permissions
• Standard web file permissions: 644 for files, 755 for directories

🏁 SUCCESS CRITERIA:
• All files have read permissions for others (r-- in permissions)
• Directory has execute permissions for others (--x in permissions)
• Files can be read by any user

💡 TIP: Use chmod to fix file and directory permissions
"""
            
            return {
                "success": True,
                "connection_info": connection_info,
                "instructions": instructions,
                "scenario_path": str(self.scenario_dir)
            }
            
        except Exception as e:
            return {"success": False, "error": f"Failed to start scenario: {str(e)}"}
    
    def stop(self) -> bool:
        """Stop and cleanup the scenario"""
        try:
            if self.scenario_dir.exists():
                subprocess.run(["rm", "-rf", str(self.scenario_dir)], check=True)
            self.clear_state()
            return True
        except Exception:
            return False
    
    def status(self) -> Dict[str, Any]:
        """Get current status of the scenario"""
        try:
            if not self.scenario_dir.exists():
                return {"running": False, "details": "Scenario files not found"}
            
            # Check if files exist
            files = list(self.scenario_dir.glob("*"))
            details = f"""Scenario Status: Active
Files Location: {self.scenario_dir}
Files Count: {len(files)}
Files: {[f.name for f in files]}"""
            
            return {"running": True, "details": details}
        except Exception as e:
            return {"running": False, "details": f"Error: {str(e)}"}
    
    def check(self) -> Dict[str, Any]:
        """Check if file permissions have been fixed"""
        try:
            if not self.scenario_dir.exists():
                return {
                    "passed": False,
                    "feedback": "❌ Scenario files not found. Please start the scenario first."
                }
            
            checks = []
            all_passed = True
            
            # Check directory permissions
            dir_stat = self.scenario_dir.stat()
            dir_perms = oct(dir_stat.st_mode)[-3:]
            dir_readable = dir_stat.st_mode & 0o005  # Check read and execute for others
            checks.append(("Directory has proper permissions (755)", dir_readable == 5))
            if dir_readable != 5:
                all_passed = False
            
            # Check file permissions
            for filename in ["index.html", "style.css", "script.js"]:
                filepath = self.scenario_dir / filename
                if filepath.exists():
                    file_stat = filepath.stat()
                    file_readable = file_stat.st_mode & 0o004  # Check read for others
                    checks.append((f"{filename} is readable", file_readable != 0))
                    if file_readable == 0:
                        all_passed = False
                else:
                    checks.append((f"{filename} exists", False))
                    all_passed = False
            
            # Generate feedback
            feedback_lines = []
            for check_name, passed in checks:
                status = "✅ PASS" if passed else "❌ FAIL"
                feedback_lines.append(f"{status} {check_name}")
            
            if all_passed:
                return {
                    "passed": True,
                    "feedback": "\n".join(feedback_lines) + "\n\n🎉 Perfect! File permissions are now correct and the website is accessible!"
                }
            else:
                return {
                    "passed": False,
                    "feedback": "\n".join(feedback_lines),
                    "hints": """💡 DEBUGGING HINTS:
• Use 'chmod 755' for directories (rwxr-xr-x)
• Use 'chmod 644' for files (rw-r--r--)
• Check permissions with 'ls -la'
• Remember: read(4) + write(2) + execute(1) = permission number"""
                }
                
        except Exception as e:
            return {"passed": False, "feedback": f"❌ Error checking solution: {str(e)}"}
    
    def reset(self) -> bool:
        """Reset scenario to broken state"""
        try:
            if self.scenario_dir.exists():
                # Reset to broken permissions
                subprocess.run(["chmod", "000", str(self.scenario_dir / "index.html")], check=True)
                subprocess.run(["chmod", "000", str(self.scenario_dir / "style.css")], check=True)
                subprocess.run(["chmod", "000", str(self.scenario_dir / "script.js")], check=True)
                subprocess.run(["chmod", "600", str(self.scenario_dir)], check=True)
            return True
        except Exception:
            return False

# Export scenario
scenario_class = FilePermissionsBrokenScenario