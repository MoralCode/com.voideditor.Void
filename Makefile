# Makefile for building the Cursor Flatpak

# --- Variables ---
APP_ID := com.voideditor.Void
MANIFEST := $(APP_ID).yml
APPDATA := $(APP_ID).appdata.xml
DESKTOP := $(APP_ID).desktop
BUILD_DIR := build-dir
SQUASHFS_ROOT := squashfs-root
ARCH ?= x86_64


APPIMAGE_FILE = $(notdir $(CURSOR_URL))

.PHONY: all build install run clean uninstall

# --- Main Targets ---

all: build

# Builds the Flatpak. Depends on the AppImage being extracted.
	@echo "--> Building the Flatpak..."
	# Update the version in the appdata file before building
	flatpak-builder $(BUILD_DIR) $(MANIFEST) --force-clean
	@echo "--> Build complete."

# Installs the Flatpak for the current user.
install: build
	@echo "--> Installing the Flatpak for the current user..."
	flatpak-builder --user --install --force-clean $(BUILD_DIR) $(MANIFEST)
	@echo "--> Installation complete."

# Uninstalls the application.
uninstall:
	@echo "--> Uninstalling Cursor..."
	flatpak uninstall $(APP_ID)

# --- Helper Targets ---

# This target handles downloading and extracting the AppImage.
# It's triggered by the 'build' target.

Cursor-$(VERSION)-$(ARCH).AppImage:
	@echo "--> Preparing AppImage..."
	@echo "    Downloading from: $(CURSOR_URL)"
	wget -O $(APPIMAGE_FILE) "$(CURSOR_URL)"
	@echo "    Making executable..."
	chmod +x $(APPIMAGE_FILE)

$(SQUASHFS_ROOT): Cursor-$(VERSION)-$(ARCH).AppImage
	@echo "    Extracting AppImage..."
	./$(APPIMAGE_FILE) --appimage-extract
	@echo "    Extraction complete. Extracted to '$(SQUASHFS_ROOT)'."

# Cleans up all generated files and directories.
clean:
	@echo "--> Cleaning up..."
	rm -rf $(BUILD_DIR)
	rm -rf $(SQUASHFS_ROOT)
	rm -f *.AppImage
	@echo "--> Cleanup complete."
