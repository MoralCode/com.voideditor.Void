# Cursor AI - Building a restrictive Flatpak

This repository contains the necessary files and automation to build a
restrictive, sandboxed Flatpak for the [Cursor AI](https://cursor.sh/) code
editor.

The primary goal is to provide a secure environment for running Cursor by
limiting its access to the host system. The build process is automated with a
`Makefile`, requiring only the version number and download URL for a new release
to build and package it.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Project Structure](#project-structure)
- [How to Build](#how-to-build)
- [Makefile Targets](#makefile-targets)
- [Post-Install Customization with Flatseal](#post-install-customization-with-flatseal)

## Prerequisites

Before you can build the Flatpak, you must have the following tools installed on
your system:

- `flatpak`
- `flatpak-builder`
- `make`
- `wget`

You also need to have the Flathub remote added to your Flatpak installation:

```bash
flatpak remote-add --if-not-exists flathub [https://flathub.org/repo/flathub.flatpakrepo](https://flathub.org/repo/flathub.flatpakrepo)
```

## Project Structure

This repository contains the following files:

- **`Makefile`**: The main script that automates the entire download, build, and
installation process.
- **`com.cursor.App.yml`**: The Flatpak manifest. This is the core blueprint
that tells `flatpak-builder` how to construct the application, including its
dependencies, sources, and sandbox permissions.
- **`com.cursor.App.appdata.xml`**: AppStream metadata for the application. This
file provides the information (name, description, version history) that software
centers like GNOME Software and KDE Discover use to display the application.
- **`com.cursor.App.desktop`**: The `.desktop` file that allows the application
to be launched from your desktop environment's application menu.

## How to Build

The build process is managed entirely by the `Makefile`.

1. **Find the Release URL and Version:**
Go to the [Cursor Download History](https://github.com/oslook/cursor-ai-downloads)
or the official website to find the download URL for the Linux AppImage of the
version you want to package.

2. **Run the Build Command:**
From the root of this project directory, run the `make` command, providing
the `VERSION` and `CURSOR_URL` as arguments.

    **Example:**

    ```bash
    make build VERSION=x.y.z
    CURSOR_URL="URL_FOR_XYZ_RELEASE_OBTAINED_FROM_WEBSITE"
    ```

    This command will:
    - Download the specified AppImage.
    - Make it executable and extract its contents.
    - Update the version number in the `appdata.xml` file.
    - Run `flatpak-builder` to create the Flatpak in a `build-dir` directory.

3. **Install the Flatpak:**
Once the build is complete, you can install it for your user with:

    ```bash
    make install
    ```

4. **Run the Application:**

Once installed, you can normally run your application with:

   ```bash
   flatpak run com.anysphere.Cursor
   ```

## Makefile Targets

The `Makefile` provides several convenient targets:

- `make build`: Downloads the AppImage and builds the Flatpak. (Requires
`VERSION` and `CURSOR_URL`).
- `make install`: Installs the locally built Flatpak for the current user.
- `make run`: Runs the installed Flatpak application.
- `make uninstall`: Removes the Flatpak from your system.
- `make clean`: Removes all build artifacts, including `build-dir`, `repo`, the
downloaded AppImage, and the extracted `squashfs-root`.

## Post-Install Customization with Flatseal

For easy, on-the-fly permission management *without* rebuilding, you can use
**Flatseal**, a graphical utility for managing Flatpak permissions.

1. **Install Flatseal:**

    ```bash
    flatpak install flathub com.github.tchx84.Flatseal
    ```

2. **Launch Flatseal** and select "Cursor" from the list of applications.
3. You can now toggle permissions for filesystem access, network sockets, device
access, and more. Changes are applied instantly.

## Roadmap

0. Allow operating the flatpak without "--share-network": The work for this is
ongoing with the slirp4netns_helper.py script that is meant to inject networking
to the isolate network namespace of the Flatpak.
1. Automate download of the latest version
2. Automate builds with github actions.
