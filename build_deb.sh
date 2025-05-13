#!/bin/bash

# Script to build the PhotoGlimmer .deb package
set -e

# Set version manually
VERSION="0.4.0"
echo "Building PhotoGlimmer version $VERSION"

# Create package directory structure
PKG_DIR="photoglimmer_${VERSION}"
rm -rf "$PKG_DIR"
mkdir -p "$PKG_DIR/DEBIAN"
mkdir -p "$PKG_DIR/usr/bin"
mkdir -p "$PKG_DIR/usr/share/applications"
mkdir -p "$PKG_DIR/usr/share/icons/hicolor/scalable/apps"
mkdir -p "$PKG_DIR/usr/lib/python3/dist-packages"

# Create control file
cat > "$PKG_DIR/DEBIAN/control" << EOF
Package: photoglimmer
Version: $VERSION
Section: graphics
Priority: optional
Architecture: amd64
Depends: python3 (>= 3.8), python3-pip, python3-numpy, python3-opencv
Maintainer: Rahul Singh <codecliff@users.noreply.github.com>
Description: AI powered photo editor to tweak illumination on people
 PhotoGlimmer is an AI-powered photo editor that lets you precisely adjust
 illumination on people, leaving the background untouched.
EOF

# Create postinst script
cat > "$PKG_DIR/DEBIAN/postinst" << EOF
#!/bin/bash
set -e

# Instalar dependencias de Python específicas
pip3 install "numpy==1.24.3" "opencv-contrib-python==4.8.1.78" "mediapipe==0.10.7" "pyqtdarktheme~=2.1.0" "splines~=0.3.0" "piexif~=1.1.3"

exit 0
EOF

# Make postinst executable
chmod +x "$PKG_DIR/DEBIAN/postinst"

# Create launcher script
cat > "$PKG_DIR/usr/bin/photoglimmer" << EOF
#!/bin/bash
python3 -m photoglimmer
EOF

# Make launcher executable
chmod +x "$PKG_DIR/usr/bin/photoglimmer"

# Create desktop file
cat > "$PKG_DIR/usr/share/applications/photoglimmer.desktop" << EOF
[Desktop Entry]
Version=$VERSION
Type=Application
Name=PhotoGlimmer
Comment=AI powered photo editor to tweak illumination on people
Exec=/usr/bin/photoglimmer
Icon=photoglimmer
Categories=Graphics;Photography;
Terminal=false
StartupNotify=true
EOF

# Copy Python package
cp -r src/photoglimmer "$PKG_DIR/usr/lib/python3/dist-packages/"

# Copy icon if it exists
if [ -f "src/photoglimmer/resources/icons/photoglimmer.svg" ]; then
  cp "src/photoglimmer/resources/icons/photoglimmer.svg" "$PKG_DIR/usr/share/icons/hicolor/scalable/apps/"
fi

# Build the package
dpkg-deb --build "$PKG_DIR"

echo "Package built: ${PKG_DIR}.deb"
