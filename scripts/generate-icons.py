#!/usr/bin/env python3
"""
EchoNote Icon Generator
Generates all required app icons from source images.
"""

import os
import shutil
import subprocess
from pathlib import Path
from PIL import Image

# Paths
ROOT_DIR = Path(__file__).parent.parent
ASSETS_DIR = ROOT_DIR / "assets"
ICONS_DIR = ROOT_DIR / "apps/desktop/src-tauri/icons"
TRAY_ICONS_DIR = ROOT_DIR / "plugins/tray/icons"

# Source files
MAIN_ICON_SRC = ASSETS_DIR / "echonote.png"
MENU_BAR_SRC = ASSETS_DIR / "echonote-1.png"


def crop_menu_bar_icon():
    """Crop and process the menu bar icon from echonote-1.png"""
    print("Processing menu bar icon...")

    img = Image.open(MENU_BAR_SRC)
    width, height = img.size
    print(f"  Source size: {width}x{height}")

    # The left half contains the dark icon on white background
    # Crop only the upper portion to exclude text at the bottom
    # Original: 1536x1024, left half: 768x1024
    # Text starts around y=960, so we only take the top 900 pixels
    left_half = img.crop((0, 0, width // 2, 900))

    # Convert to RGBA
    left_half = left_half.convert("RGBA")

    # Find the bounding box of the non-white content
    pixels = left_half.load()
    min_x, min_y, max_x, max_y = left_half.width, left_half.height, 0, 0

    for y in range(left_half.height):
        for x in range(left_half.width):
            r, g, b, a = pixels[x, y]
            # If not white (with some tolerance)
            if r < 240 or g < 240 or b < 240:
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                max_x = max(max_x, x)
                max_y = max(max_y, y)

    print(f"  Icon bounds: ({min_x}, {min_y}) to ({max_x}, {max_y})")

    # Add padding
    padding = 20
    min_x = max(0, min_x - padding)
    min_y = max(0, min_y - padding)
    max_x = min(left_half.width, max_x + padding)
    max_y = min(left_half.height, max_y + padding)

    # Crop to the icon area
    icon_crop = left_half.crop((min_x, min_y, max_x, max_y))

    # Remove white background (make it transparent)
    pixels = icon_crop.load()
    for y in range(icon_crop.height):
        for x in range(icon_crop.width):
            r, g, b, a = pixels[x, y]
            # If white or near-white, make transparent
            if r > 240 and g > 240 and b > 240:
                pixels[x, y] = (r, g, b, 0)

    # Make it square by adding transparent padding
    size = max(icon_crop.width, icon_crop.height)
    square_icon = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    paste_x = (size - icon_crop.width) // 2
    paste_y = (size - icon_crop.height) // 2
    square_icon.paste(icon_crop, (paste_x, paste_y))

    # Resize to 160x160 (matching current tray_default.png)
    final_icon = square_icon.resize((160, 160), Image.Resampling.LANCZOS)

    # Save
    TRAY_ICONS_DIR.mkdir(parents=True, exist_ok=True)
    output_path = TRAY_ICONS_DIR / "tray_default.png"
    final_icon.save(output_path, "PNG")
    print(f"  Saved: {output_path}")

    return final_icon


def crop_to_content(img: Image.Image) -> Image.Image:
    """Crop image to its actual content, removing surrounding whitespace/transparency.

    Args:
        img: Source image with potential whitespace around content

    Returns:
        Cropped image containing only the content, made square
    """
    img = img.convert("RGBA")
    pixels = img.load()
    width, height = img.size

    # Find bounding box of non-white/non-transparent content
    min_x, min_y, max_x, max_y = width, height, 0, 0

    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]
            # If not white/transparent (has actual content)
            if a > 10 and not (r > 250 and g > 250 and b > 250):
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                max_x = max(max_x, x)
                max_y = max(max_y, y)

    # Crop to content
    content = img.crop((min_x, min_y, max_x + 1, max_y + 1))

    # Make it square
    content_width, content_height = content.size
    size = max(content_width, content_height)
    square = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    paste_x = (size - content_width) // 2
    paste_y = (size - content_height) // 2
    square.paste(content, (paste_x, paste_y), content)

    return square


def add_padding_to_icon(img: Image.Image, padding_percent: float = 0.1) -> Image.Image:
    """Add padding around the icon content for macOS style icons.

    Args:
        img: Source image (should be cropped to content first)
        padding_percent: Padding as percentage of canvas size (0.1 = 10% on each side)

    Returns:
        New image with padding added
    """
    width, height = img.size

    # Calculate new content size (content will be smaller to add padding)
    content_size = int(width * (1 - 2 * padding_percent))

    # Resize content to fit within padded area
    content = img.resize((content_size, content_size), Image.Resampling.LANCZOS)

    # Create new canvas with transparent background
    new_img = Image.new("RGBA", (width, height), (0, 0, 0, 0))

    # Calculate position to center the content
    offset = (width - content_size) // 2

    # Paste content centered
    new_img.paste(content, (offset, offset), content if content.mode == 'RGBA' else None)

    return new_img


def generate_desktop_icons(variant: str = "stable"):
    """Generate all desktop icons for a given variant"""
    print(f"\nGenerating desktop icons for {variant}...")

    variant_dir = ICONS_DIR / variant
    variant_dir.mkdir(parents=True, exist_ok=True)

    # Load source image and crop to actual content
    src_img_raw = Image.open(MAIN_ICON_SRC).convert("RGBA")
    print(f"  Raw source size: {src_img_raw.size}")

    # First crop to remove whitespace around the icon
    src_img = crop_to_content(src_img_raw)
    print(f"  Cropped to content: {src_img.size}")

    # Add padding to source image for macOS-style icons
    # macOS icons typically have ~10% padding on each side
    src_img_padded = add_padding_to_icon(src_img, padding_percent=0.10)
    print(f"  Added 10% padding for macOS-style icons")

    # Standard sizes for desktop
    standard_sizes = {
        "icon.png": 512,
        "16.png": 16,
        "32x32.png": 32,
        "64x64.png": 64,
        "128x128.png": 128,
        "128x128@2x.png": 256,
    }

    # Windows Square logos (Windows icons don't need padding)
    square_sizes = {
        "Square30x30Logo.png": 30,
        "Square44x44Logo.png": 44,
        "Square71x71Logo.png": 71,
        "Square89x89Logo.png": 89,
        "Square107x107Logo.png": 107,
        "Square142x142Logo.png": 142,
        "Square150x150Logo.png": 150,
        "Square284x284Logo.png": 284,
        "Square310x310Logo.png": 310,
        "StoreLogo.png": 50,
    }

    # Generate standard icons with padding
    for filename, size in standard_sizes.items():
        resized = src_img_padded.resize((size, size), Image.Resampling.LANCZOS)
        output_path = variant_dir / filename
        resized.save(output_path, "PNG")
        print(f"  Generated: {filename} ({size}x{size})")

    # Generate Windows icons without padding
    for filename, size in square_sizes.items():
        resized = src_img.resize((size, size), Image.Resampling.LANCZOS)
        output_path = variant_dir / filename
        resized.save(output_path, "PNG")
        print(f"  Generated: {filename} ({size}x{size})")

    return variant_dir


def generate_icns(variant_dir: Path):
    """Generate macOS .icns file"""
    print("\nGenerating macOS .icns file...")

    # Create iconset directory
    iconset_dir = variant_dir / "icon.iconset"
    if iconset_dir.exists():
        shutil.rmtree(iconset_dir)
    iconset_dir.mkdir()

    # Load source, crop to content, and add padding for macOS
    src_img_raw = Image.open(MAIN_ICON_SRC).convert("RGBA")
    src_img = crop_to_content(src_img_raw)
    src_img_padded = add_padding_to_icon(src_img, padding_percent=0.10)

    # Required sizes for iconset
    iconset_sizes = [
        ("icon_16x16.png", 16),
        ("icon_16x16@2x.png", 32),
        ("icon_32x32.png", 32),
        ("icon_32x32@2x.png", 64),
        ("icon_128x128.png", 128),
        ("icon_128x128@2x.png", 256),
        ("icon_256x256.png", 256),
        ("icon_256x256@2x.png", 512),
        ("icon_512x512.png", 512),
        ("icon_512x512@2x.png", 1024),
    ]

    for filename, size in iconset_sizes:
        resized = src_img_padded.resize((size, size), Image.Resampling.LANCZOS)
        resized.save(iconset_dir / filename, "PNG")

    # Convert to icns using iconutil
    icns_path = variant_dir / "icon.icns"
    result = subprocess.run(
        ["iconutil", "-c", "icns", str(iconset_dir), "-o", str(icns_path)],
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        print(f"  Generated: icon.icns")
        # Clean up iconset directory
        shutil.rmtree(iconset_dir)
    else:
        print(f"  Error generating icns: {result.stderr}")

    return icns_path


def generate_ico(variant_dir: Path):
    """Generate Windows .ico file"""
    print("\nGenerating Windows .ico file...")

    src_img_raw = Image.open(MAIN_ICON_SRC).convert("RGBA")
    src_img = crop_to_content(src_img_raw)
    ico_path = variant_dir / "icon.ico"

    # ICO file with multiple sizes (256 is the max for ICO format)
    sizes = [16, 24, 32, 48, 64, 128, 256]
    images = []

    for size in sizes:
        resized = src_img.resize((size, size), Image.Resampling.LANCZOS)
        images.append(resized)

    # Save as ICO - Pillow will include all the images in the ICO file
    # The largest image should be first for better compatibility
    images_sorted = sorted(images, key=lambda x: x.size[0], reverse=True)
    images_sorted[0].save(ico_path, format="ICO", append_images=images_sorted[1:])
    print(f"  Generated: icon.ico (sizes: {sizes})")

    return ico_path


def generate_android_icons(variant_dir: Path):
    """Generate Android icons"""
    print("\nGenerating Android icons...")

    src_img_raw = Image.open(MAIN_ICON_SRC).convert("RGBA")
    src_img = crop_to_content(src_img_raw)
    android_dir = variant_dir / "android"

    # Remove existing android directory and recreate
    if android_dir.exists():
        shutil.rmtree(android_dir)

    # Android mipmap densities
    densities = {
        "mipmap-mdpi": {"launcher": 48, "foreground": 108},
        "mipmap-hdpi": {"launcher": 72, "foreground": 162},
        "mipmap-xhdpi": {"launcher": 96, "foreground": 216},
        "mipmap-xxhdpi": {"launcher": 144, "foreground": 324},
        "mipmap-xxxhdpi": {"launcher": 192, "foreground": 432},
    }

    for density, sizes in densities.items():
        density_dir = android_dir / density
        density_dir.mkdir(parents=True, exist_ok=True)

        # ic_launcher.png
        launcher = src_img.resize(
            (sizes["launcher"], sizes["launcher"]), Image.Resampling.LANCZOS
        )
        launcher.save(density_dir / "ic_launcher.png", "PNG")

        # ic_launcher_round.png (same as launcher for now)
        launcher.save(density_dir / "ic_launcher_round.png", "PNG")

        # ic_launcher_foreground.png (larger, for adaptive icons)
        foreground = src_img.resize(
            (sizes["foreground"], sizes["foreground"]), Image.Resampling.LANCZOS
        )
        foreground.save(density_dir / "ic_launcher_foreground.png", "PNG")

        print(
            f"  Generated: {density}/ ({sizes['launcher']}x{sizes['launcher']}, fg: {sizes['foreground']}x{sizes['foreground']})"
        )


def generate_ios_icons(variant_dir: Path):
    """Generate iOS icons"""
    print("\nGenerating iOS icons...")

    src_img_raw = Image.open(MAIN_ICON_SRC).convert("RGBA")
    src_img = crop_to_content(src_img_raw)
    ios_dir = variant_dir / "ios"

    # Remove existing ios directory and recreate
    if ios_dir.exists():
        shutil.rmtree(ios_dir)
    ios_dir.mkdir(parents=True, exist_ok=True)

    # iOS icon sizes
    ios_sizes = [
        ("AppIcon-20x20@1x.png", 20),
        ("AppIcon-20x20@2x.png", 40),
        ("AppIcon-20x20@2x-1.png", 40),
        ("AppIcon-20x20@3x.png", 60),
        ("AppIcon-29x29@1x.png", 29),
        ("AppIcon-29x29@2x.png", 58),
        ("AppIcon-29x29@2x-1.png", 58),
        ("AppIcon-29x29@3x.png", 87),
        ("AppIcon-40x40@1x.png", 40),
        ("AppIcon-40x40@2x.png", 80),
        ("AppIcon-40x40@2x-1.png", 80),
        ("AppIcon-40x40@3x.png", 120),
        ("AppIcon-60x60@2x.png", 120),
        ("AppIcon-60x60@3x.png", 180),
        ("AppIcon-76x76@1x.png", 76),
        ("AppIcon-76x76@2x.png", 152),
        ("AppIcon-83.5x83.5@2x.png", 167),
        ("AppIcon-512@2x.png", 1024),
    ]

    for filename, size in ios_sizes:
        resized = src_img.resize((size, size), Image.Resampling.LANCZOS)
        resized.save(ios_dir / filename, "PNG")
        print(f"  Generated: {filename} ({size}x{size})")


def copy_to_variants(source_variant: str = "stable"):
    """Copy icons from source variant to other variants"""
    print("\nCopying icons to other variants...")

    source_dir = ICONS_DIR / source_variant
    variants = ["nightly", "pro"]

    for variant in variants:
        variant_dir = ICONS_DIR / variant
        if variant_dir.exists():
            shutil.rmtree(variant_dir)
        shutil.copytree(source_dir, variant_dir)
        print(f"  Copied to: {variant}/")


def main():
    print("=" * 50)
    print("EchoNote Icon Generator")
    print("=" * 50)

    # Step 1: Generate menu bar icon
    crop_menu_bar_icon()

    # Step 2: Generate desktop icons for stable
    variant_dir = generate_desktop_icons("stable")

    # Step 3: Generate icns (macOS)
    generate_icns(variant_dir)

    # Step 4: Generate ico (Windows)
    generate_ico(variant_dir)

    # Step 5: Generate Android icons
    generate_android_icons(variant_dir)

    # Step 6: Generate iOS icons
    generate_ios_icons(variant_dir)

    # Step 7: Copy to other variants
    copy_to_variants("stable")

    print("\n" + "=" * 50)
    print("Icon generation complete!")
    print("=" * 50)


if __name__ == "__main__":
    main()
