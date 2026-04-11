import pdfplumber

def extract_pdf_text(pdf_object:pdfplumber.pdf.PDF) -> list[str]:
    page_texts = []

    print(pdf_object.metadata)

    for page in pdf_object.pages:
        page_texts.append(page.extract_text())

    return page_texts