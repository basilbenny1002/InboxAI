import warnings
import logging
import pdfplumber

warnings.filterwarnings("ignore")
logging.getLogger("pdfminer").setLevel(logging.ERROR)

def extract_text_from_pdf(path, max_pages=5):
    """
    Extract text from PDF, limiting to first few pages for efficiency
    """
    text = ""
    try:
        with pdfplumber.open(path) as pdf:
            # Limit pages to avoid huge PDFs
            pages_to_read = min(len(pdf.pages), max_pages)
            
            for page_num in range(pages_to_read):
                page_text = pdf.pages[page_num].extract_text()
                if page_text:
                    text += page_text + "\n"
            
            # Indicate if there are more pages
            if len(pdf.pages) > max_pages:
                text += f"\n[Note: PDF has {len(pdf.pages)} total pages, only first {max_pages} extracted]"
                
    except Exception as e:
        return f"[ERROR reading PDF: {str(e)}]"

    return " ".join(text.split())