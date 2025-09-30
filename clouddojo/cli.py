#!/usr/bin/env python3
"""
CloudDojo CLI - A modular troubleshooting platform for DevOps/SRE
"""

import os
import sys
import json
import time
import click
import random
import importlib.util
from pathlib import Path
from typing import Dict, Any, Optional
from rich.console import Console

# Fix Windows encoding issues
if sys.platform == "win32":
    os.environ["PYTHONIOENCODING"] = "utf-8"
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.live import Live
from rich.layout import Layout
from rich.align import Align
from rich.columns import Columns
from rich.prompt import Confirm, Prompt
from rich.syntax import Syntax
from rich.tree import Tree
from rich.rule import Rule
from rich.box import ROUNDED, DOUBLE, HEAVY
from rich import box
import subprocess
import platform

from clouddojo.base_scenario import BaseScenario
from clouddojo.metadata_registry import registry
from clouddojo.progress import ProgressTracker
from clouddojo.hints import HintsManager
from clouddojo.learning_paths import LearningPathManager, PathStatus
from clouddojo.storytelling import StorytellingManager
from clouddojo.setup import SetupManager
from clouddojo.learning_path_definitions import LEARNING_PATH_CLASSES
from clouddojo.ascii_art import get_banner, get_small_banner, get_divider


# Create console with proper encoding for Windows
try:
    console = Console(stderr=True, force_terminal=True)
except:
    console = Console(stderr=True)
    
tracker = ProgressTracker()
hints_manager = HintsManager()
learning_paths = LearningPathManager()
storyteller = StorytellingManager()
setup_manager = SetupManager()

# Register learning paths
for path_class in LEARNING_PATH_CLASSES:
    registry.register_learning_path(path_class())



class ScenarioManager:
    """Manages scenario loading and execution"""
    
    def __init__(self):
        self.console = Console(stderr=True)
        self.scenarios_dir = Path(__file__).parent / 'scenarios'
        self.scenarios_dir.mkdir(exist_ok=True)
        self._scenarios = {}
        self._load_scenarios()
    
    def _load_scenarios(self):
        """Load scenarios with progress"""
        try:
            scenario_dirs = [d for d in self.scenarios_dir.iterdir() 
                            if d.is_dir() and (d / '__init__.py').exists()]
            
            if not scenario_dirs:
                return
            
            self.console.print("[bold cyan]Loading scenarios...[/bold cyan]")
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(bar_width=40),
                TaskProgressColumn(),
                console=self.console,
            ) as progress:
                task = progress.add_task("Loading scenarios...", total=len(scenario_dirs))
                
                for scenario_dir in scenario_dirs:
                    try:
                        spec = importlib.util.spec_from_file_location(
                            f"scenarios.{scenario_dir.name}",
                            scenario_dir / '__init__.py'
                        )
                        if spec is None:
                            continue
                            
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                        
                        if hasattr(module, 'scenario_class'):
                            scenario_name = scenario_dir.name
                            self._scenarios[scenario_name] = module.scenario_class
                            
                            # Register scenario metadata
                            scenario_instance = module.scenario_class(scenario_name)
                            registry.register_scenario(scenario_name, scenario_instance)
                            
                            progress.update(task, description=f"Loaded: {scenario_name}")
                        
                        progress.advance(task)
                        time.sleep(0.1)
                        
                    except Exception as e:
                        self.console.print(f"[red]Failed to load {scenario_dir.name}: {e}[/red]")
                        progress.advance(task)
        except Exception as e:
            self.console.print(f"[red]Error loading scenarios: {e}[/red]")
    
    def get_scenario(self, name: str) -> Optional[BaseScenario]:
        if name in self._scenarios:
            return self._scenarios[name](name)
        return None
    
    def list_scenarios(self) -> Dict[str, BaseScenario]:
        return {name: cls(name) for name, cls in self._scenarios.items()}

class InteractiveDojo:
    """Interactive interface for scenario management"""
    
    def __init__(self):
        self.console = Console()
        self.manager = ScenarioManager()
        self.running = True

    
    def show_main_menu(self):
        """Display the main dojo menu"""
        self.console.clear()
        
        # Show small banner for dojo menu
        self.console.print(get_small_banner())
        
        # Get user progress for personalized greeting
        progress_summary = tracker.get_progress_summary()
        greeting = f"Welcome, {progress_summary['stats'].rank}"
        
        menu_panel = Panel(
            f"[bold cyan]{greeting}[/bold cyan]\n"
            f"[dim]Level {progress_summary['stats'].level} | {progress_summary['stats'].xp} XP | {progress_summary['stats'].streak_days} day streak[/dim]\n\n"
            "Select an option:\n\n"
            "[green]1.[/green] Learning Paths (Recommended)\n"
            "[green]2.[/green] Browse Scenarios (Grouped by Tech)\n"
            "[green]3.[/green] View Progress & Achievements\n"
            "[green]4.[/green] Scenario Management\n"
            "[green]5.[/green] Status\n"
            "[green]6.[/green] Exit\n\n"
            "[dim]💡 Tip: Use a separate terminal for troubleshooting commands[/dim]",
            title="CloudDojo",
            border_style="cyan",
            box=ROUNDED
        )
        
        self.console.print(menu_panel)
    
    def browse_scenarios(self):
        """Browse available training scenarios grouped by technology"""
        scenarios = self.manager.list_scenarios()
        
        if not scenarios:
            self.console.print(Panel(
                "[yellow]No scenarios found[/yellow]\n\n"
                "[dim]Add scenarios to get started.[/dim]",
                title="No Scenarios",
                border_style="yellow"
            ))
            input("\nPress Enter to return to main menu...")
            return
        
        # Group scenarios by technology (optimized)
        tech_keywords = {
            "⚓ Kubernetes": {'k8s', 'kubernetes'},
            "🐋 Container & Docker": {'nginx', 'docker'},
            "🐧 Linux & System Admin": {'process', 'cron', 'file', 'permission'}
        }
        
        tech_groups = {
            "🐋 Container & Docker": [],
            "⚓ Kubernetes": [],
            "🐧 Linux & System Admin": [],
            "🌐 Networking & Services": []
        }
        
        for name, scenario in scenarios.items():
            name_lower = name.lower()
            assigned = False
            
            for group_name, keywords in tech_keywords.items():
                if any(keyword in name_lower for keyword in keywords):
                    tech_groups[group_name].append((name, scenario))
                    assigned = True
                    break
            
            if not assigned:
                tech_groups["🌐 Networking & Services"].append((name, scenario))
        
        self.console.print("\n[bold cyan]Training Scenarios by Technology[/bold cyan]\n")
        
        for group_name, group_scenarios in tech_groups.items():
            if not group_scenarios:
                continue
                
            self.console.print(f"\n[bold bright_magenta]{group_name}[/bold bright_magenta]")
            
            table = Table(
                show_header=True,
                header_style="bold cyan",
                box=ROUNDED,
                border_style="dim"
            )
            table.add_column("🎯 Scenario", style="bright_cyan", width=25)
            table.add_column("📜 Description", style="white", width=45)
            table.add_column("⭐ Level", justify="center", width=12)
            
            for name, scenario in group_scenarios:
                difficulty_colors = {
                    "beginner": "bright_green",
                    "intermediate": "bright_yellow", 
                    "advanced": "bright_red"
                }
                
                # Show completion status
                completed = name in [s for s, p in tracker.scenarios.items() if p.status == "completed"]
                status_icon = "✅" if completed else "🎯"
                
                table.add_row(
                    f"{status_icon} {name}",
                    scenario.description,
                    f"[{difficulty_colors.get(scenario.difficulty, 'white')}]{scenario.difficulty}[/{difficulty_colors.get(scenario.difficulty, 'white')}]"
                )
            
            self.console.print(table)
        
        input("\nPress Enter to return to main menu...")
    
    def show_learning_paths(self):
        """Display structured learning paths"""
        completed_scenarios = [name for name, progress in tracker.scenarios.items() if progress.status == "completed"]
        available_paths = learning_paths.get_available_paths(completed_scenarios)
        
        self.console.print("\n🎯 [bold bright_cyan]Learning Paths - Your Journey to Mastery[/bold bright_cyan] 🎯\n")
        
        # Show recommendation first
        recommendation = learning_paths.get_recommended_next_step(completed_scenarios)
        if recommendation:
            rec_panel = Panel(
                f"[bold bright_green]🌟 Recommended Next Step:[/bold bright_green]\n\n"
                f"{recommendation['message']}\n"
                f"Path: {recommendation['path']['name']}\n"
                f"Next Scenario: {recommendation.get('next_scenario', 'N/A')}",
                title="🎯 Your Next Challenge",
                border_style="bright_green"
            )
            self.console.print(rec_panel)
            self.console.print()
        
        # Display all paths
        for path_id in registry.get_learning_paths():
            path = learning_paths.get_path(path_id)
            if not path:
                continue
                
            progress_info = learning_paths.get_path_progress(path_id, completed_scenarios)
            status = progress_info.get('status', PathStatus.LOCKED)
            
            # Status styling
            status_colors = {
                PathStatus.LOCKED: "dim",
                PathStatus.AVAILABLE: "bright_green", 
                PathStatus.IN_PROGRESS: "bright_yellow",
                PathStatus.COMPLETED: "bright_magenta"
            }
            
            status_icons = {
                PathStatus.LOCKED: "🔒",
                PathStatus.AVAILABLE: "🟢",
                PathStatus.IN_PROGRESS: "🟡", 
                PathStatus.COMPLETED: "✅"
            }
            
            # Progress bar
            progress_percent = progress_info.get('progress_percent', 0)
            progress_bar = "█" * int(progress_percent // 10) + "░" * (10 - int(progress_percent // 10))
            
            path_panel = Panel(
                f"[bold]{path['icon']} {path['name']}[/bold]\n"
                f"[dim]{path['description']}[/dim]\n\n"
                f"📊 Progress: [{status_colors[status]}]{progress_bar}[/{status_colors[status]}] {progress_percent:.0f}%\n"
                f"⏱️ Estimated Time: {path['estimated_time']}\n"
                f"🎯 Scenarios: {len(path['scenarios'])} challenges\n"
                f"⭐ Difficulty: {path['difficulty'].title()}",
                title=f"{status_icons[status]} {status.value.title()}",
                border_style=status_colors[status]
            )
            self.console.print(path_panel)
        
        input("\nPress Enter to return to main menu...")
    
    def view_progress(self):
        """Display user progress, achievements, and statistics"""
        progress_summary = tracker.get_progress_summary()
        stats = progress_summary['stats']
        
        self.console.print("\n[bold bright_cyan]Your Journey Progress[/bold bright_cyan]\n")
        
        # Stats Panel
        stats_panel = Panel(
            f"[bold bright_green]Rank:[/bold bright_green] {stats.rank}\n"
            f"[bold bright_blue]Level:[/bold bright_blue] {stats.level} ({stats.xp} XP)\n"
            f"[bold bright_yellow]Next Level:[/bold bright_yellow] {progress_summary['xp_to_next_level']} XP needed\n"
            f"[bold bright_magenta]Scenarios Completed:[/bold bright_magenta] {progress_summary['scenarios_completed']}/{progress_summary['total_scenarios']}\n"
            f"[bold bright_cyan]Learning Streak:[/bold bright_cyan] {stats.streak_days} days\n"
            f"[bold bright_red]Total Time:[/bold bright_red] {stats.total_time_spent // 60}m {stats.total_time_spent % 60}s",
            title="Warrior Stats",
            border_style="bright_green"
        )
        self.console.print(stats_panel)
        
        # Achievements Panel
        unlocked_achievements = [a for a in tracker.achievements.values() if a.unlocked]
        locked_achievements = [a for a in tracker.achievements.values() if not a.unlocked]
        
        achievements_text = "[bold bright_yellow]Unlocked Achievements:[/bold bright_yellow]\n"
        if unlocked_achievements:
            for achievement in unlocked_achievements:
                achievements_text += f"  {achievement.icon} {achievement.name} - {achievement.description}\n"
        else:
            achievements_text += "  [dim]No achievements unlocked yet. Complete scenarios to earn them![/dim]\n"
        
        achievements_text += "\n[bold bright_blue]Available Achievements:[/bold bright_blue]\n"
        for achievement in locked_achievements[:3]:  # Show first 3 locked
            achievements_text += f"  🔒 {achievement.name} - {achievement.description}\n"
        
        if len(locked_achievements) > 3:
            achievements_text += f"  [dim]... and {len(locked_achievements) - 3} more to discover![/dim]"
        
        achievements_panel = Panel(
            achievements_text,
            title=f"Achievements ({len(unlocked_achievements)}/{len(tracker.achievements)})",
            border_style="bright_yellow"
        )
        self.console.print("\n")
        self.console.print(achievements_panel)
        
        input("\nPress Enter to return to main menu...")
    
    def scenario_management(self):
        """Manage scenarios - start, stop, check, reset"""
        scenarios = self.manager.list_scenarios()
        
        if not scenarios:
            self.console.print(Panel(
                "[yellow]No scenarios available for management[/yellow]",
                title="⚠️ No Scenarios",
                border_style="yellow"
            ))
            input("\nPress Enter to return...")
            return
        
        while True:
            self.console.clear()
            self.console.print("🎆 [bold bright_cyan]Scenario Management[/bold bright_cyan] 🎆\n")
            
            # List scenarios without expensive status checks
            for i, (name, scenario) in enumerate(scenarios.items(), 1):
                # Show completion status instead of runtime status
                completed = name in [s for s, p in tracker.scenarios.items() if p.status == "completed"]
                status = "✅ COMPLETED" if completed else "🎯 AVAILABLE"
                self.console.print(f"[bright_green]{i}.[/bright_green] {name} - {status}")
            
            self.console.print("\n[bright_yellow]Actions:[/bright_yellow]")
            self.console.print("[bright_green]s[/bright_green] - Start scenario")
            self.console.print("[bright_green]t[/bright_green] - Stop scenario")
            self.console.print("[bright_green]c[/bright_green] - Check scenario")
            self.console.print("[bright_green]r[/bright_green] - Reset scenario")
            self.console.print("[bright_green]i[/bright_green] - Show connection info")
            self.console.print("[bright_green]b[/bright_green] - Back to main menu")
            
            choice = Prompt.ask("\n[bright_yellow]Choose action[/bright_yellow]", choices=["s", "t", "c", "r", "i", "b"])
            
            if choice == "b":
                break
            
            scenario_choice = Prompt.ask(
                "[bright_yellow]Select scenario number[/bright_yellow]",
                choices=[str(i) for i in range(1, len(scenarios) + 1)]
            )
            
            scenario_name = list(scenarios.keys())[int(scenario_choice) - 1]
            scenario = self.manager.get_scenario(scenario_name)
            
            if choice == "s":
                self.start_scenario(scenario, scenario_name)
            elif choice == "t":
                self.stop_scenario(scenario, scenario_name)
            elif choice == "c":
                self.check_scenario(scenario, scenario_name)
            elif choice == "r":
                self.reset_scenario(scenario, scenario_name)
            elif choice == "i":
                self.show_scenario_connection_info(scenario, scenario_name)
    
    def start_scenario(self, scenario, name):
        """Start a scenario with storytelling and connection info"""
        
        # Show story introduction
        story_intro = storyteller.format_story_intro(name)
        self.console.print(Panel(
            story_intro,
            title=f"🎬 {name.upper()}",
            border_style="bright_cyan"
        ))
        
        if not Confirm.ask("\n[bright_yellow]Accept this mission?[/bright_yellow]", default=True):
            return
        
        self.console.print(f"\n⚡ [bold bright_green]Initializing scenario environment...[/bold bright_green]")
        
        # Track scenario start
        tracker.start_scenario(name)
        
        # Show progress during initialization
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
        ) as progress:
            task = progress.add_task("Setting up Docker environment...", total=None)
            
            try:
                result = scenario.start()
                progress.update(task, description="✅ Environment ready!")
                time.sleep(0.5)  # Brief pause to show completion
            except Exception as e:
                progress.update(task, description="❌ Setup failed!")
                time.sleep(0.5)
                self.console.print(f"[red]✗ Error: {e}[/red]")
                input("\nPress Enter to continue...")
                return
        
        if result.get('success', False):
            self.console.print(f"[bright_green]✓ Environment ready! The clock is ticking...[/bright_green]")
            
            # Show connection info for troubleshooting
            self._show_connection_info(scenario, name, result)
            
            if 'instructions' in result:
                self.console.print(Panel(
                    f"[bright_cyan]{result['instructions']}[/bright_cyan]\n\n"
                    f"[dim]💡 Need help? Use the check command to get progressive hints![/dim]",
                    title="🎯 Your Mission",
                    border_style="bright_blue"
                ))
        else:
            self.console.print(f"[red]✗ Failed to start {name}: {result.get('error', 'Unknown error')}[/red]")
        
        input("\nPress Enter to continue...")
    
    def _show_connection_info(self, scenario, name, result):
        """Display connection information for troubleshooting"""
        try:
            status_info = scenario.status()
            
            # Build connection info based on scenario type
            connection_info = "\n📋 [bold bright_yellow]Scenario Resources:[/bold bright_yellow]\n"
            commands = "\n🔧 [bold bright_green]Quick Commands:[/bold bright_green]\n"
            
            if 'nginx' in name:
                # Docker-based nginx scenarios
                container_name = result.get('container_name', f'clouddojo-{name}')
                port = result.get('port', '8080')
                
                connection_info += f"  🐳 Container: [bright_cyan]{container_name}[/bright_cyan]\n"
                connection_info += f"  🌐 Port: [bright_cyan]http://localhost:{port}[/bright_cyan]\n"
                connection_info += f"  📁 Config: [bright_cyan]/etc/nginx/[/bright_cyan]\n"
                
                commands += f"  docker ps                                    # List containers\n"
                commands += f"  docker exec -it {container_name} bash        # Enter container\n"
                commands += f"  docker logs {container_name}                 # View logs\n"
                commands += f"  curl http://localhost:{port}                 # Test web server\n"
                
            elif 'k8s' in name:
                # Kubernetes scenarios
                namespace = result.get('namespace', 'default')
                pod_name = result.get('pod_name', f'{name}-pod')
                
                connection_info += f"  ⚓ Namespace: [bright_cyan]{namespace}[/bright_cyan]\n"
                connection_info += f"  📦 Pod: [bright_cyan]{pod_name}[/bright_cyan]\n"
                connection_info += f"  🎯 Context: [bright_cyan]minikube[/bright_cyan]\n"
                
                commands += f"  kubectl get pods -n {namespace}              # List pods\n"
                commands += f"  kubectl describe pod {pod_name} -n {namespace} # Pod details\n"
                commands += f"  kubectl logs {pod_name} -n {namespace}        # Pod logs\n"
                commands += f"  kubectl exec -it {pod_name} -n {namespace} -- bash # Enter pod\n"
            
            # Add general commands
            commands += "\n📝 [bold bright_blue]General Commands:[/bold bright_blue]\n"
            commands += "  docker ps -a                                 # All containers\n"
            commands += "  kubectl get all                              # All K8s resources\n"
            
            # Display the connection panel
            connection_panel = Panel(
                connection_info + commands + "\n"
                "[dim bright_magenta]💡 Open a new terminal to run these commands while keeping the dojo open![/dim bright_magenta]",
                title="🔗 Connection Info",
                border_style="bright_yellow"
            )
            self.console.print("\n")
            self.console.print(connection_panel)
            
        except Exception as e:
            # Fallback connection info if status fails
            fallback_panel = Panel(
                "📋 [bold bright_yellow]Scenario Active![/bold bright_yellow]\n\n"
                "🔧 [bold bright_green]Basic Commands:[/bold bright_green]\n"
                "  docker ps                                    # List containers\n"
                "  kubectl get pods                             # List pods\n\n"
                "[dim bright_magenta]💡 Open a new terminal to troubleshoot while keeping the dojo open![/dim bright_magenta]",
                title="🔗 Connection Info",
                border_style="bright_yellow"
            )
            self.console.print("\n")
            self.console.print(fallback_panel)
    
    def stop_scenario(self, scenario, name):
        """Stop a scenario"""
        self.console.print(f"\n🛑 [bold bright_red]Stopping {name}...[/bold bright_red]")
        try:
            success = scenario.stop()
            if success:
                self.console.print(f"[bright_green]✓ {name} stopped successfully![/bright_green]")
            else:
                self.console.print(f"[red]✗ Failed to stop {name}[/red]")
        except Exception as e:
            self.console.print(f"[red]✗ Error: {e}[/red]")
        input("\nPress Enter to continue...")
    
    def check_scenario(self, scenario, name):
        """Check scenario solution with hints and completion tracking"""
        self.console.print(f"\n🔍 [bold bright_blue]Analyzing your solution...[/bold bright_blue]")
        
        # Get current scenario progress for hint tracking
        scenario_progress = tracker.scenarios.get(name)
        hints_used = scenario_progress.hints_used if scenario_progress else 0
        
        try:
            result = scenario.check()
            if result.get('passed', False):
                # Calculate actual completion time
                scenario_progress = tracker.scenarios.get(name)
                if scenario_progress and hasattr(scenario_progress, 'start_time') and scenario_progress.start_time:
                    time_taken = int(time.time() - scenario_progress.start_time)
                else:
                    time_taken = 60  # Default to 1 minute if no start time recorded
                
                # Award XP and track completion
                xp_earned = tracker.complete_scenario(name, time_taken, hints_used)
                
                # Show completion message
                self.console.print("[bold green]✅ Challenge Completed![/bold green]")
                
                # Show story conclusion
                story_conclusion = storyteller.format_completion_story(name, time_taken)
                self.console.print(Panel(
                    f"[bold bright_green]{story_conclusion}[/bold bright_green]\n\n"
                    f"[bright_yellow]⚡ XP Earned: {xp_earned}[/bright_yellow]\n"
                    f"[dim]Hints used: {hints_used}[/dim]",
                    title="🏆 MISSION ACCOMPLISHED",
                    border_style="bright_green"
                ))
                
            else:
                self.console.print(f"[bright_yellow]⏳ Mission in progress...[/bright_yellow]")
                
                if 'feedback' in result:
                    self.console.print(f"\n[bright_cyan]Current Status:[/bright_cyan] {result['feedback']}")
                
                # Offer progressive hints
                if hints_manager.has_hints(name):
                    max_hints = hints_manager.get_max_hint_level(name)
                    current_hint_level = hints_used + 1
                    
                    if current_hint_level <= max_hints:
                        if Confirm.ask(f"\n[bright_blue]Need a hint? (Level {current_hint_level}/{max_hints})[/bright_blue]", default=False):
                            hint = hints_manager.get_hint(name, current_hint_level)
                            if hint:
                                self.console.print(Panel(
                                    f"[bold]{hint.title}[/bold]\n\n"
                                    f"{hint.content}\n\n"
                                    f"[dim]Command: {hint.command}[/dim]" if hint.command else "",
                                    title=f"💡 Hint {current_hint_level}",
                                    border_style="bright_blue"
                                ))
                                
                                # Update hints used
                                if scenario_progress:
                                    scenario_progress.hints_used += 1
                                    tracker._save_progress()
                
        except Exception as e:
            self.console.print(f"[red]✗ Error: {e}[/red]")
        
        input("\nPress Enter to continue...")
    
    def show_scenario_connection_info(self, scenario, name):
        """Show connection info for an active scenario"""
        self.console.print(f"\n🔗 [bold bright_cyan]Connection Info for {name}[/bold bright_cyan]")
        
        try:
            status_info = scenario.status()
            if not status_info.get('running', False):
                self.console.print(Panel(
                    "[yellow]Scenario is not currently running.[/yellow]\n\n"
                    "Start the scenario first to see connection details.",
                    title="⚠️ Not Running",
                    border_style="yellow"
                ))
                input("\nPress Enter to continue...")
                return
            
            # Use the same connection info logic
            result = {'container_name': f'clouddojo-{name}', 'port': '8080', 'namespace': 'default', 'pod_name': f'{name}-pod'}
            self._show_connection_info(scenario, name, result)
            
        except Exception as e:
            self.console.print(Panel(
                "[red]Could not retrieve connection info.[/red]\n\n"
                "🔧 [bold bright_green]Basic Commands:[/bold bright_green]\n"
                "  docker ps                                    # List containers\n"
                "  kubectl get pods                             # List pods\n\n"
                "[dim bright_magenta]💡 Use these commands in a separate terminal![/dim bright_magenta]",
                title="🔗 Basic Connection Info",
                border_style="bright_yellow"
            ))
        
        input("\nPress Enter to continue...")
    
    def reset_scenario(self, scenario, name):
        """Reset a scenario"""
        if not Confirm.ask(f"[yellow]Reset {name} to initial state?[/yellow]", default=False):
            return
        
        self.console.print(f"\n🔄 [bold bright_purple]Resetting {name}...[/bold bright_purple]")
        try:
            success = scenario.reset()
            if success:
                self.console.print(f"[bright_green]✓ {name} reset successfully![/bright_green]")
            else:
                self.console.print(f"[red]✗ Failed to reset {name}[/red]")
        except Exception as e:
            self.console.print(f"[red]✗ Error: {e}[/red]")
        input("\nPress Enter to continue...")
    
    def show_status(self):
        """Show dojo status (optimized for speed)"""
        scenarios = self.manager.list_scenarios()
        
        self.console.print("\n📊 [bold bright_cyan]Dojo Status Dashboard[/bold bright_cyan] 📊\n")
        
        if not scenarios:
            self.console.print(Panel(
                "[yellow]No scenarios loaded[/yellow]",
                title="🌌 Empty Dojo",
                border_style="yellow"
            ))
        else:
            # Quick status without expensive Docker checks
            progress_summary = tracker.get_progress_summary()
            
            status_panel = Panel(
                f"🎯 [bold bright_blue]Available Scenarios:[/bold bright_blue] {len(scenarios)}\n"
                f"✅ [bold bright_green]Completed:[/bold bright_green] {progress_summary['scenarios_completed']}\n"
                f"⚡ [bold bright_yellow]Your Level:[/bold bright_yellow] {progress_summary['stats'].level}\n"
                f"🔥 [bold bright_magenta]Current Streak:[/bold bright_magenta] {progress_summary['stats'].streak_days} days\n\n"
                f"[dim bright_cyan]\"Ready for your next challenge!\" 🌟[/dim bright_cyan]",
                title="🏮 Dojo Overview",
                border_style="bright_green"
            )
            self.console.print(status_panel)
        
        input("\nPress Enter to return to main menu...")
    
    def run(self):
        """Main interactive loop"""
        try:
            while self.running:
                self.show_main_menu()
                
                choice = Prompt.ask(
                    "\n[bright_yellow]Enter your choice[/bright_yellow]",
                    choices=["1", "2", "3", "4", "5", "6"],
                    default="1"
                )
                
                if choice == "1":
                    self.show_learning_paths()
                elif choice == "2":
                    self.browse_scenarios()
                elif choice == "3":
                    self.view_progress()
                elif choice == "4":
                    self.scenario_management()
                elif choice == "5":
                    self.show_status()
                elif choice == "6":
                    self.console.print("\n[dim bright_cyan]\"May your servers always stay healthy!\"[/dim bright_cyan]")
                    self.console.print(get_small_banner())
                    self.running = False
        
        except KeyboardInterrupt:
            self.console.print("\n[dim bright_cyan]🌸 \"Until next time, digital warrior!\" 🌸[/dim bright_cyan]")
            self.console.print(get_small_banner())

# Simplified CLI with only 3 commands
@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """CloudDojo CLI - Gamified DevOps Troubleshooting Platform
    
    Master the art of system debugging through immersive challenges
    "Every system failure is a lesson in disguise - embrace the chaos!"
    """
    if ctx.invoked_subcommand is None:
        # Show simplified help when no command is given
        console.print(get_banner())
        console.print("\nAvailable commands:")
        console.print("[bright_green]setup[/bright_green]   - Install training prerequisites")
        console.print("[bright_green]dojo[/bright_green]    - Enter the interactive training realm")
        console.print("[bright_green]version[/bright_green] - Show version information")
        console.print("\n[dim bright_cyan]\"Begin your journey with 'clouddojo dojo'\"[/dim bright_cyan]")

@cli.command()
def setup():
    """Install prerequisites for your training dojo"""
    setup_manager.quick_setup()

@cli.command()
def dojo():
    """Enter the sacred dojo (interactive training realm)"""
    # Show welcome banner
    console.print(get_small_banner())
    console.print("[dim bright_magenta]Initializing training environment...[/dim bright_magenta]\n")
    
    interactive_dojo = InteractiveDojo()
    interactive_dojo.run()

@cli.command()
def version():
    """About this tool"""
    console.print(get_small_banner())
    
    version_panel = Panel(
        "[bold cyan]CloudDojo CLI[/bold cyan]\n"
        "[bold green]Version 0.3.0[/bold green]\n\n"
        "[bold]Features:[/bold]\n"
        "  • Interactive training interface\n"
        "  • Gamified scenario management\n"
        "  • Real-world debugging challenges\n"
        "  • Cross-platform support\n\n"
        "[dim]DevOps troubleshooting made engaging[/dim]",
        title="Version Info",
        border_style="cyan",
        box=ROUNDED
    )
    console.print(version_panel)

if __name__ == "__main__":
    cli()