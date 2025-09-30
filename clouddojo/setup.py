#!/usr/bin/env python3
"""
Auto Setup Script for Docker, kubectl, Minikube
Supports: Ubuntu / Debian / Fedora / RHEL / CentOS / macOS (with Homebrew)
"""

import subprocess
import platform
import shutil
import threading
import time
from pathlib import Path
from typing import List, Tuple, Union

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

try:
    import distro
except ImportError:
    distro = None

console = Console()


class SetupManager:
    def __init__(self):
        self.os_type = platform.system().lower()
        self.arch = platform.machine().lower()
        self.distro = self._detect_distro() if self.os_type == "linux" else None
        self.verbose = False

    def _detect_distro(self) -> str:
        """Detect Linux distribution with fallback methods."""
        if distro:
            try:
                return distro.id().lower()
            except Exception:
                pass

        # /etc/os-release fallback
        try:
            with open("/etc/os-release", "r") as f:
                for line in f:
                    if line.startswith("ID="):
                        return line.split("=", 1)[1].strip().strip('"').lower()
        except Exception:
            pass

        # lsb_release fallback
        try:
            result = subprocess.run(["lsb_release", "-si"], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip().lower()
        except Exception:
            pass

        # package manager hints
        if shutil.which("apt-get"):
            return "ubuntu"
        if shutil.which("dnf"):
            return "fedora"
        if shutil.which("yum"):
            return "centos"

        return "unknown"

    def _run(self, cmd: Union[List[str], str], shell=False, sudo=False, silent=False, **kwargs) -> subprocess.CompletedProcess:
        if sudo:
            if isinstance(cmd, list):
                cmd = ["sudo"] + cmd
            else:
                cmd = "sudo " + cmd
        if "timeout" not in kwargs:
            kwargs["timeout"] = 300

        if self.verbose:
            cmd_str = " ".join(cmd) if isinstance(cmd, list) else cmd
            console.print(f"[dim cyan]Running: {cmd_str}[/dim cyan]")

        if self.verbose and not silent:
            return subprocess.run(cmd, shell=shell, text=True, **kwargs)
        else:
            return subprocess.run(cmd, shell=shell, capture_output=True, text=True, **kwargs)

    def _check_tool(self, tool: str, cmd: List[str]) -> Tuple[bool, str]:
        try:
            cp = self._run(cmd)
            if cp.returncode == 0:
                out = (cp.stdout or "").strip() or (cp.stderr or "").strip()
                line = out.splitlines()[0] if out else ""
                return True, line
        except Exception as e:
            return False, f"Error: {e}"
        return False, "Not installed"

    def quick_setup(self) -> bool:
        if self.os_type == "windows":
            console.print(Panel(
                "[bold red]⚠️ Windows not supported directly[/bold red]\nUse WSL or a Linux VM.",
                title="Setup"
            ))
            return False

        console.print(Panel(
            "[bold bright_magenta]🔧 Auto Setup[/bold bright_magenta]\n"
            "Checks for Docker, kubectl, minikube and installs them if needed.",
            title="🚀 Setup"
        ))

        choice = console.input("\n[cyan]Choose:[/cyan]\n"
                               "[1] Auto Install (recommended)\n"
                               "[2] Check Only\n"
                               "[3] Skip Setup\n"
                               "[4] [black on bright_red]⚡ Install the Hard Way ⚡[/black on bright_red]\n"
                               "[5] [bright_yellow]🔍 Verbose Install[/bright_yellow]\n"
                               "Enter [1–5] (1): ").strip() or "1"
        if choice == "1":
            return self._auto_install()
        elif choice == "2":
            return self._check_only()
        elif choice == "4":
            return self._hard_way_challenge()
        elif choice == "5":
            self.verbose = True
            console.print("[bright_yellow]🔍 Verbose mode enabled[/bright_yellow]")
            return self._auto_install()
        else:
            console.print("[yellow]⚠️ Skipping setup[/yellow]")
            return True

    def _auto_install(self) -> bool:
        # Show patience warning for first-time setup
        console.print(Panel(
            "[bold yellow]⚠️ CAUTION:[/bold yellow] If this is your first time setting up, it might take a *while* — like, 'watching paint dry' level slow.\n"
            "Good things come to those who wait... but great things come to those with a fast internet connection.",
            title="⏳ Patience is key",
            border_style="yellow"
        ))
        try:
            ready = console.input("\n[cyan]Ready to proceed? (Y/n):[/cyan] ").strip().lower()
            if ready in ("n", "no"):
                console.print("[yellow]Setup cancelled[/yellow]")
                return False
        except KeyboardInterrupt:
            console.print("\n[yellow]Setup cancelled[/yellow]")
            return False

        console.print("[dim]🔐 Requesting sudo access...[/dim]")
        try:
            self._run(["sudo", "-v"])
        except Exception as e:
            console.print(f"[red]❌ Failed to get sudo: {e}[/red]")
            return False

        def keep_sudo_alive():
            while True:
                time.sleep(60)
                subprocess.run(["sudo", "-v"], capture_output=True)

        threading.Thread(target=keep_sudo_alive, daemon=True).start()

        console.print("\n[bold cyan]🔍 Checking tools...[/bold cyan]")
        tools = {
            "docker": ["docker", "--version"],
            "kubectl": ["kubectl", "version", "--client=true"],
            "minikube": ["minikube", "version"]
        }
        missing = []
        for name, cmd in tools.items():
            ok, ver = self._check_tool(name, cmd)
            if ok:
                console.print(f"[green]✓ {name}[/green] — {ver}")
            else:
                console.print(f"[red]✗ {name}[/red] — {ver}")
                missing.append(name)

        if not missing:
            console.print("\n[green]✅ All tools already installed[/green]")
            return self._check_services()

        console.print(f"\n[yellow]📦 Installing: {', '.join(missing)}[/yellow]")
        console.print("[dim]Press Ctrl+C to skip installation of a specific tool[/dim]")

        from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console,
        ) as progress:
            total = len(missing)
            task = progress.add_task("Installing tools...", total=total)

            count_success = 0
            for idx, tool in enumerate(missing):
                progress.update(task, description=f"Installing {tool}...", completed=idx)
                try:
                    if tool == "docker" and self._install_docker_silent():
                        count_success += 1
                    elif tool == "kubectl" and self._install_kubectl_silent():
                        count_success += 1
                    elif tool == "minikube" and self._install_minikube_silent():
                        count_success += 1
                except KeyboardInterrupt:
                    console.print(f"\n[yellow]Skipping {tool} installation...[/yellow]")
                progress.update(task, completed=idx + 1)

            progress.update(task, description="Done installation", completed=total)

        if count_success == len(missing):
            console.print("\n[green]✅ Installed all missing tools[/green]")
        elif count_success > 0:
            console.print(f"\n[yellow]⚠️ Installed {count_success}/{len(missing)} tools[/yellow]")
        else:
            console.print(f"\n[red]❌ No tools were installed successfully[/red]")
            console.print("[yellow]Install manually and rerun this script[/yellow]")

        return self._check_services()

    def _install_docker_silent(self) -> bool:
        try:
            if self.os_type == "linux":
                if self.distro in ("ubuntu", "debian"):
                    # Clean up old files first
                    self._run("rm -f /etc/apt/sources.list.d/docker.list", shell=True, sudo=True)
                    self._run("rm -f /etc/apt/keyrings/docker.gpg", shell=True, sudo=True)
                    
                    # Official Docker installation
                    self._run("apt-get update", shell=True, sudo=True)
                    self._run("apt-get install -y ca-certificates curl gnupg lsb-release", shell=True, sudo=True)
                    self._run("mkdir -p /etc/apt/keyrings", shell=True, sudo=True)

                    # Download GPG key
                    self._run(
                        "curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg",
                        shell=True
                    )

                    # Add repository
                    codename = subprocess.check_output(["lsb_release", "-cs"], text=True).strip()
                    repo_line = f"deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu {codename} stable"
                    self._run(f'echo "{repo_line}" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null', shell=True)

                    # Update and install
                    self._run("apt-get update", shell=True, sudo=True)
                    result = self._run(
                        "apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin",
                        shell=True, sudo=True
                    )
                    if result.returncode != 0:
                        return False
                    self._run("systemctl enable docker", shell=True, sudo=True)
                    self._run("systemctl start docker", shell=True, sudo=True)
                    return True

                elif self.distro in ("fedora",):
                    self._run("dnf config-manager --add-repo https://download.docker.com/linux/fedora/docker-ce.repo", shell=True, sudo=True)
                    result = self._run("dnf install -y docker-ce docker-ce-cli containerd.io", shell=True, sudo=True)
                    self._run("systemctl enable docker", shell=True, sudo=True)
                    self._run("systemctl start docker", shell=True, sudo=True)
                    return result.returncode == 0

                elif self.distro in ("centos", "rhel"):
                    self._run("yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo", shell=True, sudo=True)
                    result = self._run("yum install -y docker-ce docker-ce-cli containerd.io", shell=True, sudo=True)
                    self._run("systemctl enable docker", shell=True, sudo=True)
                    self._run("systemctl start docker", shell=True, sudo=True)
                    return result.returncode == 0

                else:
                    console.print(f"[red]Unsupported distro: {self.distro}[/red]")
                    return False

            elif self.os_type == "darwin" and shutil.which("brew"):
                result = self._run(["brew", "install", "--cask", "docker"])
                return result.returncode == 0

        except subprocess.TimeoutExpired:
            console.print("[red]Docker installation timed out[/red]")
            return False
        except Exception as e:
            console.print(f"[red]Docker installation failed: {e}[/red]")
            return False

    def _install_kubectl_silent(self) -> bool:
        try:
            arch = "amd64" if "x86_64" in self.arch else "arm64"
            cp = self._run(["curl", "-L", "-s", "https://dl.k8s.io/release/stable.txt"])
            if cp.returncode != 0 or not cp.stdout:
                return False
            version = cp.stdout.strip()
            url = f"https://dl.k8s.io/release/{version}/bin/linux/{arch}/kubectl"
            self._run(["curl", "-LO", url])
            self._run(["chmod", "+x", "kubectl"])
            self._run(["mv", "kubectl", "/usr/local/bin/kubectl"], sudo=True)
            return True
        except Exception:
            return False

    def _install_minikube_silent(self) -> bool:
        try:
            arch = "amd64" if "x86_64" in self.arch else "arm64"
            url = f"https://storage.googleapis.com/minikube/releases/latest/minikube-linux-{arch}"
            self._run(["curl", "-LO", url])
            self._run(["install", f"minikube-linux-{arch}", "/usr/local/bin/minikube"], sudo=True)
            self._run(["rm", f"minikube-linux-{arch}"])
            return True
        except Exception:
            return False

    def _check_only(self) -> bool:
        console.print("\n[bold cyan]🔍 Tool Status[/bold cyan]")
        table = Table(title="Tool Status")
        table.add_column("Tool", style="cyan")
        table.add_column("Status", justify="center")
        table.add_column("Version", style="dim")

        all_ok = True
        for name, cmd in [
            ("Docker", ["docker", "--version"]),
            ("kubectl", ["kubectl", "version", "--client=true"]),
            ("minikube", ["minikube", "version"])
        ]:
            ok, ver = self._check_tool(name.lower(), cmd)
            table.add_row(name, "[green]✓ Installed[/green]" if ok else "[red]✗ Missing[/red]", ver)
            if not ok:
                all_ok = False
        console.print(table)
        return all_ok and self._check_services()

    def _hard_way_challenge(self) -> bool:
        console.print(Panel(
            "[bold red]⚔️  THE HARD WAY CHALLENGE ⚔️[/bold red]\n"
            "You must install everything yourself.",
            title="Hard Way"
        ))
        try:
            confirm = console.input("\n[red]Proceed anyway? (yes/NO):[/red] ").strip().lower()
            if confirm not in ("yes", "y"):
                console.print("[yellow]Going back to auto install[/yellow]")
                return self._auto_install()
        except KeyboardInterrupt:
            console.print("\n[red]Cancelled[/red]")
            return False

        console.print("[cyan]Please follow official docs to install Docker, kubectl, and minikube manually.[/cyan]")
        return True

    def _check_services(self) -> bool:
        console.print("\n[bold cyan]🔍 Checking services[/bold cyan]")
        docker_cp = self._run(["docker", "info"])
        docker_ok = (docker_cp.returncode == 0)

        minikube_cp = self._run(["minikube", "status"])

        if docker_ok:
            console.print("[green]✓ Docker daemon is running[/green]")
        else:
            console.print(f"[yellow]⚠️ Docker daemon might not be running or accessible.\n{(docker_cp.stderr or '').strip()}[/yellow]")

        if minikube_cp.stdout and "Running" in minikube_cp.stdout:
            console.print("[green]✓ minikube is running[/green]")
            return docker_ok
        else:
            console.print("[yellow]Minikube is installed but not running[/yellow]")
            try:
                choice = console.input("[cyan]Start minikube now? (Y/n):[/cyan] ").strip().lower()
                if choice in ("", "y", "yes"):
                    console.print("[blue]Starting minikube...[/blue]")
                    subprocess.run(["minikube", "start"])
                    return docker_ok
            except KeyboardInterrupt:
                console.print("\n[red]Cancelled start[/red]")
        return docker_ok


if __name__ == "__main__":
    SetupManager().quick_setup()