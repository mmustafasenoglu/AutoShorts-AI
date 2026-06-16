from PIL import Image, ImageDraw, ImageFont
import os

def create_overlay(text, filename="overlay.png", width=600, height=80):
    # Create a black image
    img = Image.new('RGBA', (width, height), color='black')
    d = ImageDraw.Draw(img)
    
    # Try to load a font, otherwise use default
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 48)
    except IOError:
        try:
            font = ImageFont.truetype("/Library/Fonts/Arial.ttf", 48)
        except IOError:
            font = ImageFont.load_default()

    # Get text size
    # In newer Pillow versions, textbbox is used
    if hasattr(d, 'textbbox'):
        bbox = d.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
    else:
        text_w, text_h = d.textsize(text, font=font)

    # Calculate position
    x = (width - text_w) / 2
    y = (height - text_h) / 2 - 10 # slightly adjust upwards

    # Draw text
    d.text((x, y), text, fill="white", font=font)
    
    img.save(filename)
    print(f"Overlay saved to {filename}")

if __name__ == "__main__":
    create_overlay("mustafa senoglu")
