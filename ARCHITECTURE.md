# CloudDojo Architecture

## 📁 Project Structure

```
clouddojo-cli/
├── clouddojo/                    # Main package
│   ├── scenarios/               # Scenario implementations
│   ├── cli.py                   # Main CLI interface
│   ├── base_scenario.py         # Base class for scenarios
│   ├── k8s_base_scenario.py     # Kubernetes scenario base
│   ├── progress.py              # Progress tracking & gamification
│   ├── learning_paths.py        # Learning path management
│   └── ...                      # Other core modules
├── tests/                       # Test suite
├── .github/                     # GitHub templates & workflows
├── CONTRIBUTING.md              # Contribution guide
├── scenario_template.py         # Template for new scenarios
└── README.md                    # Project overview
```

## 🧩 Core Components

### CLI Interface (`cli.py`)
- **Purpose**: Main user interface using Rich library
- **Features**: Interactive menus, progress display, scenario management
- **Key Classes**: `InteractiveDojo`, `ScenarioManager`

### Scenario System
- **Base Classes**: `BaseScenario`, `K8sBaseScenario`
- **Purpose**: Abstract framework for troubleshooting scenarios
- **Location**: `clouddojo/scenarios/*/`

### Progress System (`progress.py`)
- **Purpose**: Gamification, XP tracking, achievements
- **Storage**: `~/.clouddojo/progress.json`
- **Features**: Levels, streaks, completion tracking

### Learning Paths (`learning_paths.py`)
- **Purpose**: Structured progression through scenarios
- **Types**: Docker Basics, Kubernetes Essentials, Production SRE
- **Features**: Prerequisites, progress calculation

### Metadata Registry (`metadata_registry.py`)
- **Purpose**: Dynamic discovery of scenarios and learning paths
- **Features**: Story contexts, hints, completion stories

## 🎯 Scenario Architecture

### Base Scenario Structure
```python
class MyScenario(BaseScenario):
    # Required methods
    def start(self) -> Dict[str, Any]      # Setup broken environment
    def stop(self) -> bool                 # Cleanup resources
    def status(self) -> Dict[str, Any]     # Check if running
    def check(self) -> Dict[str, Any]      # Validate solution
    def reset(self) -> bool                # Return to broken state
    
    # Required properties
    @property
    def description(self) -> str           # What's broken
    def difficulty(self) -> str            # beginner/intermediate/advanced
    def technologies(self) -> list         # [docker, nginx, etc]
```

### Kubernetes Scenarios
```python
class MyK8sScenario(K8sBaseScenario):
    # Additional required methods
    def get_manifest_path(self) -> Path    # Path to K8s manifest
    def get_resource_name(self) -> str     # Main resource name
    def get_resource_type(self) -> str     # Resource type (pod, etc)
    
    # Built-in helpers
    def apply_manifest(self)               # kubectl apply
    def delete_manifest(self)              # kubectl delete
```

### Scenario Metadata
```python
class MyScenarioMetadata(ScenarioMetadata):
    def get_story_context(self) -> StoryContext    # Business context
    def get_hints(self) -> List[Hint]              # Progressive hints
    def get_learning_path(self) -> str             # Path assignment
    def get_completion_story(self, time) -> str    # Success story
```

## 🔄 Data Flow

### Scenario Lifecycle
1. **Discovery**: CLI scans `scenarios/` directory
2. **Registration**: Metadata registered with registry
3. **Start**: User selects scenario, `start()` called
4. **Interaction**: User troubleshoots, uses hints
5. **Validation**: `check()` validates solution
6. **Completion**: Progress tracked, XP awarded
7. **Cleanup**: `stop()` cleans up resources

### Progress Tracking
1. **Start**: `tracker.start_scenario(name)`
2. **Hints**: Track hint usage
3. **Completion**: `tracker.complete_scenario(name, time, hints)`
4. **Storage**: Save to `~/.clouddojo/progress.json`

## 🧪 Testing Architecture

### Test Framework (`tests/test_scenarios.py`)
- **Purpose**: Validate scenario implementations
- **Checks**: Inheritance, methods, properties, metadata
- **Usage**: `python tests/test_scenarios.py`

### Test Categories
- **Inheritance**: Proper base class usage
- **Methods**: All required methods implemented
- **Properties**: Valid difficulty, technologies
- **Metadata**: Story context, hints structure
- **Instantiation**: Can create scenario objects

## 📦 Package Structure

### Core Modules
- `cli.py` - Main interface
- `base_scenario.py` - Scenario framework
- `progress.py` - Gamification system
- `learning_paths.py` - Path management
- `metadata_registry.py` - Dynamic discovery

### Supporting Modules
- `storytelling.py` - Narrative formatting
- `hints.py` - Hint management
- `setup.py` - Prerequisite installation
- `ascii_art.py` - Visual elements

### Configuration
- `learning_path_definitions.py` - Path exports
- `default_learning_paths.py` - Default paths
- `scenario_metadata.py` - Metadata framework

## 🔌 Extension Points

### Adding New Scenarios
1. Create directory: `clouddojo/scenarios/my-scenario/`
2. Implement: `__init__.py` with scenario class
3. Export: `scenario_class = MyScenario`
4. Test: `python tests/test_scenarios.py`

### Adding New Learning Paths
1. Create class inheriting `LearningPathMetadata`
2. Add to `learning_path_definitions.py`
3. Assign scenarios to path via metadata

### Adding New Base Classes
1. Inherit from `BaseScenario`
2. Add technology-specific helpers
3. Update test framework for validation

## 🚀 Deployment

### Package Distribution
- **PyPI**: `pip install clouddojo`
- **Entry Point**: `clouddojo` command
- **Dependencies**: Listed in `requirements.txt`

### Local Development
```bash
pip install -e .              # Editable install
python -m clouddojo.cli       # Direct module execution
python tests/test_scenarios.py # Run tests
```

## 🔒 Security Considerations

### Scenario Isolation
- Scenarios run in user context (not root)
- Docker containers use non-privileged users
- Temporary files in `/tmp/` with unique names

### Input Validation
- Scenario names validated against directory traversal
- User inputs sanitized in CLI
- File operations use Path objects for safety

### Resource Management
- Containers auto-removed on scenario stop
- Temporary files cleaned up
- Process management for system scenarios

## 📈 Performance

### Startup Optimization
- Lazy loading of scenarios
- Cached metadata registry
- Minimal imports in CLI

### Resource Usage
- Docker containers use minimal base images
- Kubernetes scenarios use lightweight manifests
- Progress data stored locally (no network calls)

### Scalability
- Modular scenario architecture
- Plugin-based learning paths
- Stateless scenario execution

This architecture supports easy extension while maintaining clean separation of concerns and robust testing.