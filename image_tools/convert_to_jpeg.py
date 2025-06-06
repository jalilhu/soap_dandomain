from PIL import Image
import os

def convert_to_jpeg(image_path):
    img = Image.open(image_path)

    # Fix: handle transparency correctly
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGBA")
        # Add white background for JPEG (since it doesn't support transparency)
        background = Image.new("RGB", img.size, (255, 255, 255))
        background.paste(img, mask=img.split()[3])  # 3 is the alpha channel
        img = background
    else:
        img = img.convert("RGB")

    # Save as JPEG
    jpeg_path = os.path.splitext(image_path)[0] + ".jepg"
    img.save(jpeg_path, "JPEG", quality=85)

    return jpeg_path

def convert_to_webp(input_path, output_path):
    with Image.open(input_path) as img:
        img.save(output_path, 'WEBP')
    