import cv2
import numpy as np
from PIL import Image, ImageEnhance

def hex_to_rgb(hex_str: str) -> tuple:
    """Helper to convert hex string (#RRGGBB or RRGGBB) to RGB tuple."""
    hex_str = hex_str.lstrip('#')
    if len(hex_str) != 6:
        raise ValueError("Invalid hex color format. Expected length 6.")
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))

# --- Aspect Ratio Crops ---

def crop_to_ratio(image: Image.Image, ratio: float) -> Image.Image:
    """Crop the PIL Image to the target aspect ratio centered on the image."""
    w, h = image.size
    img_ratio = w / h
    if img_ratio > ratio:
        # Image is too wide, crop left/right borders
        new_w = int(h * ratio)
        left = (w - new_w) // 2
        top = 0
        right = left + new_w
        bottom = h
    else:
        # Image is too tall, crop top/bottom borders
        new_h = int(w / ratio)
        left = 0
        top = (h - new_h) // 2
        right = w
        bottom = top + new_h
    return image.crop((left, top, right, bottom))

def crop_1_1(image: Image.Image) -> Image.Image:
    return crop_to_ratio(image, 1.0)

def crop_4_3(image: Image.Image) -> Image.Image:
    return crop_to_ratio(image, 4.0 / 3.0)

def crop_16_9(image: Image.Image) -> Image.Image:
    return crop_to_ratio(image, 16.0 / 9.0)

# --- Color Transformations ---

def transform_warm_tone(image: Image.Image) -> Image.Image:
    """Enhance red and yellow tones to create a warm feeling."""
    arr = np.array(image, dtype=np.float32)
    # arr is HxWx3 (RGB)
    arr[:, :, 0] = arr[:, :, 0] * 1.15  # Red
    arr[:, :, 1] = arr[:, :, 1] * 1.05  # Green
    arr[:, :, 2] = arr[:, :, 2] * 0.85  # Blue
    arr = np.clip(arr, 0, 255).astype(np.uint8)
    return Image.fromarray(arr)

def transform_cool_tone(image: Image.Image) -> Image.Image:
    """Enhance blue and cyan tones to create a cool/clinical feeling."""
    arr = np.array(image, dtype=np.float32)
    arr[:, :, 0] = arr[:, :, 0] * 0.85  # Red
    arr[:, :, 1] = arr[:, :, 1] * 1.05  # Green
    arr[:, :, 2] = arr[:, :, 2] * 1.20  # Blue
    arr = np.clip(arr, 0, 255).astype(np.uint8)
    return Image.fromarray(arr)

def transform_dark_mode(image: Image.Image) -> Image.Image:
    """Lower brightness and blend with a deep slate/blue tone."""
    arr = np.array(image, dtype=np.float32)
    # Lower intensity
    arr = arr * 0.5
    # Blend with slate blue: RGB (15, 20, 35)
    tint = np.array([15, 20, 35], dtype=np.float32)
    arr = arr + tint * 0.5
    arr = np.clip(arr, 0, 255).astype(np.uint8)
    return Image.fromarray(arr)

def transform_brand_palette(image: Image.Image, brand_color_hex: str) -> Image.Image:
    """Overlay a custom brand color onto the image."""
    try:
        color = hex_to_rgb(brand_color_hex)
    except Exception:
        color = (79, 70, 229)  # Default Indigo
    arr = np.array(image, dtype=np.float32)
    overlay = np.zeros_like(arr)
    overlay[:, :, 0] = color[0]
    overlay[:, :, 1] = color[1]
    overlay[:, :, 2] = color[2]
    # Blend 15% color overlay, 85% original image
    blended = arr * 0.85 + overlay * 0.15
    blended = np.clip(blended, 0, 255).astype(np.uint8)
    return Image.fromarray(blended)

# --- Background Replacement Module (GrabCut + Composite) ---

def extract_foreground_mask(image: Image.Image) -> np.ndarray:
    """
    Generate a soft foreground mask [0.0, 1.0] of shape (H, W) using
    adaptive thresholding for uniform backgrounds and OpenCV GrabCut for complex backgrounds.
    """
    # Convert PIL to OpenCV BGR
    cv_img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    h, w = cv_img.shape[:2]
    
    # 1. Check if background is highly uniform (e.g. white/studio background)
    # We sample the border pixels to calculate the mean and standard deviation
    border_w = max(5, int(w * 0.02))
    border_h = max(5, int(h * 0.02))
    
    borders = np.concatenate([
        cv_img[0:border_h, :].reshape(-1, 3),
        cv_img[h-border_h:h, :].reshape(-1, 3),
        cv_img[:, 0:border_w].reshape(-1, 3),
        cv_img[:, w-border_w:w].reshape(-1, 3)
    ])
    mean_color = np.mean(borders, axis=0)
    std_color = np.std(borders, axis=0)
    
    # If border pixels are very bright and uniform, perform direct color keying
    is_uniform_light_bg = mean_color[0] > 220 and mean_color[1] > 220 and mean_color[2] > 220 and np.max(std_color) < 25
    
    if is_uniform_light_bg:
        # Distance map from background color
        diff = np.abs(cv_img.astype(np.float32) - mean_color)
        dist = np.max(diff, axis=2)
        # Background thresholding: values > 25 are considered foreground
        mask = np.where(dist > 25, 1.0, 0.0).astype(np.float32)
        # Smooth mask borders
        mask = cv2.GaussianBlur(mask, (5, 5), 0)
        return mask

    # 2. Run GrabCut for complex backgrounds
    mask = np.zeros((h, w), dtype=np.uint8)
    bgd_model = np.zeros((1, 65), dtype=np.float64)
    fgd_model = np.zeros((1, 65), dtype=np.float64)
    
    # Set a center bounding box (5% margin)
    rect_x = int(w * 0.05)
    rect_y = int(h * 0.05)
    rect = (rect_x, rect_y, w - 2 * rect_x, h - 2 * rect_y)
    
    try:
        # Perform 3 iterations of GrabCut
        cv2.grabCut(cv_img, mask, rect, bgd_model, fgd_model, 3, cv2.GC_INIT_WITH_RECT)
        # Binarize: GC_BGD=0, GC_PR_BGD=2 => 0 (background); GC_FGD=1, GC_PR_FGD=3 => 1 (foreground)
        fg_mask = np.where((mask == 2) | (mask == 0), 0.0, 1.0).astype(np.float32)
        # Apply smoothing to feather edges
        fg_mask = cv2.GaussianBlur(fg_mask, (5, 5), 0)
        return fg_mask
    except Exception as e:
        print(f"GrabCut failed, falling back to radial vignette: {e}")
        # Vignette fallback mask (center radial gradient)
        fallback = np.zeros((h, w), dtype=np.float32)
        cv2.ellipse(fallback, (w // 2, h // 2), (int(w * 0.45), int(h * 0.45)), 0, 0, 360, 1.0, -1)
        return cv2.GaussianBlur(fallback, (21, 21), 0)

def composite_foreground(image: Image.Image, bg_image: Image.Image) -> Image.Image:
    """Extract foreground and composite it over the provided background image."""
    mask = extract_foreground_mask(image)
    # Convert mask to 0-255 uint8 PIL Image (mode L)
    mask_pil = Image.fromarray((mask * 255).astype(np.uint8), mode="L")
    
    # Resize background to match source image
    bg_resized = bg_image.resize(image.size, Image.Resampling.LANCZOS)
    return Image.composite(image, bg_resized, mask_pil)

def bg_replace_white(image: Image.Image) -> Image.Image:
    bg = Image.new("RGB", image.size, (255, 255, 255))
    return composite_foreground(image, bg)

def bg_replace_black(image: Image.Image) -> Image.Image:
    bg = Image.new("RGB", image.size, (0, 0, 0))
    return composite_foreground(image, bg)

def bg_replace_custom(image: Image.Image, bg_color_hex: str) -> Image.Image:
    try:
        color = hex_to_rgb(bg_color_hex)
    except Exception:
        color = (240, 240, 240)
    bg = Image.new("RGB", image.size, color)
    return composite_foreground(image, bg)

def bg_replace_gradient(image: Image.Image, color1_hex: str = "#646ef0", color2_hex: str = "#b464f4") -> Image.Image:
    """Replace background with a diagonal linear gradient."""
    try:
        c1 = hex_to_rgb(color1_hex)
        c2 = hex_to_rgb(color2_hex)
    except Exception:
        c1 = (100, 110, 240)  # Indigo
        c2 = (180, 100, 244)  # Violet
        
    w, h = image.size
    X, Y = np.meshgrid(np.arange(w), np.arange(h))
    dist = (X + Y) / (w + h)
    
    r = (1.0 - dist) * c1[0] + dist * c2[0]
    g = (1.0 - dist) * c1[1] + dist * c2[1]
    b = (1.0 - dist) * c1[2] + dist * c2[2]
    
    gradient = np.stack([r, g, b], axis=-1).astype(np.uint8)
    bg = Image.fromarray(gradient)
    return composite_foreground(image, bg)

# --- Style Adjustments ---

def adjust_brightness(image: Image.Image, factor: float) -> Image.Image:
    return ImageEnhance.Brightness(image).enhance(factor)

def adjust_contrast(image: Image.Image, factor: float) -> Image.Image:
    return ImageEnhance.Contrast(image).enhance(factor)

def adjust_saturation(image: Image.Image, factor: float) -> Image.Image:
    return ImageEnhance.Color(image).enhance(factor)
