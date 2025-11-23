#!/usr/bin/env python3
"""
Helper script to install oasdiff.
This script attempts to install oasdiff using the most appropriate method for the current platform.
"""

import os
import platform
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

def run_command(command, shell=False):
    """Run a command and return True if successful."""
    try:
        result = subprocess.run(
            command if shell else command.split(),
            shell=shell,
            capture_output=True,
            text=True,
            timeout=60
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
        return False

def check_oasdiff_installed():
    """Check if oasdiff is already installed."""
    return run_command("oasdiff --version")

def install_with_go():
    """Try to install oasdiff using Go."""
    print("Attempting to install oasdiff using Go...")
    if run_command("go version"):
        return run_command("go install github.com/oasdiff/oasdiff@latest")
    return False

def install_with_brew():
    """Try to install oasdiff using Homebrew (macOS)."""
    print("Attempting to install oasdiff using Homebrew...")
    if run_command("brew --version"):
        if run_command("brew tap oasdiff/homebrew-oasdiff"):
            return run_command("brew install oasdiff")
    return False

def install_with_curl():
    """Try to install oasdiff using the curl script."""
    print("Attempting to install oasdiff using curl...")
    if run_command("curl --version"):
        return run_command("curl -fsSL https://raw.githubusercontent.com/oasdiff/oasdiff/main/install.sh | sh", shell=True)
    return False

def download_binary():
    """Download oasdiff binary manually."""
    print("Attempting to download oasdiff binary...")
    
    system = platform.system().lower()
    machine = platform.machine().lower()
    
    # Map platform names
    if system == "darwin":
        os_name = "darwin"
    elif system == "linux":
        os_name = "linux"
    elif system == "windows":
        os_name = "windows"
        return False  # Skip binary download for Windows for now
    else:
        return False
    
    # Map architecture names
    if machine in ["x86_64", "amd64"]:
        arch = "amd64"
    elif machine in ["aarch64", "arm64"]:
        arch = "arm64"
    else:
        return False
    
    # Construct download URL (you may need to update the version)
    version = "v1.10.0"  # Update this to the latest version
    filename = f"oasdiff_{version}_{os_name}_{arch}.tar.gz"
    url = f"https://github.com/oasdiff/oasdiff/releases/download/{version}/{filename}"
    
    try:
        # Create temporary directory
        with tempfile.TemporaryDirectory() as tmp_dir:
            tar_path = os.path.join(tmp_dir, filename)
            
            # Download the file
            print(f"Downloading {url}...")
            urllib.request.urlretrieve(url, tar_path)
            
            # Extract the tar file
            if run_command(f"tar -xzf {tar_path} -C {tmp_dir}"):
                # Find the oasdiff binary
                binary_path = os.path.join(tmp_dir, "oasdiff")
                if os.path.exists(binary_path):
                    # Try to install to /usr/local/bin
                    dest_path = "/usr/local/bin/oasdiff"
                    if run_command(f"sudo cp {binary_path} {dest_path}"):
                        run_command(f"sudo chmod +x {dest_path}")
                        return True
                    
                    # Fallback: install to ~/.local/bin
                    local_bin = Path.home() / ".local" / "bin"
                    local_bin.mkdir(parents=True, exist_ok=True)
                    dest_path = local_bin / "oasdiff"
                    
                    if run_command(f"cp {binary_path} {dest_path}"):
                        run_command(f"chmod +x {dest_path}")
                        print(f"oasdiff installed to {dest_path}")
                        print(f"Make sure {local_bin} is in your PATH")
                        return True
            
    except Exception as e:
        print(f"Error downloading binary: {e}")
    
    return False

def main():
    """Main installation function."""
    print("oasdiff Installation Helper")
    print("=" * 40)
    
    # Check if already installed
    if check_oasdiff_installed():
        print("✓ oasdiff is already installed!")
        result = subprocess.run(["oasdiff", "--version"], capture_output=True, text=True)
        print(f"Version: {result.stdout.strip()}")
        return True
    
    print("oasdiff not found. Attempting installation...\n")
    
    # Get platform info
    system = platform.system()
    print(f"Detected platform: {system} {platform.machine()}")
    print()
    
    # Try different installation methods
    installation_methods = []
    
    if system == "Darwin":  # macOS
        installation_methods = [install_with_brew, install_with_go, install_with_curl, download_binary]
    elif system == "Linux":
        installation_methods = [install_with_go, install_with_curl, download_binary]
    else:  # Windows or other
        installation_methods = [install_with_go]
    
    for method in installation_methods:
        try:
            if method():
                print("✓ Installation successful!")
                if check_oasdiff_installed():
                    result = subprocess.run(["oasdiff", "--version"], capture_output=True, text=True)
                    print(f"oasdiff version: {result.stdout.strip()}")
                    print("\nYou can now run the API monitor!")
                    return True
                else:
                    print("Installation completed but oasdiff is not in PATH.")
                    print("You may need to restart your terminal or update your PATH.")
                    return False
        except Exception as e:
            print(f"Installation method failed: {e}")
            continue
    
    # If all methods failed
    print("✗ Could not install oasdiff automatically.")
    print("\nPlease install oasdiff manually:")
    print("1. Go users: go install github.com/oasdiff/oasdiff@latest")
    print("2. macOS with Homebrew: brew tap oasdiff/homebrew-oasdiff && brew install oasdiff")
    print("3. Download from: https://github.com/oasdiff/oasdiff/releases")
    print("4. See installation guide: https://github.com/oasdiff/oasdiff#installation")
    
    return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 