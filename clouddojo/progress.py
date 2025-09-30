#!/usr/bin/env python3
"""
CloudDojo Progress Tracking System
"""

import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class Achievement:
    """Represents an achievement/badge"""
    id: str
    name: str
    description: str
    icon: str
    unlocked: bool = False
    unlocked_at: Optional[str] = None

@dataclass
class ScenarioProgress:
    """Progress for a specific scenario"""
    name: str
    status: str  # "not_started", "in_progress", "completed", "mastered"
    attempts: int = 0
    completed_at: Optional[str] = None
    best_time: Optional[int] = None  # seconds
    hints_used: int = 0
    difficulty_rating: Optional[int] = None  # 1-5 stars
    start_time: Optional[float] = None  # timestamp when scenario was started

@dataclass
class UserStats:
    """User statistics and progress"""
    level: int = 1
    xp: int = 0
    total_scenarios_completed: int = 0
    total_time_spent: int = 0  # seconds
    streak_days: int = 0
    last_activity: Optional[str] = None
    rank: str = "Digital Novice"

class ProgressTracker:
    """Manages user progress, achievements, and statistics"""
    
    def __init__(self):
        self.progress_dir = Path.home() / '.clouddojo'
        self.progress_dir.mkdir(exist_ok=True)
        self.progress_file = self.progress_dir / 'progress.json'
        self.stats = UserStats()
        self.scenarios: Dict[str, ScenarioProgress] = {}
        self.achievements: Dict[str, Achievement] = {}
        self._init_achievements()
        self._load_progress()
    
    def _init_achievements(self):
        """Initialize available achievements"""
        achievements_data = [
            ("first_blood", "First Blood", "Complete your first scenario", "🩸"),
            ("speed_demon", "Speed Demon", "Complete a scenario in under 5 minutes", "⚡"),
            ("perfectionist", "Perfectionist", "Complete a scenario without using hints", "💎"),
            ("persistent", "Persistent", "Complete a scenario after 5+ attempts", "🔥"),
            ("streak_master", "Streak Master", "Maintain a 7-day learning streak", "🌟"),
            ("scenario_hunter", "Scenario Hunter", "Complete 10 different scenarios", "🎯"),
            ("digital_samurai", "Digital Samurai", "Reach level 10", "⚔️"),
            ("mentor", "Mentor", "Rate 5 scenarios to help others", "🧙"),
        ]
        
        for aid, name, desc, icon in achievements_data:
            self.achievements[aid] = Achievement(aid, name, desc, icon)
    
    def _load_progress(self):
        """Load progress from disk"""
        if self.progress_file.exists():
            try:
                with open(self.progress_file, 'r') as f:
                    data = json.load(f)
                
                # Load stats
                if 'stats' in data:
                    self.stats = UserStats(**data['stats'])
                
                # Load scenarios
                if 'scenarios' in data:
                    for name, scenario_data in data['scenarios'].items():
                        self.scenarios[name] = ScenarioProgress(**scenario_data)
                
                # Load achievements
                if 'achievements' in data:
                    for aid, achievement_data in data['achievements'].items():
                        if aid in self.achievements:
                            self.achievements[aid] = Achievement(**achievement_data)
            
            except Exception as e:
                # If loading fails, start fresh
                pass
    
    def _save_progress(self):
        """Save progress to disk"""
        data = {
            'stats': asdict(self.stats),
            'scenarios': {name: asdict(scenario) for name, scenario in self.scenarios.items()},
            'achievements': {aid: asdict(achievement) for aid, achievement in self.achievements.items()},
            'last_updated': datetime.now().isoformat()
        }
        
        with open(self.progress_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def start_scenario(self, scenario_name: str):
        """Mark scenario as started"""
        current_time = time.time()
        
        if scenario_name not in self.scenarios:
            self.scenarios[scenario_name] = ScenarioProgress(scenario_name, "in_progress", start_time=current_time)
        else:
            self.scenarios[scenario_name].status = "in_progress"
            self.scenarios[scenario_name].attempts += 1
            self.scenarios[scenario_name].start_time = current_time
        
        self._update_activity()
        self._save_progress()
    
    def complete_scenario(self, scenario_name: str, time_taken: int = 0, hints_used: int = 0):
        """Mark scenario as completed and award XP"""
        if scenario_name not in self.scenarios:
            self.scenarios[scenario_name] = ScenarioProgress(scenario_name, "completed")
        
        scenario = self.scenarios[scenario_name]
        scenario.status = "completed"
        scenario.completed_at = datetime.now().isoformat()
        scenario.hints_used = hints_used
        
        # Update best time
        if time_taken > 0:
            if scenario.best_time is None or time_taken < scenario.best_time:
                scenario.best_time = time_taken
        
        # Award XP based on performance
        base_xp = 100
        bonus_xp = 0
        
        # Time bonus (if under 10 minutes)
        if time_taken > 0 and time_taken < 600:
            bonus_xp += 50
        
        # No hints bonus
        if hints_used == 0:
            bonus_xp += 30
        
        # First completion bonus
        if scenario.attempts == 1:
            bonus_xp += 20
        
        total_xp = base_xp + bonus_xp
        self._award_xp(total_xp)
        
        # Update stats
        self.stats.total_scenarios_completed += 1
        self.stats.total_time_spent += time_taken
        
        # Check for achievements
        self._check_achievements(scenario_name, time_taken, hints_used)
        
        self._update_activity()
        self._save_progress()
        
        return total_xp
    
    def _award_xp(self, xp: int):
        """Award XP and handle level ups"""
        old_level = self.stats.level
        self.stats.xp += xp
        
        # Level calculation: 100 XP for level 1, +50 XP per level
        new_level = 1
        total_xp_needed = 0
        while total_xp_needed <= self.stats.xp:
            total_xp_needed += 100 + (new_level - 1) * 50
            if total_xp_needed <= self.stats.xp:
                new_level += 1
        
        self.stats.level = new_level
        
        # Update rank based on level
        ranks = [
            (1, "Digital Novice"),
            (3, "Code Apprentice"), 
            (5, "System Warrior"),
            (8, "Debug Master"),
            (12, "DevOps Ninja"),
            (15, "Cloud Samurai"),
            (20, "Digital Sensei")
        ]
        
        for level_req, rank in reversed(ranks):
            if self.stats.level >= level_req:
                self.stats.rank = rank
                break
        
        return new_level > old_level  # Return True if leveled up
    
    def _check_achievements(self, scenario_name: str, time_taken: int, hints_used: int):
        """Check and unlock achievements"""
        newly_unlocked = []
        
        # First Blood
        if not self.achievements["first_blood"].unlocked and self.stats.total_scenarios_completed == 1:
            self._unlock_achievement("first_blood")
            newly_unlocked.append("first_blood")
        
        # Speed Demon
        if not self.achievements["speed_demon"].unlocked and time_taken > 0 and time_taken < 300:
            self._unlock_achievement("speed_demon")
            newly_unlocked.append("speed_demon")
        
        # Perfectionist
        if not self.achievements["perfectionist"].unlocked and hints_used == 0:
            self._unlock_achievement("perfectionist")
            newly_unlocked.append("perfectionist")
        
        # Persistent
        scenario = self.scenarios[scenario_name]
        if not self.achievements["persistent"].unlocked and scenario.attempts >= 5:
            self._unlock_achievement("persistent")
            newly_unlocked.append("persistent")
        
        # Scenario Hunter
        if not self.achievements["scenario_hunter"].unlocked and self.stats.total_scenarios_completed >= 10:
            self._unlock_achievement("scenario_hunter")
            newly_unlocked.append("scenario_hunter")
        
        # Digital Samurai
        if not self.achievements["digital_samurai"].unlocked and self.stats.level >= 10:
            self._unlock_achievement("digital_samurai")
            newly_unlocked.append("digital_samurai")
        
        return newly_unlocked
    
    def _unlock_achievement(self, achievement_id: str):
        """Unlock an achievement"""
        if achievement_id in self.achievements:
            self.achievements[achievement_id].unlocked = True
            self.achievements[achievement_id].unlocked_at = datetime.now().isoformat()
    
    def _update_activity(self):
        """Update last activity and streak"""
        now = datetime.now()
        today = now.date()
        
        if self.stats.last_activity:
            last_date = datetime.fromisoformat(self.stats.last_activity).date()
            days_diff = (today - last_date).days
            
            if days_diff == 1:
                # Consecutive day
                self.stats.streak_days += 1
            elif days_diff > 1:
                # Streak broken
                self.stats.streak_days = 1
            # Same day, no change to streak
        else:
            # First activity
            self.stats.streak_days = 1
        
        self.stats.last_activity = now.isoformat()
        
        # Check streak achievement
        if not self.achievements["streak_master"].unlocked and self.stats.streak_days >= 7:
            self._unlock_achievement("streak_master")
    
    def get_progress_summary(self) -> Dict[str, Any]:
        """Get a summary of user progress"""
        completed_scenarios = [s for s in self.scenarios.values() if s.status == "completed"]
        unlocked_achievements = [a for a in self.achievements.values() if a.unlocked]
        
        # Calculate XP needed for next level
        current_level_xp = sum(100 + i * 50 for i in range(self.stats.level - 1))
        next_level_xp = current_level_xp + 100 + (self.stats.level - 1) * 50
        xp_to_next = next_level_xp - self.stats.xp
        
        return {
            'stats': self.stats,
            'scenarios_completed': len(completed_scenarios),
            'total_scenarios': len(self.scenarios),
            'achievements_unlocked': len(unlocked_achievements),
            'total_achievements': len(self.achievements),
            'xp_to_next_level': xp_to_next,
            'completion_rate': len(completed_scenarios) / max(len(self.scenarios), 1) * 100
        }
    
    def get_leaderboard_data(self) -> Dict[str, Any]:
        """Get data for leaderboard display"""
        return {
            'level': self.stats.level,
            'xp': self.stats.xp,
            'rank': self.stats.rank,
            'scenarios_completed': self.stats.total_scenarios_completed,
            'streak': self.stats.streak_days
        }
    
    def rate_scenario(self, scenario_name: str, rating: int):
        """Rate a scenario (1-5 stars)"""
        if scenario_name in self.scenarios:
            self.scenarios[scenario_name].difficulty_rating = rating
            self._save_progress()
            
            # Check mentor achievement
            rated_scenarios = sum(1 for s in self.scenarios.values() if s.difficulty_rating is not None)
            if not self.achievements["mentor"].unlocked and rated_scenarios >= 5:
                self._unlock_achievement("mentor")
                self._save_progress()