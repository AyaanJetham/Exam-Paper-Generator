import fitz  # PyMuPDF
import os

def extract_module_content(pdf_path):
    if not os.path.exists(pdf_path):
        print(f"File not found: {pdf_path}")
        return ""

    try:
        doc = fitz.open(pdf_path)
        extracted_text = ""
        is_module_section = False

        for page_number, page in enumerate(doc, start=1):
            text = page.get_text()
            # print(f"Processing Page {page_number}:")  # Debugging
            # print(text)  # Print full page text for debugging

            for line in text.splitlines():
                # print(f"Line: {line}")  # Debugging
                if "Module" in line or "module" in line:
                    # print(f"Found 'Module': {line}")
                    is_module_section = True
                if "Textbooks" in line:
                    # print(f"Found 'Textbooks': {line}")
                    is_module_section = False
                    break

                if is_module_section:
                    extracted_text += line + "\n"

        # print(f"Extracted Text:\n{extracted_text}")  # Debugging
        return extracted_text.strip()

    except Exception as e:
        print(f"Error processing PDF: {e}")
        return ""

# pdf_path = "backend/artifacts/syllabus.pdf"
# module_content = extract_module_content(pdf_path)
# print("Extracted Module Content:")
# print(module_content) #extracted required data from the user pdf
