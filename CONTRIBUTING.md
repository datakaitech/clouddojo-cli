# Contributing to CloudDojo

Welcome! CloudDojo makes it super easy to contribute new troubleshooting scenarios. This guide will get you started in 5 minutes.

## 🚀 Quick Start

### 1. Set Up Your Environment
```bash
# Clone your fork
git clone https://github.com/datakaitech/clouddojo-cli.git
cd clouddojo-cli

# Install dependencies
python -m venv venv 
pip install -e . 
pip install -r requirements.txt

# Test the setup
python tests/test_scenarios.py
```

### 2. Create Your Scenario
```bash
# Create scenario directory
mkdir clouddojo/scenarios/my-awesome-scenario

# Copy the template
cp scenario_template.py clouddojo/scenarios/my-awesome-scenario/__init__.py
```

### 3. Implement Your Scenario
Edit `clouddojo/scenarios/my-awesome-scenario/__init__.py`:

1. **Replace class names**: `MyScenario` → `MyAwesomeScenario`
2. **Update metadata**: Company story, hints, learning path
3. **Implement methods**: `start()`, `stop()`, `check()`, `reset()`
4. **Set properties**: `description`, `difficulty`, `technologies`

### 4. Test Your Implementation
```bash
# Run automated tests
python tests/test_scenarios.py

# Should show:
# Testing: my-awesome-scenario
#   PASS

# Test in the dojo
clouddojo dojo
# Navigate to: Scenario Management → Start → my-awesome-scenario
```

### 5. Submit Your Contribution
```bash
git add .
git commit -m "Add my-awesome-scenario: Redis connection troubleshooting"
git push origin feature/my-awesome-scenario
# Create pull request on GitHub
```

## 📋 Scenario Requirements

### Required Implementation
- ✅ Inherit from `BaseScenario`
- ✅ Implement all abstract methods
- ✅ Export `scenario_class` variable
- ✅ Valid difficulty: `"beginner"`, `"intermediate"`, or `"advanced"`

### Recommended Features
- ✅ Create `ScenarioMetadata` class with story context
- ✅ Provide 4 progressive hints
- ✅ Assign to learning path: `"docker-basics"`, `"k8s-essentials"`, or `"production-sre"`
- ✅ Include business context and completion story

## 🎯 Scenario Ideas

### Beginner (Docker Basics)
- Redis connection refused
- PostgreSQL authentication failure
- Apache virtual host misconfiguration
- File permission issues

### Intermediate (Kubernetes)
- Pod OOMKilled errors
- ConfigMap mounting issues
- Service discovery failures
- Ingress routing problems

### Advanced (Production SRE)
- Log rotation failures
- Cron job syntax errors
- Process management issues
- Performance bottlenecks

## 🔧 Implementation Patterns

### Docker-Based Scenarios
```python
import docker

class MyDockerScenario(BaseScenario):
    def __init__(self, name: str):
        super().__init__(name)
        self.docker_client = docker.from_env()
        self.container_name = f"clouddojo-{name}"
    
    def start(self):
        # Build and run container with broken config
        container = self.docker_client.containers.run(
            "my-image:broken",
            name=self.container_name,
            detach=True,
            ports={'80/tcp': None}
        )
        return {"success": True, "connection_info": f"Container: {self.container_name}"}
```

### Kubernetes-Based Scenarios
```python
from clouddojo.k8s_base_scenario import K8sBaseScenario

class MyK8sScenario(K8sBaseScenario):
    def get_manifest_path(self):
        return self.manifests_dir / "broken-deployment.yaml"
    
    def start(self):
        result = self.apply_manifest()
        return result
```

### System-Based Scenarios
```python
import subprocess
from pathlib import Path

class MySystemScenario(BaseScenario):
    def start(self):
        # Create broken configuration
        config_file = Path("/tmp/broken.conf")
        config_file.write_text("invalid syntax here")
        return {"success": True, "connection_info": f"Config: {config_file}"}
```

## 🧪 Testing Guidelines

### Automated Tests Check
- Class inheritance from `BaseScenario`
- All required methods implemented
- Valid properties and metadata
- Learning path assignment
- Instantiation without errors

### Manual Testing Checklist
- [ ] Scenario starts successfully
- [ ] Instructions are clear and actionable
- [ ] Check method validates solution correctly
- [ ] Reset returns to broken state
- [ ] Completion story appears when solved
- [ ] Hints are progressive and helpful

## 📝 Code Style

### Naming Conventions
- **Scenario class**: `MyScenarioName` (PascalCase)
- **Metadata class**: `MyScenarioNameMetadata`
- **File name**: `my-scenario-name` (kebab-case)
- **Directory**: `clouddojo/scenarios/my-scenario-name/`

### Documentation
- Include docstrings for classes and methods
- Add comments for complex logic
- Provide clear error messages
- Use descriptive variable names

## 🏷️ Pull Request Guidelines

### PR Title Format
```
Add [scenario-name]: [Brief description]

Examples:
- Add redis-connection-failure: Redis server connection troubleshooting
- Add k8s-pvc-mounting: Kubernetes PVC mounting issues
- Add nginx-ssl-config: Nginx SSL certificate configuration errors
```

### PR Description Template
```markdown
## Scenario Overview
- **Name**: my-scenario-name
- **Difficulty**: beginner/intermediate/advanced
- **Learning Path**: docker-basics/k8s-essentials/production-sre
- **Technologies**: [list technologies]

## What's Broken
Brief description of the problem users will troubleshoot.

## Solution Summary
Brief description of how to fix the issue.

## Testing
- [ ] Automated tests pass (`python tests/test_scenarios.py`)
- [ ] Manual testing completed in dojo
- [ ] All hints tested and working
- [ ] Completion story verified

## Additional Notes
Any special setup requirements or considerations.
```

### Review Checklist
- [ ] Tests pass
- [ ] Scenario works in dojo interface
- [ ] Story context is engaging
- [ ] Hints are progressive (gentle → specific → detailed → solution)
- [ ] Learning objectives are clear
- [ ] Code follows style guidelines

## 🆘 Getting Help

- **Questions**: Open an issue with the `question` label
- **Bug Reports**: Open an issue with the `bug` label
- **Feature Requests**: Open an issue with the `enhancement` label
- **Discussion**: Use GitHub Discussions

## 🎉 Recognition

Contributors will be:
- Listed in the project README
- Credited in scenario metadata
- Invited to join the maintainer team (for significant contributions)

Thank you for helping make DevOps troubleshooting more accessible and engaging! 🚀