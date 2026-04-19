from fpdf import FPDF
import os

def sanitize_pdf_text(text):
    if not text:
        return ""
    # Standard replacement for common win-1252/unicode characters that FPDF Times/Arial handles poorly
    return str(text).replace('\u2013', '-').replace('\u2014', '-') \
                   .replace('\u2018', "'").replace('\u2019', "'") \
                   .replace('\u201c', '"').replace('\u201d', '"') \
                   .replace('\u2026', '...')

class PaperPDF(FPDF):
    def __init__(self, subject_name="", difficulty="medium"):
        super().__init__()
        self.subject_name = subject_name
        self.difficulty = difficulty

    def header(self):
        # Border
        self.set_line_width(0.5)
        self.rect(5.0, 5.0, 200.0, 287.0)

        # Header Title
        self.set_font('Times', 'B', 16)
        self.cell(0, 10, '[ UNIVERSITY EXAMINATION ]', 0, 1, 'C')
        
        if self.subject_name:
            self.set_font('Times', 'B', 14)
            self.cell(0, 8, sanitize_pdf_text(self.subject_name).upper(), 0, 1, 'C')
        
        self.ln(2)
        
        # Duration and Marks
        self.set_font('Times', 'B', 12)
        self.cell(0, 8, 'Duration: 3 Hours', 0, 0, 'L')
        self.set_x(150)
        self.cell(0, 8, 'Total Marks: 80 Marks', 0, 1, 'R')
        
        # Horizontal line
        y = self.get_y()
        self.line(10, y, 200, y)
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Times', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()} of {{nb}}', 0, 0, 'C')

def generate_question_paper_pdf(data, output_path, difficulty='medium', include_answers=False):
    subject_name = data.get('subject_name', 'Subject Name')
    paper_data = data.get('paper', [])

    pdf = PaperPDF(subject_name=subject_name, difficulty=difficulty)
    pdf.alias_nb_pages()
    pdf.add_page()

    # Instructions box
    pdf.set_font('Times', 'B', 11)
    y_start = pdf.get_y()
    pdf.cell(0, 6, '  N.B.:', 0, 1, 'L')
    pdf.set_font('Times', '', 10)
    
    instructions = [
        "(1) Question No 1 is Compulsory.",
        "(2) Attempt any three questions out of the remaining five.",
        "(3) All questions carry equal marks.",
        "(4) Assume suitable data, if required and state it clearly."
    ]
    for inst in instructions:
        pdf.set_x(15)
        pdf.cell(0, 5, inst, 0, 1, 'L')
    
    y_end = pdf.get_y()
    pdf.rect(10, y_start, 190, (y_end - y_start) + 2)
    pdf.ln(8)

    # Questions logic
    for q in paper_data:
        qnum = q.get('qst_num')
        instruction = sanitize_pdf_text(q.get('instruction', ''))
        
        # Check for page break
        if pdf.get_y() > 250:
            pdf.add_page()

        # Question header
        pdf.set_font('Times', 'B', 12)
        
        # Marks display logic
        marks_display = "20"
        if difficulty == 'balanced':
            if qnum == 1: marks_display = "20 (2x10)"
            elif qnum == 2: marks_display = "20 (4x5)"
            elif qnum == 6: marks_display = "20 (2x10)"
        else:
            if qnum == 1: marks_display = "20 (4x5)"
            elif qnum == 6: marks_display = "20 (2x10)"

        # Write Q.Num and Marks
        current_y = pdf.get_y()
        pdf.set_x(175)
        pdf.cell(20, 7, marks_display, 0, 0, 'R')
        pdf.set_x(10)
        pdf.cell(15, 7, f'Q.{qnum}', 0, 0, 'L')
        
        if instruction:
            pdf.set_font('Times', '', 12)
            pdf.multi_cell(150, 7, instruction)
        else:
            pdf.ln(7)

        # Parts
        for part in q.get('parts', []):
            part_label = part.get('part_label', '')
            part_text = sanitize_pdf_text(part.get('text', ''))
            part_marks = part.get('marks', '')

            if pdf.get_y() > 265:
                pdf.add_page()

            if part_text:
                pdf.set_x(20)
                pdf.set_font('Times', '', 11)
                
                # Marks on right
                if part_marks:
                    save_y = pdf.get_y()
                    pdf.set_x(175)
                    pdf.cell(20, 6, str(part_marks), 0, 0, 'R')
                    pdf.set_y(save_y)
                
                pdf.set_x(20)
                pdf.multi_cell(150, 6, f'{part_label}. {part_text}')
                pdf.ln(1)

            # Subparts
            for idx, subpart in enumerate(part.get('subparts', [])):
                sub_label = subpart.get('sub_label', '')
                sub_text = sanitize_pdf_text(subpart.get('text', ''))
                sub_marks = subpart.get('marks', '')

                if pdf.get_y() > 265:
                    pdf.add_page()

                pdf.set_x(30)
                pdf.set_font('Times', '', 10.5)
                
                if sub_marks:
                    save_y = pdf.get_y()
                    pdf.set_x(175)
                    pdf.cell(20, 5.5, str(sub_marks), 0, 0, 'R')
                    pdf.set_y(save_y)

                prefix = f'{part_label}. ' if not part_text and idx == 0 else ''
                pdf.set_x(30)
                pdf.multi_cell(140, 5.5, f'{prefix}{sub_label}. {sub_text}')
        
        pdf.ln(4)

    # Answer Key Section
    if include_answers:
        pdf.add_page()
        pdf.set_font('Times', 'B', 14)
        pdf.cell(0, 10, 'MODEL ANSWER KEY / SOLUTION GUIDE', 0, 1, 'C')
        pdf.set_font('Times', 'I', 10)
        pdf.cell(0, 5, '(Includes Marking Scheme and Technical Key Points)', 0, 1, 'C')
        pdf.ln(5)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(5)

        for q in paper_data:
            pdf.set_font('Times', 'B', 12)
            pdf.cell(0, 8, f"Question {q.get('qst_num')}:", 0, 1, 'L')
            
            for part in q.get('parts', []):
                part_label = part.get('part_label', '')
                ans = sanitize_pdf_text(part.get('answer_guide', '').strip())
                
                subparts = part.get('subparts', [])
                if subparts:
                    for sub in subparts:
                        sub_label = sub.get('sub_label', '')
                        sub_ans = sanitize_pdf_text(sub.get('answer_guide', '').strip())
                        if sub_ans:
                            pdf.set_x(20)
                            pdf.set_font('Times', 'B', 11)
                            pdf.cell(15, 6, f"({part_label}.{sub_label})", 0, 0, 'L')
                            pdf.set_font('Times', '', 11)
                            pdf.multi_cell(165, 6, sub_ans)
                elif ans:
                    pdf.set_x(20)
                    pdf.set_font('Times', 'B', 11)
                    pdf.cell(15, 6, f"({part_label})", 0, 0, 'L')
                    pdf.set_font('Times', '', 11)
                    pdf.multi_cell(165, 6, ans)
            pdf.ln(5)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    pdf.output(output_path)
    return output_path
