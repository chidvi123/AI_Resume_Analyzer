import io
from pdfminer.high_level import extract_text

def extract_text_from_pdf(file_path:str)->str:
    """
    Extracting the entire text from the pdf using miner
    and returning the text as a string
    """

    try:
        text=extract_text(file_path)
        return text
    except Exception as e:
        return f"Error extracting text :{e}"