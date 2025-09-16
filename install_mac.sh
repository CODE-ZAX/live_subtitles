#!/bin/bash

# AI Video Transcription Studio - macOS Installer
# This script installs the application and all dependencies on macOS

set -e  # Exit on any error

echo "=========================================="
echo "AI Video Transcription Studio - Installer"
echo "=========================================="
echo

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅${NC} $1"
}

print_error() {
    echo -e "${RED}❌${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠️${NC} $1"
}

print_info() {
    echo -e "${BLUE}🔄${NC} $1"
}

# Check if Python is installed
print_info "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed"
    echo "📋 Please install Python 3.8+ from:"
    echo "   • Official installer: https://python.org"
    echo "   • Homebrew: brew install python"
    echo "   • Xcode Command Line Tools: xcode-select --install"
    exit 1
fi

print_status "Python found: $(python3 --version)"

# Check if we're in the right directory
if [ ! -d "src" ]; then
    print_error "Please run this script from the application root directory"
    echo "The script should be in the same folder as the 'src' directory"
    exit 1
fi

# Check for Xcode Command Line Tools (needed for some Python packages)
print_info "Checking development tools..."
if ! xcode-select -p &> /dev/null; then
    print_warning "Xcode Command Line Tools not found"
    echo "📋 Installing Xcode Command Line Tools (required for compilation)..."
    xcode-select --install
    echo "⏳ Please complete the Xcode Command Line Tools installation and run this script again"
    exit 1
fi

print_status "Development tools found"

# Make the script executable
chmod +x "$0"

echo
print_info "Starting installation..."
echo

# Run the Python setup script
if python3 setup.py; then
    print_status "Installation completed successfully!"
else
    print_error "Installation failed"
    exit 1
fi

# Create a run script for easy launching
cat > run_app.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
./venv/bin/python src/main.py
EOF

chmod +x run_app.sh

print_status "Created run_app.sh for easy launching"

echo
echo "🎉 Installation completed!"
echo
echo "📋 You can now:"
echo "   1. Use the application bundle on your Desktop"
echo "   2. Or run: ./run_app.sh"
echo "   3. Or run: python3 src/main.py"
echo

# Check if Homebrew is installed for FFmpeg
if ! command -v brew &> /dev/null; then
    echo
    print_warning "Homebrew not found"
    echo "📋 For automatic FFmpeg installation, consider installing Homebrew:"
    echo "   /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
    echo "   Then run: brew install ffmpeg"
    echo
fi

echo "✨ AI Video Transcription Studio is ready to use!"
