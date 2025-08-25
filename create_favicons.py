#!/usr/bin/env python3
from PIL import Image, ImageDraw, ImageFont
import os

def create_favicon(size, filename):
    # Create image with StableYield brand color
    img = Image.new('RGB', (size, size), '#2E6049')
    draw = ImageDraw.Draw(img)
    
    # Add "SY" text for StableYield
    try:
        font_size = int(size * 0.5)
        # Try to use a system font
        try:
            font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', font_size)
        except:
            font = ImageFont.load_default()
    except:
        font = ImageFont.load_default()
    
    # Calculate text position to center it
    text = "SY"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (size - text_width) // 2
    y = (size - text_height) // 2
    
    # Draw white text
    draw.text((x, y), text, fill='white', font=font)
    
    # Save the image
    img.save(filename, 'PNG')
    print(f"Created {filename}")

# Create favicon directory if it doesn't exist
os.makedirs('/app/frontend/public/favicons', exist_ok=True)

# Create different sized favicons
create_favicon(16, '/app/frontend/public/favicons/favicon-16.png')
create_favicon(32, '/app/frontend/public/favicons/favicon-32.png')
create_favicon(180, '/app/frontend/public/favicons/apple-touch-icon.png')

print("All favicons created successfully!")