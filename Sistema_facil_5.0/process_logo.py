from PIL import Image, ImageDraw

def make_background_transparent(image_path, output_path):
    img = Image.open(image_path).convert("RGBA")
    width, height = img.size
    
    # Create a circular mask
    mask = Image.new("L", (width, height), 0)
    draw = ImageDraw.Draw(mask)
    # Draw a filled circle with a tiny margin to avoid aliasing issues at the edge
    draw.ellipse((2, 2, width - 2, height - 2), fill=255)
    
    # Create transparent base and paste the image through the mask
    result = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    result.paste(img, (0, 0), mask=mask)
    result.save(output_path, "PNG")

if __name__ == "__main__":
    make_background_transparent("logo_sf_raw.png", "logo_sf.png")
    print("Logo processed successfully!")
