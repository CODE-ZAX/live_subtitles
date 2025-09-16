#!/usr/bin/env python3
"""
Build script for creating distributable packages of AI Video Transcription Studio
Supports creating installers for Windows and macOS
"""

import os
import sys
import shutil
import platform
import subprocess
import zipfile
from pathlib import Path

VERSION = "1.0.0"
APP_NAME = "AI-Video-Transcription-Studio"

def create_distribution_folder():
    """Create a clean distribution folder"""
    dist_folder = Path("dist")
    if dist_folder.exists():
        shutil.rmtree(dist_folder)
    
    dist_folder.mkdir()
    return dist_folder

def copy_source_files(dist_folder):
    """Copy necessary source files to distribution"""
    print("📁 Copying source files...")
    
    # Files and folders to include
    include_items = [
        "src/",
        "requirements.txt",
        "setup.py",
        "README.md",
        "USAGE.md",
        "Bangers-Regular.ttf"
    ]
    
    # System-specific installers
    system = platform.system().lower()
    if system == "windows":
        include_items.extend(["install_windows.bat"])
    elif system == "darwin":
        include_items.extend(["install_mac.sh"])
    
    for item in include_items:
        item_path = Path(item)
        if item_path.exists():
            if item_path.is_dir():
                shutil.copytree(item_path, dist_folder / item_path.name)
            else:
                shutil.copy2(item_path, dist_folder / item_path.name)
        else:
            print(f"⚠️  Warning: {item} not found, skipping...")

def create_installer_readme(dist_folder):
    """Create installation instructions"""
    system = platform.system().lower()
    
    readme_content = f"""# {APP_NAME} v{VERSION}

## 🚀 AI-Powered Video Transcription Studio

Transform your videos with professional AI-powered subtitles!

### ✨ Features
- 🎤 AI speech recognition with Whisper
- 🎬 Beautiful subtitle overlays
- 📱 Word-by-word rolling captions
- 🎨 Customizable fonts and colors
- 💻 Cross-platform (Windows, macOS, Linux)

### 📋 System Requirements
- Python 3.8 or higher
- FFmpeg (auto-installed by setup)
- 4GB RAM minimum
- 2GB free disk space

### 🛠️ Installation

"""

    if system == "windows":
        readme_content += """#### Windows Installation
1. **Double-click `install_windows.bat`**
2. Follow the on-screen instructions
3. Launch from desktop shortcut or `run_app.bat`

#### Manual Installation (Windows)
```cmd
# Install Python from https://python.org (if not installed)
# Open Command Prompt in this folder and run:
python setup.py
```
"""
    elif system == "darwin":
        readme_content += """#### macOS Installation
1. **Right-click `install_mac.sh` → Open With → Terminal**
2. Follow the on-screen instructions
3. Launch from Applications or `./run_app.sh`

#### Manual Installation (macOS)
```bash
# Open Terminal in this folder and run:
chmod +x install_mac.sh
./install_mac.sh
```
"""
    else:
        readme_content += """#### Linux Installation
```bash
# Open terminal in this folder and run:
python3 setup.py
```
"""

    readme_content += """
### 🎯 Usage

#### GUI Mode (Recommended)
```bash
python src/main.py
```
1. Click "Browse" to select your video file
2. Configure subtitle options (optional)
3. Click "Start Transcription"
4. Wait for processing to complete
5. Find your subtitled video as `output_with_subtitles.mp4`

#### CLI Mode
```bash
python src/main.py --mode cli --video your_video.mp4
```

### 🎨 Customization Options
- **Font Family**: Use system fonts or custom TTF files
- **Font Size**: Adjustable from 16-48px
- **Colors**: Customize text and highlight colors
- **Positioning**: Adjust bottom padding
- **Mode**: Choose between word-by-word or line-by-line

### 🆘 Troubleshooting

#### FFmpeg Issues
- **Windows**: Install via winget or chocolatey
- **macOS**: Install via Homebrew: `brew install ffmpeg`
- **Linux**: Use your package manager: `sudo apt install ffmpeg`

#### Python Issues
- Ensure Python 3.8+ is installed and in PATH
- On Windows: reinstall Python with "Add to PATH" checked
- On macOS: use `python3` instead of `python`

#### Memory Issues
- Close other applications during processing
- Use shorter video clips for testing
- Ensure 4GB+ RAM available

### 📧 Support
For issues and feature requests, please check our documentation or create an issue on our repository.

### 📄 License
This software is provided as-is for personal and educational use.

---
Made with ❤️ for content creators worldwide
"""

    with open(dist_folder / "INSTALL.md", "w", encoding="utf-8") as f:
        f.write(readme_content)

def create_zip_package(dist_folder):
    """Create a ZIP package for distribution"""
    system = platform.system().lower()
    arch = platform.machine().lower()
    
    if "arm" in arch or "aarch64" in arch:
        arch_suffix = "arm64"
    elif "x86_64" in arch or "amd64" in arch:
        arch_suffix = "x64"
    else:
        arch_suffix = arch
    
    zip_name = f"{APP_NAME}-v{VERSION}-{system}-{arch_suffix}.zip"
    zip_path = Path("dist") / zip_name
    
    print(f"📦 Creating package: {zip_name}")
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(dist_folder):
            for file in files:
                if file.endswith('.zip'):
                    continue  # Don't include the zip itself
                
                file_path = os.path.join(root, file)
                arc_path = os.path.relpath(file_path, dist_folder)
                zipf.write(file_path, arc_path)
    
    return zip_path

def create_windows_installer():
    """Create Windows installer using NSIS (if available)"""
    if platform.system().lower() != "windows":
        return None
    
    # Check if NSIS is available
    try:
        subprocess.run(["makensis", "/VERSION"], capture_output=True, check=True)
        print("🔧 NSIS found, creating Windows installer...")
        
        # Create NSIS script
        nsis_script = f"""
!define APP_NAME "{APP_NAME}"
!define APP_VERSION "{VERSION}"
!define PUBLISHER "AI Video Transcription Studio"
!define WEB_SITE "https://github.com/yourusername/ai-video-transcription"

!include "MUI2.nsh"

Name "${{APP_NAME}}"
OutFile "dist\\${{APP_NAME}}-v${{APP_VERSION}}-windows-installer.exe"
InstallDir "$PROGRAMFILES\\${{APP_NAME}}"

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

!insertmacro MUI_LANGUAGE "English"

Section "MainSection" SEC01
    SetOutPath "$INSTDIR"
    File /r "dist\\${{APP_NAME}}-v${{APP_VERSION}}-windows-x64\\*"
    
    CreateDirectory "$SMPROGRAMS\\${{APP_NAME}}"
    CreateShortCut "$SMPROGRAMS\\${{APP_NAME}}\\${{APP_NAME}}.lnk" "$INSTDIR\\run_app.bat"
    CreateShortCut "$DESKTOP\\${{APP_NAME}}.lnk" "$INSTDIR\\run_app.bat"
    
    WriteUninstaller "$INSTDIR\\uninstall.exe"
SectionEnd

Section "Uninstall"
    RMDir /r "$INSTDIR"
    RMDir /r "$SMPROGRAMS\\${{APP_NAME}}"
    Delete "$DESKTOP\\${{APP_NAME}}.lnk"
SectionEnd
"""
        
        with open("installer.nsi", "w") as f:
            f.write(nsis_script)
        
        # Run NSIS
        result = subprocess.run(["makensis", "installer.nsi"], capture_output=True)
        if result.returncode == 0:
            print("✅ Windows installer created successfully")
            os.remove("installer.nsi")
            return True
        else:
            print(f"❌ NSIS compilation failed: {result.stderr.decode()}")
            return False
            
    except subprocess.CalledProcessError:
        print("⚠️  NSIS not found - skipping Windows installer creation")
        return False

def main():
    """Main build process"""
    print(f"🏗️  Building {APP_NAME} v{VERSION} Distribution")
    print("=" * 50)
    
    system = platform.system()
    print(f"🖥️  Target System: {system}")
    print(f"🏗️  Architecture: {platform.machine()}")
    
    # Create distribution folder
    dist_folder = create_distribution_folder()
    
    # Copy source files
    copy_source_files(dist_folder)
    
    # Create installation readme
    create_installer_readme(dist_folder)
    
    # Create ZIP package
    zip_path = create_zip_package(dist_folder)
    
    # Create platform-specific installers
    if system == "Windows":
        create_windows_installer()
    
    print("\n✅ Build completed successfully!")
    print(f"📦 Package created: {zip_path}")
    print(f"📁 Distribution folder: {dist_folder}")
    
    # Show package info
    zip_size = os.path.getsize(zip_path) / (1024 * 1024)  # MB
    print(f"📊 Package size: {zip_size:.1f} MB")
    
    print("\n🚀 Ready for distribution!")

if __name__ == "__main__":
    main()
