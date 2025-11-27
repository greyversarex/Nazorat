from PIL import Image, ImageDraw

def create_icon(size):
    img = Image.new('RGBA', (size, size), (13, 110, 253, 255))
    draw = ImageDraw.Draw(img)
    
    margin = size // 6
    envelope_top = size // 3
    envelope_bottom = size - margin
    envelope_left = margin
    envelope_right = size - margin
    
    draw.polygon([
        (envelope_left, envelope_top),
        (envelope_right, envelope_top),
        (envelope_right, envelope_bottom),
        (envelope_left, envelope_bottom)
    ], fill=(255, 255, 255, 255))
    
    center_x = size // 2
    flap_bottom = envelope_top + (envelope_bottom - envelope_top) // 2
    
    draw.polygon([
        (envelope_left, envelope_top),
        (center_x, flap_bottom),
        (envelope_right, envelope_top)
    ], fill=(230, 240, 255, 255), outline=(200, 220, 255, 255))
    
    return img

sizes = [72, 96, 128, 144, 152, 192, 384, 512]

for size in sizes:
    icon = create_icon(size)
    icon.save(f'static/icons/icon-{size}.png')
    print(f'Created icon-{size}.png')

print('All icons created successfully!')
