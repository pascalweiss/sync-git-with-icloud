#!/usr/bin/env bash

# Exit immediately if a command exits with non-zero status
set -e

# Generic version update script for any project

show_help() {
  echo "Usage: $(basename "$0") [OPTIONS] [VERSION]"
  echo
  echo "Update version numbers across project files to trigger a new build."
  echo
  echo "OPTIONS:"
  echo "  -h, --help    Show this help message and exit"
  echo
  echo "VERSION:"
  echo "  If provided, must be in format x.y.z (e.g., 0.1.7)"
  echo "  If not provided, the script will show the current version"
  echo
  echo "EXAMPLES:"
  echo "  $(basename "$0") 0.2.0    # Set version to 0.2.0"
  echo "  $(basename "$0") --help   # Display this help message"
  echo
}

# Get the directory of this script
DIR=$(dirname "$0")/..
cd "$DIR" || exit 1

# Function to validate version format
validate_version() {
    local version=$1
    if ! [[ $version =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        echo "Error: Version must be in format x.y.z (e.g., 0.1.5)"
        exit 1
    fi
}

# Function to update version in a file using sed
update_version_in_file() {
    local file=$1
    local pattern=$2
    local replacement=$3
    
    if [ -f "$file" ]; then
        echo "Updating $file..."
        sed -i "$pattern" "$file"
    else
        echo "Skipping $file (not found)"
    fi
}

# Detect files that might contain version information
VERSION_FILES=()

# Common CI configuration files
[ -f ".gitlab-ci.yml" ] && VERSION_FILES+=(".gitlab-ci.yml")
[ -f ".github/workflows/main.yml" ] && VERSION_FILES+=(".github/workflows/main.yml")

# Package files
[ -f "setup.py" ] && VERSION_FILES+=("setup.py")
[ -f "pyproject.toml" ] && VERSION_FILES+=("pyproject.toml")
[ -f "package.json" ] && VERSION_FILES+=("package.json")

# Helm chart files
[ -f "chart/Chart.yaml" ] && VERSION_FILES+=("chart/Chart.yaml")
[ -f "chart/values.yaml" ] && VERSION_FILES+=("chart/values.yaml")

# Docker/container files
[ -f "Dockerfile" ] && VERSION_FILES+=("Dockerfile")
[ -f ".env" ] && VERSION_FILES+=(".env")
[ -f ".env.docker" ] && VERSION_FILES+=(".env.docker")

# Find current version from any of the files
CURRENT_VERSION=""

# Try to get version from CI files first
if [ -f ".gitlab-ci.yml" ]; then
    CURRENT_VERSION=$(grep -oP 'TAG: \K[0-9]+\.[0-9]+\.[0-9]+' .gitlab-ci.yml 2>/dev/null || echo "")
fi

if [ -z "$CURRENT_VERSION" ] && [ -f "pyproject.toml" ]; then
    CURRENT_VERSION=$(grep -oP 'version = "\K[0-9]+\.[0-9]+\.[0-9]+' pyproject.toml 2>/dev/null || echo "")
fi

if [ -z "$CURRENT_VERSION" ] && [ -f "setup.py" ]; then
    CURRENT_VERSION=$(grep -oP 'version="\K[0-9]+\.[0-9]+\.[0-9]+' setup.py 2>/dev/null || echo "")
fi

if [ -z "$CURRENT_VERSION" ] && [ -f "package.json" ]; then
    CURRENT_VERSION=$(grep -oP '"version": "\K[0-9]+\.[0-9]+\.[0-9]+' package.json 2>/dev/null || echo "")
fi

if [ -z "$CURRENT_VERSION" ] && [ -f "chart/Chart.yaml" ]; then
    CURRENT_VERSION=$(grep -oP 'version: \K[0-9]+\.[0-9]+\.[0-9]+' chart/Chart.yaml 2>/dev/null || echo "")
fi

if [ -z "$CURRENT_VERSION" ]; then
    echo "Warning: Could not determine current version from any files."
    CURRENT_VERSION="0.0.0"
else
    echo "Current version: $CURRENT_VERSION"
fi

# Process command-line arguments
if [ $# -eq 0 ]; then
    echo
    echo "Please provide a new version number to update the project."
    echo "Example: $0 0.1.7"
    echo
    echo "For more information, use: $0 --help"
    exit 0
fi

# Check for help parameter
if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    show_help
    exit 0
fi

# Use provided version
NEW_VERSION=$1
validate_version "$NEW_VERSION"

echo "New version will be: $NEW_VERSION"

# Update detected files
for file in "${VERSION_FILES[@]}"; do
    case "$file" in
        ".gitlab-ci.yml")
            update_version_in_file "$file" "s/TAG: [0-9]\+\.[0-9]\+\.[0-9]\+/TAG: $NEW_VERSION/" "$NEW_VERSION"
            ;;
        ".github/workflows/main.yml")
            update_version_in_file "$file" "s/version: [0-9]\+\.[0-9]\+\.[0-9]\+/version: $NEW_VERSION/" "$NEW_VERSION"
            ;;
        "setup.py")
            update_version_in_file "$file" "s/version=\"[0-9]\+\.[0-9]\+\.[0-9]\+\"/version=\"$NEW_VERSION\"/" "$NEW_VERSION"
            ;;
        "pyproject.toml")
            update_version_in_file "$file" "s/version = \"[0-9]\+\.[0-9]\+\.[0-9]\+\"/version = \"$NEW_VERSION\"/" "$NEW_VERSION"
            ;;
        "package.json")
            update_version_in_file "$file" "s/\"version\": \"[0-9]\+\.[0-9]\+\.[0-9]\+\"/\"version\": \"$NEW_VERSION\"/" "$NEW_VERSION"
            ;;
        "chart/Chart.yaml")
            update_version_in_file "$file" "s/version: [0-9]\+\.[0-9]\+\.[0-9]\+/version: $NEW_VERSION/" "$NEW_VERSION"
            ;;
        "chart/values.yaml")
            update_version_in_file "$file" "s/tag: \"[0-9]\+\.[0-9]\+\.[0-9]\+\"/tag: \"$NEW_VERSION\"/" "$NEW_VERSION"
            ;;
        "Dockerfile")
            update_version_in_file "$file" "s/VERSION=\"[0-9]\+\.[0-9]\+\.[0-9]\+\"/VERSION=\"$NEW_VERSION\"/" "$NEW_VERSION"
            ;;
        ".env")
            update_version_in_file "$file" "s/export TAG=\"[0-9]\+\.[0-9]\+\.[0-9]\+\"/export TAG=\"$NEW_VERSION\"/" "$NEW_VERSION"
            ;;
        ".env.docker")
            update_version_in_file "$file" "s/TAG=[0-9]\+\.[0-9]\+\.[0-9]\+/TAG=$NEW_VERSION/" "$NEW_VERSION"
            ;;
    esac
done

echo "Version updated successfully to $NEW_VERSION!"
echo ""
echo "To complete the update, commit and push the changes:"
echo "git add ${VERSION_FILES[*]}"
echo "git commit -m \"Bump version to $NEW_VERSION\""
echo "git push"