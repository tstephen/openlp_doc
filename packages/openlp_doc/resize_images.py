#!/usr/bin/env python3
"""
Script to resize PNG images to be under 500KB while maintaining quality
"""

import os
import sys
from pathlib import Path

from PIL import Image


def get_file_size_kb(filepath):
    """Get file size in KB"""
    return os.path.getsize(filepath) / 1024


def resize_image_to_target_size(
    image_path, target_size_kb=500, quality_start=95
):
    """
    Resize image to be under target size in KB
    """
    print(f"Processing: {image_path}")

    # Get original size
    original_size_kb = get_file_size_kb(image_path)
    print(f"Original size: {original_size_kb:.1f} KB")

    if original_size_kb <= target_size_kb:
        print(f"Image already under {target_size_kb}KB, skipping")
        return

    # Open image
    with Image.open(image_path) as img:
        # Convert to RGB if necessary (PNG with transparency)
        if img.mode in ("RGBA", "LA"):
            # Create white background
            background = Image.new("RGB", img.size, (255, 255, 255))
            if img.mode == "RGBA":
                background.paste(
                    img, mask=img.split()[-1]
                )  # Use alpha channel as mask
            else:
                background.paste(img, mask=img.split()[-1])
            img = background
        elif img.mode != "RGB":
            img = img.convert("RGB")

        # Start with original dimensions and reduce if needed
        width, height = img.size
        print(f"Original dimensions: {width}x{height}")

        # Try different resize factors
        for scale_factor in [0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3]:
            new_width = int(width * scale_factor)
            new_height = int(height * scale_factor)

            # Resize image
            resized_img = img.resize(
                (new_width, new_height), Image.Resampling.LANCZOS
            )

            # Try different quality settings
            for quality in range(quality_start, 30, -10):
                # Save to temporary path to check size
                temp_path = str(image_path) + ".temp"

                try:
                    if image_path.suffix.lower() == ".png":
                        # For PNG, use optimize and compress_level
                        resized_img.save(
                            temp_path, "PNG", optimize=True, compress_level=9
                        )
                    else:
                        # For JPEG
                        resized_img.save(
                            temp_path, "JPEG", quality=quality, optimize=True
                        )

                    temp_size_kb = get_file_size_kb(temp_path)
                    print(
                        f"  Trying {new_width}x{new_height}, quality={quality}: {temp_size_kb:.1f} KB"
                    )

                    if temp_size_kb <= target_size_kb:
                        # Replace original with resized version
                        os.replace(temp_path, image_path)
                        print(
                            f"✓ Successfully resized to {temp_size_kb:.1f} KB ({new_width}x{new_height})"
                        )
                        return
                    else:
                        # Clean up temp file
                        os.remove(temp_path)

                except Exception as e:
                    print(f"  Error with quality {quality}: {e}")
                    if os.path.exists(temp_path):
                        os.remove(temp_path)

        print(f"✗ Could not resize {image_path} to under {target_size_kb}KB")


def main():
    """Main function"""
    # Find all PNG files in tests/resources
    base_path = Path("tests/resources")
    png_files = list(base_path.glob("**/*.png"))

    if not png_files:
        print("No PNG files found in tests/resources")
        return

    print(f"Found {len(png_files)} PNG files to process")

    for png_file in png_files:
        try:
            resize_image_to_target_size(png_file)
            print()
        except Exception as e:
            print(f"Error processing {png_file}: {e}")
            print()


if __name__ == "__main__":
    main()
