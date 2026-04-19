from fpdf import FPDF
import math

from .pdf_generator import sanitize_pdf_text as sanitize


class MCQPDF(FPDF):
    def __init__(self, subject_name=""):
        super().__init__()
        self.subject_name = subject_name

    def header(self):
        self.set_line_width(0.5)
        self.rect(5.0, 5.0, 200.0, 287.0)

        self.set_font('Times', 'B', 16)
        self.cell(0, 10, '[ UNIVERSITY EXAMINATION ]', 0, 1, 'C')
        self.ln(2)

        if self.subject_name:
            self.set_font('Times', 'B', 14)
            self.cell(0, 8, self.subject_name, 0, 1, 'C')
            self.ln(2)

        self.set_font('Times', 'B', 12)
        self.cell(0, 8, 'Duration: 3 Hours', 0, 0, 'L')
        self.cell(0, 8, 'Marks: 80 Marks', 0, 1, 'R')

        y = self.get_y()
        self.set_line_width(0.3)
        self.line(10, y, 200, y)
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        y = self.get_y() - 1
        self.set_line_width(0.3)
        self.line(10, y, 200, y)
        self.set_font('Times', 'I', 10)
        self.cell(0, 10, f'Page {self.page_no()} of {{nb}}', 0, 0, 'C')


def generate_mcq_pdf(data, output_path):
    subject_name = sanitize(data.get('subject_name', ''))
    mcqs = data.get('mcqs', [])

    pdf = MCQPDF(subject_name=subject_name)
    pdf.alias_nb_pages()
    pdf.add_page()

    # Instructions box
    pdf.set_font('Times', 'B', 11)
    y_start = pdf.get_y()
    pdf.cell(0, 6, '  N.B.:', 0, 1, 'L')
    pdf.set_font('Times', '', 10)
    instructions = [
        "(1) All questions are compulsory.",
        "(2) Each question carries 2 marks.",
        "(3) Choose the most appropriate answer from the given options.",
        "(4) Total Marks: 80  |  Total Questions: 40",
    ]
    for inst in instructions:
        pdf.cell(10)
        pdf.cell(0, 6, inst, 0, 1, 'L')
    y_end = pdf.get_y()
    pdf.set_line_width(0.2)
    pdf.rect(10, y_start, 190, (y_end - y_start) + 2)
    pdf.ln(6)

    # MCQ Questions
    for mcq in mcqs:
        if pdf.get_y() > 255:
            pdf.add_page()

        pdf.set_font('Times', 'B', 11)
        q_text = sanitize(f"Q.{mcq['qst_num']}.  {mcq['text']}")

        # Marks on right
        pdf.set_x(175)
        pdf.cell(0, 6, '2', 0, 0, 'R')
        pdf.set_x(10)
        pdf.multi_cell(160, 6, q_text)

        # Options
        pdf.set_font('Times', '', 11)
        options = mcq.get('options', {})
        option_labels = ['A', 'B', 'C', 'D']
        for label in option_labels:
            opt_text = sanitize(options.get(label, ''))
            if opt_text:
                if pdf.get_y() > 268:
                    pdf.add_page()
                pdf.set_x(20)
                pdf.multi_cell(170, 5.5, f'{label}. {opt_text}')

        pdf.ln(4)

    # ===== ANSWER KEY Page =====
    pdf.add_page()
    pdf.set_font('Times', 'B', 14)
    pdf.cell(0, 10, 'ANSWER KEY', 0, 1, 'C')
    pdf.ln(4)

    # Draw grid: 4 columns to fit answers compactly
    cols = 4
    col_width = 40
    row_height = 7
    pdf.set_font('Times', 'B', 11)

    # Header row
    for c in range(cols):
        pdf.cell(col_width / 2, row_height, 'Q.No', 1, 0, 'C')
        pdf.cell(col_width / 2, row_height, 'Ans', 1, 0, 'C')
    pdf.ln()

    pdf.set_font('Times', '', 11)
    per_col = math.ceil(len(mcqs) / cols)

    # Build rows
    for row_idx in range(per_col):
        for col_idx in range(cols):
            mcq_idx = col_idx * per_col + row_idx
            if mcq_idx < len(mcqs):
                mcq = mcqs[mcq_idx]
                pdf.cell(col_width / 2, row_height, sanitize(f"Q.{mcq['qst_num']}"), 1, 0, 'C')
                pdf.cell(col_width / 2, row_height, sanitize(str(mcq.get('answer', '-'))), 1, 0, 'C')
            else:
                pdf.cell(col_width, row_height, '', 1, 0, 'C')
        pdf.ln()

    pdf.output(output_path)
    return output_path
