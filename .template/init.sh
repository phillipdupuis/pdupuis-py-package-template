#!/usr/bin/env bash
# initialize_template.sh - Replace placeholders in a Python package template
set -euo pipefail

# Display usage information
function show_usage() {
    echo "Usage: $0 -n PACKAGE_NAME [-a AUTHOR] [-e EMAIL] [-d DESCRIPTION] [-g GITHUB_USERNAME]"
    echo ""
    echo "Arguments:"
    echo "  -n, --name         Package name (required, snake_case recommended)"
    echo "  -a, --author       Author name (default: current git user.name)"
    echo "  -e, --email        Author email (default: current git user.email)"
    echo "  -d, --description  Short package description (default: 'A Python package')"
    echo "  -g, --github       GitHub username (default: derived from email or current user)"
    echo "  -h, --help         Show this help message"
    exit 1
}

# Parse command-line arguments
PACKAGE_NAME=""
AUTHOR=""
EMAIL=""
DESCRIPTION="A Python package"
GITHUB_USERNAME=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -n|--name)
            PACKAGE_NAME="$2"
            shift 2
            ;;
        -a|--author)
            AUTHOR="$2"
            shift 2
            ;;
        -e|--email)
            EMAIL="$2"
            shift 2
            ;;
        -d|--description)
            DESCRIPTION="$2"
            shift 2
            ;;
        -g|--github)
            GITHUB_USERNAME="$2"
            shift 2
            ;;
        -h|--help)
            show_usage
            ;;
        *)
            echo "Error: Unknown option $1"
            show_usage
            ;;
    esac
done

# Check for required arguments
if [[ -z "$PACKAGE_NAME" ]]; then
    echo "Error: Package name is required"
    show_usage
fi

# Try to get git info if not provided
if [[ -z "$AUTHOR" ]]; then
    AUTHOR=$(git config --get user.name 2>/dev/null || echo "Your Name")
fi

if [[ -z "$EMAIL" ]]; then
    EMAIL=$(git config --get user.email 2>/dev/null || echo "your.email@example.com")
fi

if [[ -z "$GITHUB_USERNAME" ]]; then
    # Try to extract username from email or use system username
    GITHUB_USERNAME=$(echo "$EMAIL" | cut -d '@' -f1 2>/dev/null || whoami)
fi

# Generate a Python-compatible package name (for imports)
IMPORT_NAME=$(echo "$PACKAGE_NAME" | tr '-' '_')

# Keep it simple - use the same name for package title
PACKAGE_TITLE="$IMPORT_NAME"

# Current year for license
YEAR=$(date +"%Y")

# Print settings for confirmation
echo "Initializing template with:"
echo "  Package Name: $PACKAGE_NAME"
echo "  Import Name: $IMPORT_NAME"
echo "  Package Title: $PACKAGE_TITLE"
echo "  Author: $AUTHOR"
echo "  Email: $EMAIL"
echo "  Description: $DESCRIPTION"
echo "  GitHub Username: $GITHUB_USERNAME"
echo "  Year: $YEAR"
echo ""
echo "Press Enter to continue or Ctrl+C to cancel..."
read -r

# Define placeholders to replace in files
declare -A replacements=(
    ["${package_name}"]="$PACKAGE_NAME"
    ["${import_name}"]="$IMPORT_NAME"
    ["${package_title}"]="$PACKAGE_TITLE"
    ["${author}"]="$AUTHOR"
    ["${email}"]="$EMAIL"
    ["${description}"]="$DESCRIPTION"
    ["${github_username}"]="$GITHUB_USERNAME"
    ["${year}"]="$YEAR"
)

# Function to replace placeholders in file contents
replace_in_file() {
    local file="$1"
    echo "Processing file content: $file"
    
    # Make a temporary file
    local temp_file="$file.temp"
    cp "$file" "$temp_file"
    
    # Replace each placeholder
    for placeholder in "${!replacements[@]}"; do
        local replacement="${replacements[$placeholder]}"
        sed -i "s|$placeholder|$replacement|g" "$temp_file"
    done
    
    # Replace the original file
    mv "$temp_file" "$file"
}

# Function to rename files with placeholders
rename_files() {
    local dir="$1"
    
    # Find files with placeholders in their names
    find "$dir" -type f -name "*\${*}*" | while read -r file; do
        local new_name="$file"
        
        # Replace each placeholder in the filename
        for placeholder in "${!replacements[@]}"; do
            local replacement="${replacements[$placeholder]}"
            new_name="${new_name//$placeholder/$replacement}"
        done
        
        if [[ "$file" != "$new_name" ]]; then
            echo "Renaming: $file -> $new_name"
            # Create directory if it doesn't exist
            mkdir -p "$(dirname "$new_name")"
            mv "$file" "$new_name"
        fi
    done
    
    # Also rename directories (starting from deepest ones to avoid path issues)
    find "$dir" -depth -type d -name "*\${*}*" | while read -r directory; do
        local new_name="$directory"
        
        # Replace each placeholder in the directory name
        for placeholder in "${!replacements[@]}"; do
            local replacement="${replacements[$placeholder]}"
            new_name="${new_name//$placeholder/$replacement}"
        done
        
        if [[ "$directory" != "$new_name" ]]; then
            echo "Renaming directory: $directory -> $new_name"
            # Create parent directory if it doesn't exist
            mkdir -p "$(dirname "$new_name")"
            mv "$directory" "$new_name"
        fi
    done
}

# Main execution
echo "Step 1: Replacing placeholders in file contents..."
find . -type f -not -path "*/\.git/*" -not -path "*/\.github/*" -not -name "initialize_template.sh" | while read -r file; do
    # Skip binary files and the script itself
    if [[ -f "$file" && ! -x "$file" ]]; then
        replace_in_file "$file"
    fi
done

echo "Step 2: Renaming files and directories with placeholders..."
rename_files "."

# Remove this initialization script itself if we're in the template repo
if [[ -f "initialize_template.sh" ]]; then
    echo "Step 3: Removing initialization script..."
    rm "initialize_template.sh"
fi

echo "Step 4: Creating initial git repository..."
if [[ ! -d ".git" ]]; then
    git init
    git add .
    git commit -m "Initial commit from template"
fi

echo "Template initialization complete!"
echo "Your Python package '$PACKAGE_NAME' is ready to use."