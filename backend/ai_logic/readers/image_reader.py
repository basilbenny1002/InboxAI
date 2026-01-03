from PIL import Image
import pytesseract

def extract_text_from_image(image_path):
    """
    Extract text from image using OCR
    """
    try:
        image = Image.open(image_path)
        
        # Convert to RGB if needed (some images are RGBA, CMYK, etc.)
        if image.mode != 'RGB':
            image = image.convert('RGB')

        # Improve OCR accuracy
        custom_config = r"--oem 3 --psm 6"

        text = pytesseract.image_to_string(
            image,
            lang="eng",
            config=custom_config
        )
        
        extracted_text = text.strip()
        
        if not extracted_text:
            return "[No text detected in image]"
        
        return extracted_text

    except pytesseract.TesseractNotFoundError:
        return "[ERROR: Tesseract OCR not installed. Please install it to read images.]"
    except Exception as e:
        return f"[ERROR reading image: {str(e)}]"