# Testing Framework

## 🚀 Quick Start

```bash
# Test all scenarios
python tests/test_scenarios.py

# Expected output:
# Testing: my-scenario
#   PASS
```

## 🧪 What Gets Tested

### ✅ Required Implementation
- Inherits from `BaseScenario` (or `K8sBaseScenario`)
- Implements all abstract methods: `start()`, `stop()`, `status()`, `check()`, `reset()`
- Has valid properties: `description`, `difficulty`, `technologies`
- Exports `scenario_class` variable
- Can be instantiated without errors

### ✅ Kubernetes Scenarios (Additional)
- Implements `get_manifest_path()`, `get_resource_name()`, `get_resource_type()`

### ✅ Optional Features
- Implements `ScenarioMetadata` with story context
- Provides progressive hints
- Assigns to valid learning path
- Includes completion story

## 📊 Test Results

- **PASS** - Scenario properly implemented
- **FAIL** - Missing required methods or invalid configuration  
- **WARNING** - Optional features missing (metadata, learning path)

## 🔧 Common Failures

| Error | Fix |
|-------|-----|
| `Missing 'scenario_class' export` | Add `scenario_class = MyScenario` at end of file |
| `Invalid difficulty 'easy'` | Use: `"beginner"`, `"intermediate"`, `"advanced"` |
| `Docker not running` | Expected for Docker scenarios in test environment |
| `Method 'check' not implemented` | Implement all required abstract methods |

## 🧪 Manual Testing

After automated tests pass:

1. **Start scenario**: `clouddojo dojo` → Scenario Management → Start
2. **Follow instructions**: Verify they're clear and actionable
3. **Test check function**: Should fail initially, pass after fixing
4. **Test reset**: Should return to broken state
5. **Test hints**: Progressive and helpful

## 🐛 Debugging

```python
# Test single scenario
from tests.test_scenarios import ScenarioTester
tester = ScenarioTester()
scenarios = tester._discover_scenarios()
tester._test_scenario("my-scenario", scenarios["my-scenario"])
```

## 📝 Test Environment Notes

- **Docker scenarios**: Will fail without Docker running (expected)
- **Kubernetes scenarios**: Will fail without kubectl configured (expected)
- **System scenarios**: Should pass in most environments
- **File operations**: Use `/tmp/` for temporary files

The testing framework ensures all scenarios follow the required patterns and work correctly before contribution.