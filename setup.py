#!/usr/bin/env python3
"""
AI Video Transcription Studio Setup Script
Universal installer for Windows and Mac
"""

import sys
import os
import platform
import subprocess
import shutil
from pathlib import Path

VERSION = "1.0.0"
APP_NAME = "AI Video Transcription Studio"
REQUIREMENTS_FILE = "requirements.txt"

def get_system_info():
    """Get system information"""
    system = platform.system().lower()
    architecture = platform.machine().lower()
    
    print(f"🖥️  Detected System: {platform.system()} {platform.release()}")
    print(f"🏗️  Architecture: {architecture}")
    print(f"🐍 Python Version: {platform.python_version()}")
    
    return system, architecture

def check_python_version():
    """Check if Python version is compatible"""
    min_version = (3, 8)
    current_version = sys.version_info[:2]
    
    if current_version < min_version:
        print(f"❌ Python {min_version[0]}.{min_version[1]}+ is required. Current: {current_version[0]}.{current_version[1]}")
        return False
    
    print(f"✅ Python version {current_version[0]}.{current_version[1]} is compatible")
    return True

def run_command(command, description="", shell=False):
    """Run a system command with error handling"""
    try:
        print(f"🔄 {description}...")
        if shell:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
        else:
            result = subprocess.run(command, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            return True
        else:
            print(f"❌ {description} failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} failed: {e}")
        return False

def install_ffmpeg_windows():
    """Install FFmpeg on Windows"""
    print("🎥 Installing FFmpeg for Windows...")
    
    # Check if winget is available
    if run_command(["winget", "--version"], "Checking winget availability"):
        # Try installing with winget
        if run_command(["winget", "install", "ffmpeg"], "Installing FFmpeg via winget"):
            return True
    
    # Check if chocolatey is available
    if run_command(["choco", "--version"], "Checking Chocolatey availability"):
        if run_command(["choco", "install", "ffmpeg", "-y"], "Installing FFmpeg via Chocolatey"):
            return True
    
    # Manual installation guide
    print("⚠️  Automatic FFmpeg installation failed.")
    print("📋 Manual installation required:")
    print("   1. Download FFmpeg from: https://ffmpeg.org/download.html#build-windows")
    print("   2. Extract to C:\\ffmpeg")
    print("   3. Add C:\\ffmpeg\\bin to your PATH environment variable")
    print("   4. Restart your command prompt and try again")
    
    return False

def install_ffmpeg_mac():
    """Install FFmpeg on macOS"""
    print("🎥 Installing FFmpeg for macOS...")
    
    # Check if Homebrew is available
    if run_command(["brew", "--version"], "Checking Homebrew availability"):
        if run_command(["brew", "install", "ffmpeg"], "Installing FFmpeg via Homebrew"):
            return True
    
    # Check if MacPorts is available
    if run_command(["port", "version"], "Checking MacPorts availability"):
        if run_command(["sudo", "port", "install", "ffmpeg"], "Installing FFmpeg via MacPorts"):
            return True
    
    # Manual installation guide
    print("⚠️  Automatic FFmpeg installation failed.")
    print("📋 Manual installation required:")
    print("   1. Install Homebrew: /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"")
    print("   2. Run: brew install ffmpeg")
    print("   3. Try running this setup again")
    
    return False

def install_ffmpeg_linux():
    """Install FFmpeg on Linux"""
    print("🎥 Installing FFmpeg for Linux...")
    
    # Try different package managers
    package_managers = [
        (["apt", "update"], ["apt", "install", "-y", "ffmpeg"], "Installing FFmpeg via apt"),
        (["yum", "update"], ["yum", "install", "-y", "ffmpeg"], "Installing FFmpeg via yum"),
        (["dnf", "update"], ["dnf", "install", "-y", "ffmpeg"], "Installing FFmpeg via dnf"),
        (["pacman", "-Sy"], ["pacman", "-S", "--noconfirm", "ffmpeg"], "Installing FFmpeg via pacman"),
    ]
    
    for update_cmd, install_cmd, description in package_managers:
        if run_command(update_cmd, f"Updating package manager"):
            if run_command(install_cmd, description):
                return True
    
    print("⚠️  Automatic FFmpeg installation failed.")
    print("📋 Please install FFmpeg manually using your distribution's package manager")
    return False

def check_ffmpeg():
    """Check if FFmpeg is installed and working"""
    print("🔍 Checking FFmpeg installation...")
    
    if run_command(["ffmpeg", "-version"], "Testing FFmpeg"):
        print("✅ FFmpeg is installed and working")
        return True
    else:
        print("❌ FFmpeg is not installed or not in PATH")
        return False

def create_virtual_environment():
    """Create a virtual environment"""
    venv_path = Path("venv")
    
    if venv_path.exists():
        print("📁 Virtual environment already exists")
        return True
    
    print("🏗️  Creating virtual environment...")
    if run_command([sys.executable, "-m", "venv", "venv"], "Creating virtual environment"):
        print("✅ Virtual environment created successfully")
        return True
    else:
        print("❌ Failed to create virtual environment")
        return False

def get_pip_command():
    """Get the appropriate pip command for the current system"""
    system = platform.system().lower()
    if system == "windows":
        return os.path.join("venv", "Scripts", "pip")
    else:
        return os.path.join("venv", "bin", "pip")

def install_python_requirements():
    """Install Python requirements"""
    print("📦 Installing Python dependencies...")
    
    pip_cmd = get_pip_command()
    
    # Upgrade pip first
    if not run_command([pip_cmd, "install", "--upgrade", "pip"], "Upgrading pip"):
        return False
    
    # Install requirements
    if not run_command([pip_cmd, "install", "-r", REQUIREMENTS_FILE], "Installing requirements"):
        return False
    
    print("✅ Python dependencies installed successfully")
    return True

def download_whisper_model():
    """Download Whisper model"""
    print("🤖 Downloading Whisper AI model...")
    
    python_cmd = sys.executable
    if platform.system().lower() == "windows":
        python_cmd = os.path.join("venv", "Scripts", "python")
    else:
        python_cmd = os.path.join("venv", "bin", "python")
    
    download_script = '''
import whisper
print("Downloading Whisper turbo model...")
model = whisper.load_model("turbo")
print("Whisper model downloaded successfully!")
'''
    
    try:
        result = subprocess.run([python_cmd, "-c", download_script], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Whisper model downloaded successfully")
            return True
        else:
            print(f"❌ Failed to download Whisper model: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Failed to download Whisper model: {e}")
        return False

def create_desktop_shortcut():
    """Create desktop shortcut"""
    system = platform.system().lower()
    
    if system == "windows":
        return create_windows_shortcut()
    elif system == "darwin":
        return create_mac_shortcut()
    else:
        return create_linux_shortcut()

def create_windows_shortcut():
    """Create Windows desktop shortcut"""
    try:
        import winshell
        from win32com.client import Dispatch
        
        desktop = winshell.desktop()
        shortcut_path = os.path.join(desktop, f"{APP_NAME}.lnk")
        target = os.path.join(os.getcwd(), "venv", "Scripts", "python.exe")
        arguments = os.path.join(os.getcwd(), "src", "main.py")
        working_dir = os.getcwd()
        
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.Targetpath = target
        shortcut.Arguments = arguments
        shortcut.WorkingDirectory = working_dir
        shortcut.IconLocation = target
        shortcut.save()
        
        print(f"✅ Desktop shortcut created: {shortcut_path}")
        return True
    except Exception as e:
        print(f"⚠️  Could not create desktop shortcut: {e}")
        return False

def create_mac_shortcut():
    """Create macOS application bundle"""
    app_name = f"{APP_NAME}.app"
    app_path = os.path.join(os.path.expanduser("~/Desktop"), app_name)
    
    try:
        # Create app bundle structure
        os.makedirs(os.path.join(app_path, "Contents", "MacOS"), exist_ok=True)
        
        # Create executable script
        script_content = f'''#!/bin/bash
cd "{os.getcwd()}"
./venv/bin/python src/main.py
'''
        
        script_path = os.path.join(app_path, "Contents", "MacOS", APP_NAME.replace(" ", ""))
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        os.chmod(script_path, 0o755)
        
        # Create Info.plist
        plist_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>
    <string>{APP_NAME}</string>
    <key>CFBundleExecutable</key>
    <string>{APP_NAME.replace(" ", "")}</string>
    <key>CFBundleVersion</key>
    <string>{VERSION}</string>
</dict>
</plist>'''
        
        with open(os.path.join(app_path, "Contents", "Info.plist"), 'w') as f:
            f.write(plist_content)
        
        print(f"✅ Application bundle created: {app_path}")
        return True
    except Exception as e:
        print(f"⚠️  Could not create application bundle: {e}")
        return False

def create_linux_shortcut():
    """Create Linux desktop entry"""
    try:
        desktop_entry = f'''[Desktop Entry]
Name={APP_NAME}
Comment=AI-powered video transcription tool
Exec={os.getcwd()}/venv/bin/python {os.getcwd()}/src/main.py
Icon={os.getcwd()}/icon.png
Terminal=false
Type=Application
Categories=AudioVideo;
'''
        
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop", f"{APP_NAME.replace(' ', '_')}.desktop")
        
        with open(desktop_path, 'w') as f:
            f.write(desktop_entry)
        
        os.chmod(desktop_path, 0o755)
        
        print(f"✅ Desktop entry created: {desktop_path}")
        return True
    except Exception as e:
        print(f"⚠️  Could not create desktop entry: {e}")
        return False

def main():
    """Main installation process"""
    print(f"🚀 {APP_NAME} v{VERSION} - Installation Setup")
    print("=" * 50)
    
    # Check system compatibility
    if not check_python_version():
        sys.exit(1)
    
    system, architecture = get_system_info()
    
    # Install FFmpeg based on system
    ffmpeg_installed = False
    if system == "windows":
        ffmpeg_installed = install_ffmpeg_windows()
    elif system == "darwin":
        ffmpeg_installed = install_ffmpeg_mac()
    elif system == "linux":
        ffmpeg_installed = install_ffmpeg_linux()
    
    # Check FFmpeg installation
    if not check_ffmpeg():
        if not ffmpeg_installed:
            print("⚠️  FFmpeg installation required for video processing")
            print("📋 Please install FFmpeg manually and run this setup again")
            
            # Ask user if they want to continue without FFmpeg
            response = input("❓ Continue setup without FFmpeg? (y/N): ").lower()
            if response != 'y':
                sys.exit(1)
    
    # Create virtual environment
    if not create_virtual_environment():
        print("❌ Failed to create virtual environment")
        sys.exit(1)
    
    # Install Python requirements
    if not install_python_requirements():
        print("❌ Failed to install Python dependencies")
        sys.exit(1)
    
    # Download Whisper model
    if not download_whisper_model():
        print("⚠️  Whisper model download failed - you can download it later from the app")
    
    # Create desktop shortcut
    create_desktop_shortcut()
    
    print("\n🎉 Installation completed successfully!")
    print(f"✨ {APP_NAME} is now ready to use!")
    print("\n📋 Next steps:")
    print("   1. Run the application from your desktop shortcut")
    print("   2. Or run: python src/main.py")
    print("   3. Select a video file and start transcribing!")
    print("\n💡 For CLI usage: python src/main.py --mode cli --video your_video.mp4")

if __name__ == "__main__":
    main()
