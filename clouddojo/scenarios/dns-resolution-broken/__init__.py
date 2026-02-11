# scenarios/dns-resolution-broken/__init__.py
"""
DNS Resolution Broken Scenario
A scenario where DNS configuration is broken preventing domain name resolution
"""

import os
import subprocess
import time
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional
from clouddojo.base_scenario import BaseScenario
from clouddojo.scenario_metadata import ScenarioMetadata, StoryContext, Hint, CompanyType

class DNSResolutionBrokenMetadata(ScenarioMetadata):
    """Metadata for dns-resolution-broken scenario"""
    
    def get_story_context(self) -> StoryContext:
        return StoryContext(
            company_name="GlobalTech Solutions",
            company_type=CompanyType.ENTERPRISE,
            your_role="Network Administrator",
            situation="Multiple applications are failing to connect to external services. Users report they can't access any websites by domain name, but direct IP connections work fine.",
            urgency="critical",
            stakeholders=["IT Director", "Application Teams", "Support Desk", "End Users"],
            business_impact="All external API integrations down. Email services offline. Business operations severely impacted.",
            success_criteria="DNS resolution working, all services can resolve domain names"
        )
    
    def get_hints(self) -> List[Hint]:
        return [
            Hint(1, "Test DNS Resolution", 
                 "First, verify that DNS resolution is actually failing.",
                 "nslookup google.com || dig google.com"),
            
            Hint(2, "Check DNS Configuration", 
                 "Examine the DNS resolver configuration file.",
                 "cat /tmp/clouddojo-resolv.conf"),
            
            Hint(3, "Identify the Problem", 
                 "Look for invalid or unreachable DNS servers in the configuration.",
                 "ping 192.168.999.1 # This IP is invalid"),
            
            Hint(4, "Fix DNS Servers", 
                 "Replace with working DNS servers like Google's or Cloudflare's.",
                 "echo 'nameserver 8.8.8.8' > /tmp/clouddojo-resolv.conf"),
            
            Hint(5, "Add Secondary DNS", 
                 "Always configure a backup DNS server for redundancy.",
                 "echo 'nameserver 1.1.1.1' >> /tmp/clouddojo-resolv.conf")
        ]
    
    def get_learning_path(self) -> str:
        return "production-sre"
    
    def get_completion_story(self, time_taken: int) -> str:
        time_str = f"{time_taken // 60}m {time_taken % 60}s" if time_taken > 0 else "record time"
        return f"DNS resolution restored! All services are back online and external APIs are responding. The IT Director commends your quick diagnosis and the support desk reports all user issues resolved. Resolution time: {time_str}"

class DNSResolutionBrokenScenario(BaseScenario):
    """DNS resolution troubleshooting scenario"""
    
    def __init__(self, name: str):
        super().__init__(name)
        self.resolv_conf = Path("/tmp/clouddojo-resolv.conf")
        self.backup_resolv = Path("/tmp/clouddojo-resolv.conf.backup")
        self.test_domains_file = Path("/tmp/clouddojo-test-domains.txt")
        self._metadata = DNSResolutionBrokenMetadata()
    
    def get_metadata(self) -> Optional[ScenarioMetadata]:
        """Return embedded metadata"""
        return self._metadata
    
    @property
    def description(self) -> str:
        return "DNS configuration is broken with invalid nameservers preventing domain resolution"
    
    @property
    def difficulty(self) -> str:
        return "intermediate"
    
    @property
    def technologies(self) -> list:
        return ["linux", "dns", "networking", "troubleshooting", "system-administration"]
    
    def start(self) -> Dict[str, Any]:
        """Start the DNS resolution broken scenario"""
        try:
            # Clean up any existing scenario files
            for file_path in [self.resolv_conf, self.backup_resolv, self.test_domains_file]:
                if file_path.exists():
                    file_path.unlink()
            
            # Create broken DNS configuration with invalid nameservers
            broken_resolv_content = """# CloudDojo DNS Configuration
# WARNING: These DNS servers are misconfigured!

# Primary DNS - Invalid IP address
nameserver 192.168.999.1

# Secondary DNS - Non-existent server
nameserver 10.0.0.999

# Tertiary DNS - Local IP that's not a DNS server  
nameserver 127.0.0.53

# Domain search path (this part is fine)
search clouddojo.local corp.internal
options timeout:2 attempts:3
"""
            self.resolv_conf.write_text(broken_resolv_content)
            
            # Create a correct version for reference
            correct_resolv_content = """# CloudDojo DNS Configuration - FIXED VERSION
# Using public DNS servers

# Primary DNS - Google
nameserver 8.8.8.8

# Secondary DNS - Cloudflare
nameserver 1.1.1.1

# Tertiary DNS - Google Secondary
nameserver 8.8.4.4

# Domain search path
search clouddojo.local corp.internal
options timeout:2 attempts:3
"""
            self.backup_resolv.write_text(correct_resolv_content)
            
            # Create test domains file
            test_domains = """# Test these domains after fixing DNS
google.com
cloudflare.com
github.com
stackoverflow.com
"""
            self.test_domains_file.write_text(test_domains)
            
            # Save state
            self.save_state({
                'resolv_conf': str(self.resolv_conf),
                'backup_resolv': str(self.backup_resolv),
                'started_at': time.time()
            })
            
            connection_info = f"""DNS Config File: {self.resolv_conf}
Backup Config: {self.backup_resolv}
Test Domains: {self.test_domains_file}
Test DNS: nslookup google.com"""
            
            instructions = f"""🔧 TROUBLESHOOTING SCENARIO: DNS Resolution Failure

📋 SITUATION:
DNS resolution is completely broken. No domains can be resolved but direct IP connections work.

🎯 YOUR MISSION:
1. Test DNS resolution to confirm the issue:
   nslookup google.com
   dig cloudflare.com
   host github.com

2. Check the DNS configuration:
   cat {self.resolv_conf}

3. Identify problems with the nameservers:
   - Invalid IP addresses (999 is not valid in IPv4)
   - Non-responsive servers
   - Wrong ports or services

4. Fix the DNS configuration:
   - Use working public DNS servers
   - Google DNS: 8.8.8.8, 8.8.4.4
   - Cloudflare DNS: 1.1.1.1, 1.0.0.1
   - OpenDNS: 208.67.222.222, 208.67.220.220

5. Verify DNS resolution works:
   nslookup google.com

💡 HINTS:
• Valid IPv4 octets range from 0-255
• Always configure multiple DNS servers for redundancy
• Common public DNS servers are reliable for testing
• Use 'echo' or text editor to modify resolv.conf
• Test with multiple domains to ensure it's working

🏁 SUCCESS CRITERIA:
• At least 2 valid nameservers configured
• DNS queries successfully resolve
• No invalid IP addresses in configuration
• Test domains can be resolved

💡 TIP: Replace the invalid nameservers with working public DNS servers
"""
            
            return {
                "success": True,
                "connection_info": connection_info,
                "instructions": instructions,
                "config_file": str(self.resolv_conf)
            }
            
        except Exception as e:
            return {"success": False, "error": f"Failed to start scenario: {str(e)}"}
    
    def stop(self) -> bool:
        """Stop and cleanup the scenario"""
        try:
            # Clean up files
            for file_path in [self.resolv_conf, self.backup_resolv, self.test_domains_file]:
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
            files_exist = self.resolv_conf.exists()
            
            # Read current configuration
            current_config = ""
            if self.resolv_conf.exists():
                current_config = self.resolv_conf.read_text()
                # Count nameservers
                nameserver_lines = [l for l in current_config.split('\n') 
                                  if l.strip().startswith('nameserver')]
            
            details = f"""Scenario Status: {'Active' if files_exist else 'Not Running'}
Config File: {'✅' if self.resolv_conf.exists() else '❌'}
Backup File: {'✅' if self.backup_resolv.exists() else '❌'}
Nameservers Configured: {len(nameserver_lines) if files_exist else 0}"""
            
            return {"running": files_exist, "details": details}
        except Exception as e:
            return {"running": False, "details": f"Error: {str(e)}"}
    
    def check(self) -> Dict[str, Any]:
        """Check if DNS resolution has been fixed"""
        try:
            checks = []
            all_passed = True
            
            # Check if config file exists
            if not self.resolv_conf.exists():
                return {
                    "passed": False,
                    "feedback": "❌ DNS configuration file not found. Please start the scenario first."
                }
            
            # Read configuration
            config_content = self.resolv_conf.read_text()
            lines = config_content.split('\n')
            
            # Extract nameserver entries
            nameservers = []
            for line in lines:
                if line.strip().startswith('nameserver'):
                    parts = line.strip().split()
                    if len(parts) >= 2:
                        nameservers.append(parts[1])
            
            # Check: At least 2 nameservers configured
            checks.append(("At least 2 nameservers configured", len(nameservers) >= 2))
            if len(nameservers) < 2:
                all_passed = False
            
            # Check: No invalid IP addresses
            valid_dns_servers = [
                "8.8.8.8", "8.8.4.4",  # Google
                "1.1.1.1", "1.0.0.1",  # Cloudflare
                "208.67.222.222", "208.67.220.220",  # OpenDNS
                "9.9.9.9", "149.112.112.112",  # Quad9
                "4.2.2.1", "4.2.2.2"  # Level3
            ]
            
            invalid_ips = []
            valid_count = 0
            
            for ns in nameservers:
                # Check if IP is valid format
                try:
                    octets = ns.split('.')
                    if len(octets) == 4:
                        for octet in octets:
                            if not (0 <= int(octet) <= 255):
                                invalid_ips.append(ns)
                                break
                        else:
                            # Check if it's a known working DNS server
                            if ns in valid_dns_servers:
                                valid_count += 1
                            elif ns.startswith("127.") or ns.startswith("192.168.999"):
                                invalid_ips.append(ns)
                    else:
                        invalid_ips.append(ns)
                except (ValueError, AttributeError):
                    invalid_ips.append(ns)
            
            checks.append(("No invalid IP addresses", len(invalid_ips) == 0))
            if len(invalid_ips) > 0:
                all_passed = False
            
            checks.append(("At least one valid public DNS server", valid_count >= 1))
            if valid_count < 1:
                all_passed = False
            
            # Test actual DNS resolution (simulate)
            has_working_dns = valid_count >= 1 and len(invalid_ips) == 0
            checks.append(("DNS resolution would work", has_working_dns))
            if not has_working_dns:
                all_passed = False
            
            # Generate feedback
            feedback_lines = []
            for check_name, passed in checks:
                status = "✅ PASS" if passed else "❌ FAIL"
                feedback_lines.append(f"{status} {check_name}")
            
            if invalid_ips:
                feedback_lines.append(f"\n⚠️  Invalid nameservers found: {', '.join(invalid_ips)}")
            
            if all_passed:
                feedback_lines.append("\n🎉 Excellent! DNS resolution is now properly configured!")
                feedback_lines.append(f"✅ Valid DNS servers configured: {', '.join([ns for ns in nameservers if ns in valid_dns_servers])}")
            else:
                feedback_lines.append("\n💡 HINTS:")
                if len(nameservers) < 2:
                    feedback_lines.append("• Add at least 2 nameservers for redundancy")
                if invalid_ips:
                    feedback_lines.append("• Remove or fix invalid IP addresses")
                if valid_count < 1:
                    feedback_lines.append("• Use known public DNS servers (8.8.8.8, 1.1.1.1, etc.)")
            
            return {
                "passed": all_passed,
                "feedback": "\n".join(feedback_lines)
            }
                
        except Exception as e:
            return {"passed": False, "feedback": f"❌ Error checking solution: {str(e)}"}
    
    def reset(self) -> bool:
        """Reset scenario to broken state"""
        try:
            # Restore broken DNS configuration
            if self.resolv_conf.exists():
                broken_resolv_content = """# CloudDojo DNS Configuration
# WARNING: These DNS servers are misconfigured!

# Primary DNS - Invalid IP address
nameserver 192.168.999.1

# Secondary DNS - Non-existent server
nameserver 10.0.0.999

# Tertiary DNS - Local IP that's not a DNS server  
nameserver 127.0.0.53

# Domain search path (this part is fine)
search clouddojo.local corp.internal
options timeout:2 attempts:3
"""
                self.resolv_conf.write_text(broken_resolv_content)
            
            return True
        except Exception:
            return False

# Export scenario
scenario_class = DNSResolutionBrokenScenario