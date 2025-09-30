#!/usr/bin/env python3
"""
CloudDojo Storytelling System - Add narrative context to scenarios
"""

from typing import Dict, List, Optional
from enum import Enum
from dataclasses import dataclass
from clouddojo.metadata_registry import registry

class CompanyType(Enum):
    STARTUP = "startup"
    ENTERPRISE = "enterprise" 
    ECOMMERCE = "ecommerce"
    FINTECH = "fintech"
    GAMING = "gaming"
    HEALTHCARE = "healthcare"

@dataclass
class StoryContext:
    """Narrative context for a scenario"""
    company_name: str
    company_type: CompanyType
    your_role: str
    situation: str
    urgency: str  # low, medium, high, critical
    stakeholders: List[str]
    business_impact: str
    success_criteria: str

class StorytellingManager:
    """Manages narrative contexts for scenarios using metadata registry"""
    
    def __init__(self):
        pass  # No longer need hardcoded stories
    
    # Removed hardcoded stories - now using registry
    
    def get_story(self, scenario_name: str):
        """Get story context for a scenario"""
        return registry.get_story_context(scenario_name)
    
    def format_story_intro(self, scenario_name: str) -> str:
        """Format story introduction for display"""
        story = self.get_story(scenario_name)
        if not story:
            return f"Debug the {scenario_name} scenario"
        
        urgency_colors = {
            "low": "bright_green",
            "medium": "bright_yellow", 
            "high": "bright_red",
            "critical": "bold bright_red"
        }
        
        urgency_icons = {
            "low": "🟢",
            "medium": "🟡",
            "high": "🔴", 
            "critical": "🚨"
        }
        
        company_icons = {
            CompanyType.STARTUP: "🚀",
            CompanyType.ENTERPRISE: "🏢",
            CompanyType.ECOMMERCE: "🛒",
            CompanyType.FINTECH: "💰",
            CompanyType.GAMING: "🎮",
            CompanyType.HEALTHCARE: "🏥"
        }
        
        intro = f"""
[bold bright_cyan]📖 MISSION BRIEFING 📖[/bold bright_cyan]

{company_icons.get(story.company_type, '🏢')} [bold]{story.company_name}[/bold] ({story.company_type.value.title()})
👤 [bold]Your Role:[/bold] {story.your_role}

🎯 [bold]SITUATION:[/bold]
{story.situation}

{urgency_icons.get(story.urgency, '🔴')} [bold {urgency_colors.get(story.urgency, 'white')}]URGENCY: {story.urgency.upper()}[/bold {urgency_colors.get(story.urgency, 'white')}]

👥 [bold]Stakeholders Watching:[/bold]
{', '.join(story.stakeholders)}

💼 [bold]Business Impact:[/bold]
{story.business_impact}

✅ [bold]Success Criteria:[/bold]
{story.success_criteria}

[dim bright_cyan]"Every incident is a chance to prove your worth as a digital warrior!"[/dim bright_cyan]
        """
        
        return intro.strip()
    
    def format_completion_story(self, scenario_name: str, time_taken: int) -> str:
        """Format story conclusion after scenario completion"""
        completion_story = registry.get_completion_story(scenario_name, time_taken)
        if completion_story:
            return completion_story
        
        time_str = f"{time_taken // 60}m {time_taken % 60}s" if time_taken > 0 else "record time"
        return f"Mission accomplished in {time_str}! Your debugging skills saved the day."
    
    def add_story(self, scenario_name: str, story):
        """Add a new story context (deprecated - use scenario metadata)"""
        pass  # Stories now come from scenario metadata