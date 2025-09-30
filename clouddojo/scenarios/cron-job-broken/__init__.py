# scenarios/cron-job-broken/__init__.py
"""
Cron Job Broken Scenario
A scenario where scheduled backup jobs have stopped working
"""

import os
import subprocess
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from clouddojo.base_scenario import BaseScenario
from clouddojo.scenario_metadata import ScenarioMetadata, StoryContext, Hint, CompanyType

class CronJobBrokenMetadata(ScenarioMetadata):
    """Metadata for cron-job-broken scenario"""
    
    def get_story_context(self) -> StoryContext:
        return StoryContext(
            company_name="SecureData Corp",
            company_type=CompanyType.ENTERPRISE,
            your_role="System Administrator",
            situation="The automated daily backup job hasn't run for 3 days. The backup script exists but the cron job seems to be broken.",
            urgency="critical",
            stakeholders=["IT Manager", "Compliance Officer", "Database Team"],
            business_impact="Data backup compliance violated. Risk of data loss.",
            success_criteria="Automated backup job running successfully on schedule"
        )
    
    def get_hints(self) -> List[Hint]:
        return [
            Hint(1, "Check Cron Service", 
                 "First verify that the cron service is running on the system.",
                 "systemctl status cron || service cron status"),
            
            Hint(2, "List Cron Jobs", 
                 "Check what cron jobs are currently scheduled for your user.",
                 "crontab -l"),
            
            Hint(3, "Check Cron Syntax", 
                 "Look at the backup cron job syntax. Is the schedule format correct?",
                 "cat /tmp/clouddojo-backup.cron"),
            
            Hint(4, "Install Fixed Cron Job", 
                 "Install the corrected cron job to schedule the backup properly.",
                 "crontab /tmp/clouddojo-backup.cron")
        ]
    
    def get_learning_path(self) -> str:
        return "production-sre"
    
    def get_completion_story(self, time_taken: int) -> str:
        time_str = f"{time_taken // 60}m {time_taken % 60}s" if time_taken > 0 else "record time"
        return f"Backup job is scheduled and working! The compliance officer is relieved and the IT manager commends your cron troubleshooting skills. Data backup compliance restored. Resolution time: {time_str}"

class CronJobBrokenScenario(BaseScenario):
    """Cron job troubleshooting scenario"""
    
    def __init__(self, name: str):
        super().__init__(name)
        self.cron_file = Path("/tmp/clouddojo-backup.cron")
        self.backup_script = Path("/tmp/clouddojo-backup.sh")
        self.backup_log = Path("/tmp/clouddojo-backup.log")
        self._metadata = CronJobBrokenMetadata()
    
    def get_metadata(self) -> Optional[ScenarioMetadata]:
        """Return embedded metadata"""
        return self._metadata
    
    @property
    def description(self) -> str:
        return "Scheduled backup cron job has stopped working due to syntax errors"
    
    @property
    def difficulty(self) -> str:
        return "beginner"
    
    @property
    def technologies(self) -> list:
        return ["linux", "cron", "scheduling", "backup", "system-administration"]
    
    def start(self) -> Dict[str, Any]:
        """Start the cron job broken scenario"""
        try:
            # Clean up any existing scenario files
            for file_path in [self.cron_file, self.backup_script, self.backup_log]:
                if file_path.exists():
                    file_path.unlink()
            
            # Create backup script
            backup_script_content = """#!/bin/bash
# CloudDojo Backup Script
echo "$(date): Starting backup process..." >> /tmp/clouddojo-backup.log
echo "$(date): Backing up important files..." >> /tmp/clouddojo-backup.log
# Simulate backup process
sleep 2
echo "$(date): Backup completed successfully!" >> /tmp/clouddojo-backup.log
"""
            self.backup_script.write_text(backup_script_content)
            self.backup_script.chmod(0o755)
            
            # Create broken cron job (invalid syntax)
            broken_cron_content = """# CloudDojo Backup Cron Job
# This cron job should run every day at 2 AM
# But there's a syntax error in the schedule
0 2 * * * /tmp/clouddojo-backup.sh
# BROKEN: Invalid day specification
0 3 * * 8 /tmp/clouddojo-backup.sh
# BROKEN: Invalid minute specification  
60 4 * * * /tmp/clouddojo-backup.sh
"""
            self.cron_file.write_text(broken_cron_content)
            
            # Create a working version for comparison
            working_cron_content = """# CloudDojo Backup Cron Job - FIXED VERSION
# Run backup every day at 2 AM
0 2 * * * /tmp/clouddojo-backup.sh
"""
            Path("/tmp/clouddojo-backup-fixed.cron").write_text(working_cron_content)
            
            # Save state
            self.save_state({
                'cron_file': str(self.cron_file),
                'backup_script': str(self.backup_script),
                'started_at': time.time()
            })
            
            connection_info = f"""Cron File: {self.cron_file}
Backup Script: {self.backup_script}
Backup Log: {self.backup_log}
Check cron: crontab -l"""
            
            instructions = f"""🔧 TROUBLESHOOTING SCENARIO: Broken Cron Job

📋 SITUATION:
The automated daily backup job hasn't run for 3 days due to cron configuration issues.

🎯 YOUR MISSION:
1. Check if cron service is running:
   systemctl status cron
2. Examine the current cron jobs:
   crontab -l
3. Check the broken cron file:
   cat {self.cron_file}
4. Fix the cron syntax errors and install:
   crontab {self.cron_file}

💡 HINTS:
• Cron format: minute hour day month weekday command
• Minutes: 0-59, Hours: 0-23, Days: 1-31, Months: 1-12, Weekdays: 0-7
• Invalid values will cause cron jobs to fail
• Use 'crontab -l' to verify installation

🏁 SUCCESS CRITERIA:
• Cron service is running
• Valid cron job is installed
• Backup script can be executed
• No syntax errors in cron schedule

💡 TIP: Fix the cron syntax and install the job to complete the challenge
"""
            
            return {
                "success": True,
                "connection_info": connection_info,
                "instructions": instructions,
                "cron_file": str(self.cron_file)
            }
            
        except Exception as e:
            return {"success": False, "error": f"Failed to start scenario: {str(e)}"}
    
    def stop(self) -> bool:
        """Stop and cleanup the scenario"""
        try:
            # Remove cron job if installed
            try:
                subprocess.run(["crontab", "-r"], check=False, capture_output=True)
            except:
                pass
            
            # Clean up files
            for file_path in [self.cron_file, self.backup_script, self.backup_log, 
                             Path("/tmp/clouddojo-backup-fixed.cron")]:
                if file_path.exists():
                    file_path.unlink()
            
            self.clear_state()
            return True
        except Exception:
            return False
    
    def status(self) -> Dict[str, Any]:
        """Get current status of the scenario"""
        try:
            # Check if files exist
            files_exist = all(f.exists() for f in [self.cron_file, self.backup_script])
            
            # Check if cron job is installed
            try:
                result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
                cron_installed = "clouddojo-backup" in result.stdout
            except:
                cron_installed = False
            
            details = f"""Scenario Status: Active
Cron File: {'✅' if self.cron_file.exists() else '❌'}
Backup Script: {'✅' if self.backup_script.exists() else '❌'}
Cron Job Installed: {'✅' if cron_installed else '❌'}"""
            
            return {"running": files_exist, "details": details}
        except Exception as e:
            return {"running": False, "details": f"Error: {str(e)}"}
    
    def check(self) -> Dict[str, Any]:
        """Check if cron job has been fixed"""
        try:
            checks = []
            all_passed = True
            
            # Check if cron service is running
            try:
                result = subprocess.run(
                    ["systemctl", "is-active", "cron"], 
                    capture_output=True, 
                    text=True
                )
                cron_running = result.returncode == 0
                if not cron_running:
                    # Try alternative service name
                    result = subprocess.run(
                        ["systemctl", "is-active", "crond"], 
                        capture_output=True, 
                        text=True
                    )
                    cron_running = result.returncode == 0
            except:
                cron_running = True  # Assume running if can't check
            
            checks.append(("Cron service is running", cron_running))
            if not cron_running:
                all_passed = False
            
            # Check if cron job is installed
            try:
                result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
                cron_output = result.stdout
                has_backup_job = "clouddojo-backup.sh" in cron_output
                checks.append(("Backup cron job is installed", has_backup_job))
                if not has_backup_job:
                    all_passed = False
                
                # Check for syntax errors (no invalid schedules)
                lines = cron_output.split('\n')
                valid_syntax = True
                for line in lines:
                    if line.strip() and not line.strip().startswith('#'):
                        parts = line.split()
                        if len(parts) >= 5:
                            try:
                                minute, hour, day, month, weekday = parts[:5]
                                # Check for common errors
                                if (int(minute) > 59 or int(hour) > 23 or 
                                    int(day) > 31 or int(month) > 12 or 
                                    int(weekday) > 7):
                                    valid_syntax = False
                                    break
                            except (ValueError, IndexError):
                                pass  # Skip non-standard cron lines
                
                checks.append(("Cron syntax is valid", valid_syntax))
                if not valid_syntax:
                    all_passed = False
                    
            except subprocess.CalledProcessError:
                checks.append(("Backup cron job is installed", False))
                checks.append(("Cron syntax is valid", False))
                all_passed = False
            
            # Check if backup script is executable
            script_executable = self.backup_script.exists() and os.access(self.backup_script, os.X_OK)
            checks.append(("Backup script is executable", script_executable))
            if not script_executable:
                all_passed = False
            
            # Generate feedback
            feedback_lines = []
            for check_name, passed in checks:
                status = "✅ PASS" if passed else "❌ FAIL"
                feedback_lines.append(f"{status} {check_name}")
            
            if all_passed:
                return {
                    "passed": True,
                    "feedback": "\n".join(feedback_lines) + "\n\n🎉 Perfect! The backup cron job is now properly configured and scheduled!"
                }
            else:
                return {
                    "passed": False,
                    "feedback": "\n".join(feedback_lines),
                    "hints": """💡 DEBUGGING HINTS:
• Check cron service: systemctl status cron
• Fix syntax errors in cron file before installing
• Cron format: minute(0-59) hour(0-23) day(1-31) month(1-12) weekday(0-7)
• Install cron job: crontab /tmp/clouddojo-backup.cron
• Verify installation: crontab -l"""
                }
                
        except Exception as e:
            return {"passed": False, "feedback": f"❌ Error checking solution: {str(e)}"}
    
    def reset(self) -> bool:
        """Reset scenario to broken state"""
        try:
            # Remove any installed cron jobs
            try:
                subprocess.run(["crontab", "-r"], check=False, capture_output=True)
            except:
                pass
            
            # Recreate broken cron file
            if self.cron_file.exists():
                broken_cron_content = """# CloudDojo Backup Cron Job
# This cron job should run every day at 2 AM
# But there's a syntax error in the schedule
0 2 * * * /tmp/clouddojo-backup.sh
# BROKEN: Invalid day specification
0 3 * * 8 /tmp/clouddojo-backup.sh
# BROKEN: Invalid minute specification  
60 4 * * * /tmp/clouddojo-backup.sh
"""
                self.cron_file.write_text(broken_cron_content)
            
            return True
        except Exception:
            return False

# Export scenario
scenario_class = CronJobBrokenScenario