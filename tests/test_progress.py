#!/usr/bin/env python3
"""
Tests for CloudDojo progress tracking system
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from clouddojo.progress import ProgressTracker, UserStats, ScenarioProgress

class TestProgressTracker:
    """Test progress tracking functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = Path(tempfile.mkdtemp())
        # Mock the progress directory
        self.original_progress_dir = ProgressTracker.__init__
        
    def teardown_method(self):
        """Cleanup test environment"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_initial_stats(self):
        """Test initial user stats"""
        tracker = ProgressTracker()
        assert tracker.stats.level == 1
        assert tracker.stats.xp == 0
        assert tracker.stats.rank == "Digital Novice"
    
    def test_scenario_completion(self):
        """Test scenario completion tracking"""
        tracker = ProgressTracker()
        
        # Complete a scenario
        xp_earned = tracker.complete_scenario("test-scenario", time_taken=300, hints_used=0)
        
        assert xp_earned > 0
        assert tracker.stats.total_scenarios_completed == 1
        assert "test-scenario" in tracker.scenarios
        assert tracker.scenarios["test-scenario"].status == "completed"
    
    def test_xp_and_leveling(self):
        """Test XP awarding and level progression"""
        tracker = ProgressTracker()
        
        # Award enough XP to level up
        tracker._award_xp(150)
        
        assert tracker.stats.xp == 150
        assert tracker.stats.level == 2
    
    def test_achievements(self):
        """Test achievement unlocking"""
        tracker = ProgressTracker()
        
        # Complete first scenario to unlock "First Blood"
        tracker.complete_scenario("test-scenario", time_taken=300, hints_used=0)
        
        assert tracker.achievements["first_blood"].unlocked
        assert tracker.achievements["first_blood"].unlocked_at is not None
    
    def test_progress_summary(self):
        """Test progress summary generation"""
        tracker = ProgressTracker()
        tracker.complete_scenario("test-scenario", time_taken=300, hints_used=0)
        
        summary = tracker.get_progress_summary()
        
        assert summary["scenarios_completed"] == 1
        assert summary["stats"].level >= 1
        assert "xp_to_next_level" in summary