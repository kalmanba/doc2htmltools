#!/bin/bash

set -e  # Exit immediately on any command failure

# Function for error messages
error_exit() {
    echo "Error: $1" >&2
    exit 1
}

# Step 1: Create /usr/bin/doc2htmltools
echo "Creating directory /usr/bin/doc2htmltools..."
sudo mkdir -p /usr/bin/doc2htmltools || error_exit "Failed to create /usr/bin/doc2htmltools"

# Step 2: Copy the doc2htmltools file
echo "Copying doc2htmltools to /usr/bin/doc2htmltools..."
if [[ ! -f ./doc2htmltools ]]; then
    error_exit "File 'doc2htmltools' not found in current directory."
fi
sudo cp ./doc2htmltools /usr/bin/doc2htmltools/ || error_exit "Failed to copy doc2htmltools"

# Step 3: Create /home/$USER/.d2htools
echo "Creating directory /home/$USER/.d2htools..."
mkdir -p "/home/$USER/.d2htools" || error_exit "Failed to create /home/$USER/.d2htools"

# Step 4: Create empty config.json
echo "Creating empty config.json..."
touch "/home/$USER/.d2htools/config.json" || error_exit "Failed to create config.json"

# Step 5: Create ~/bin if it doesn’t exist
echo "Creating /home/$USER/bin directory..."
mkdir -p "/home/$USER/bin" || error_exit "Failed to create /home/$USER/bin"

# Step 6: Create symbolic link
SYMLINK_PATH="/home/$USER/bin/doc2htmltools"
TARGET_PATH="/usr/bin/doc2htmltools/doc2htmltools"

echo "Creating symbolic link $SYMLINK_PATH -> $TARGET_PATH..."
if [[ -L "$SYMLINK_PATH" || -e "$SYMLINK_PATH" ]]; then
    # If something already exists there, check if it's the correct link
    if [[ -L "$SYMLINK_PATH" && "$(readlink -f "$SYMLINK_PATH")" == "$TARGET_PATH" ]]; then
        echo "Symlink already exists and is correct."
    else
        error_exit "A file or incorrect symlink already exists at $SYMLINK_PATH. Remove it manually to proceed."
    fi
else
    ln -s "$TARGET_PATH" "$SYMLINK_PATH" || error_exit "Failed to create symlink"
fi

# Step 7: Ensure ~/bin is in PATH for future sessions
if [[ ":$PATH:" != *":$HOME/bin:"* ]]; then
    SHELL_NAME=$(basename "$SHELL")
    case "$SHELL_NAME" in
        bash)
            PROFILE_FILE="$HOME/.bashrc"
            ;;
        zsh)
            PROFILE_FILE="$HOME/.zshrc"
            ;;
        *)
            PROFILE_FILE="$HOME/.profile"
            ;;
    esac
    echo 'export PATH="$HOME/bin:$PATH"' >> "$PROFILE_FILE"
    echo "Added ~/bin to PATH in $PROFILE_FILE"
    echo "To apply changes now, run: source \"$PROFILE_FILE\""
else
    echo "~/bin is already in PATH."
fi

echo "All operations completed successfully."
