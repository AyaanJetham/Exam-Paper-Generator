# this file is responsible for preprocessing the user syllabus
# from extract_from_pdf import extract_module_content
import spacy
nlp = spacy.load("en_core_web_sm")
pdf_path = "artifacts/syllabus.pdf"
def preprocess_text(text):
    # Convert to lowercase
    text = text.lower()
    doc = nlp(text)
    tokens = [token.lemma_ for token in doc if not token.is_stop and token.is_alpha]
    # Remove duplicates while maintaining order
    unique_tokens = list(dict.fromkeys(tokens)) 

    return " ".join(unique_tokens)

# module_content = extract_module_content(pdf_path)
# content = preprocess_text(module_content)
# print(content)