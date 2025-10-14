from PIL import Image, ImageDraw, ImageFont
import os

def create_modern_rm_logo():
    """
    Create a modern, minimal 'RM' logo for RevMark using green and white.
    The design uses bold, geometric letters with a unique accent underline.
    """

    size = 256
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Gradient green background (top to bottom)
    from PIL import ImageColor
    grad_top = ImageColor.getrgb('#43e97b')  # Lighter green
    grad_bottom = ImageColor.getrgb('#38f9d7')  # Even lighter/teal green
    for y in range(size):
        ratio = y / size
        r = int(grad_top[0] * (1 - ratio) + grad_bottom[0] * ratio)
        g = int(grad_top[1] * (1 - ratio) + grad_bottom[1] * ratio)
        b = int(grad_top[2] * (1 - ratio) + grad_bottom[2] * ratio)
        draw.line([(0, y), (size, y)], fill=(r, g, b, 255))

    # Draw a rounded square (app icon style)
    from PIL import ImageFilter
    mask = Image.new('L', (size, size), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle([8, 8, size-8, size-8], radius=48, fill=255)
    img = Image.composite(img, Image.new('RGBA', (size, size), (0, 0, 0, 0)), mask)
    draw = ImageDraw.Draw(img)

    # Load a bold sans-serif font (fallback to default if not found)
    font_path = os.path.join(os.path.dirname(__file__), 'arialbd.ttf')
    try:
        font = ImageFont.truetype(font_path, 140)
    except Exception:
        font = ImageFont.load_default()

    # Draw 'R' and 'M' with extra spacing
    white = '#ffffff'
    r_text = "R"
    m_text = "M"
    # Get sizes
    r_bbox = font.getbbox(r_text)
    m_bbox = font.getbbox(m_text)
    r_width = r_bbox[2] - r_bbox[0]
    m_width = m_bbox[2] - m_bbox[0]
    text_height = max(r_bbox[3] - r_bbox[1], m_bbox[3] - m_bbox[1])
    spacing = 2  # Very tight spacing for a modern, unified look
    total_width = r_width + m_width + spacing
    text_x = (size - total_width) // 2
    text_y = (size - text_height) // 2 - 10  # Move text upward for better centering
    # Draw R
    draw.text((text_x, text_y), r_text, font=font, fill=white)
    # Draw M
    draw.text((text_x + r_width + spacing, text_y), m_text, font=font, fill=white)

    # Add a subtle checkmark accent above the "M"
    check_x = text_x + r_width + spacing + m_width // 2
    check_y = text_y - 28  # Keep checkmark position relative to text
    check_size = 28
    check_color = (255, 255, 255, 180)
    draw.line([
        (check_x - check_size//3, check_y + check_size//3),
        (check_x, check_y + check_size),
        (check_x + check_size//2, check_y)
    ], fill=check_color, width=5, joint="curve")

    # Save logo
    out_path = os.path.join(os.path.dirname(__file__), 'logo_modern_rm.png')
    img.save(out_path)
    print(f"Logo saved to {out_path}")

if __name__ == "__main__":
    create_modern_rm_logo()
