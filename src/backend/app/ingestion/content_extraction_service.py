import io
from pathlib import Path
import fitz
import pandas as pd
import pytesseract
from PIL import Image
from docx import Document
from tqdm import tqdm

pytesseract.pytesseract.tesseract_cmd = "/opt/homebrew/Cellar/tesseract/5.5.2/bin/tesseract"

class ContentExtractor:
    def __init__(
        self,
        min_direct_text_length: int = 30,
        tesseract_cmd: str | None = None,
        ocr_languages: str = "nld+eng"
    ):
        self.min_direct_text_length = min_direct_text_length
        self.ocr_languages = ocr_languages

        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    def process_inventory(self, inventory_df: pd.DataFrame) -> pd.DataFrame:
        rows = []

        for _, file_row in tqdm(
            inventory_df.iterrows(),
            total=len(inventory_df),
            desc="Processing files"
        ):
            file_type = file_row["file_type"]

            if file_type == "pdf":
                rows.extend(self._process_pdf(file_row))
            elif file_type == "image":
                rows.append(self._process_image(file_row))
            elif file_type == "docx":
                rows.append(self._process_docx(file_row))
            elif file_type == "doc":
                rows.append(self._unsupported_file(file_row, "Legacy .doc files are not supported."))

        return pd.DataFrame(rows)

    def _base_result(self, file_row, page_number, extraction_method, raw_text, status, error_message=""):
        return {
            "file_id": file_row["file_id"],
            "file_name": file_row["file_name"],
            "file_type": file_row["file_type"],
            "page_number": page_number,
            "extraction_method": extraction_method,
            "raw_text": raw_text or "",
            "text_length": len(raw_text or ""),
            "status": status,
            "error_message": error_message,
            "source_path": file_row["full_path"],
        }

    def _process_pdf(self, file_row) -> list[dict]:
        results = []
        file_path = file_row["full_path"]

        try:
            doc = fitz.open(file_path)
        except Exception as e:
            return [
                self._base_result(
                    file_row, None, None, "", "failed", str(e)
                )
            ]

        try:
            for page_index in tqdm(
                range(len(doc)),
                desc=f"Pages: {file_row['file_name']}",
                leave=False
            ):
                page = doc.load_page(page_index)
                direct_text = page.get_text("text").strip()

                if len(direct_text) >= self.min_direct_text_length:
                    text = direct_text
                    method = "direct_pdf_text"
                else:
                    text = self._ocr_pdf_page(page)
                    method = "ocr_pdf_page"

                results.append(
                    self._base_result(
                        file_row,
                        page_index + 1,
                        method,
                        text,
                        "success"
                    )
                )
        finally:
            doc.close()

        return results

    def _ocr_pdf_page(self, page) -> str:
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
        img_bytes = pix.tobytes("png")
        image = Image.open(io.BytesIO(img_bytes))

        text = pytesseract.image_to_string(
            image,
            lang=self.ocr_languages
        )

        return text.strip()

    def _process_image(self, file_row) -> dict:
        file_path = file_row["full_path"]

        try:
            image = Image.open(file_path)
            text = pytesseract.image_to_string(
                image,
                lang=self.ocr_languages
            ).strip()

            return self._base_result(
                file_row, 1, "ocr_image", text, "success"
            )

        except Exception as e:
            return self._base_result(
                file_row, 1, None, "", "failed", str(e)
            )

    def _process_docx(self, file_row) -> dict:
        file_path = file_row["full_path"]

        try:
            document = Document(file_path)

            paragraphs = [
                paragraph.text.strip()
                for paragraph in document.paragraphs
                if paragraph.text.strip()
            ]

            text = "\n".join(paragraphs)

            return self._base_result(
                file_row, 1, "docx_text", text, "success"
            )

        except Exception as e:
            return self._base_result(
                file_row, 1, None, "", "failed", str(e)
            )

    def _unsupported_file(self, file_row, message: str) -> dict:
        return self._base_result(
            file_row, None, None, "", "skipped", message
        )