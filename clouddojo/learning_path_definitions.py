#!/usr/bin/env python3
"""
Learning Path Definitions - Export learning path classes
"""

from clouddojo.default_learning_paths import (
    DockerBasicsPath,
    K8sEssentialsPath,
    ProductionSREPath
)

# Export learning path classes for registration
LEARNING_PATH_CLASSES = [
    DockerBasicsPath,
    K8sEssentialsPath,
    ProductionSREPath
]