import io
from pathlib import Path
import fitz
import pandas as pd
import pytesseract
from PIL import Image
# from docx import Document
from tqdm import tqdm
import requests

pytesseract.pytesseract.tesseract_cmd = "C:/Program Files/Tesseract-OCR/tesseract.exe"

class ContentExtractor:
    def __init__(
        self,
        min_direct_text_length: int = 30,
        tesseract_cmd: str | None = None,
        ocr_languages: str = "nld+eng"
    ):
        self.min_direct_text_length = min_direct_text_length
        self.ocr_languages = ocr_languages

        # if tesseract_cmd:
            # pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

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

        text = self._get_text_from_image(image)

        print(text)

        # text = pytesseract.image_to_string(
        #     image,
        #     lang=self.ocr_languages
        # )

        return text.strip()

    def _process_image(self, file_row) -> dict:
        file_path = file_row["full_path"]

        try:
            image = Image.open(file_path)
            # text = pytesseract.image_to_string(
            #     image,
            #     lang=self.ocr_languages
            # ).strip()

            text = self._get_text_from_image(image)

            print(text)

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
            pass
            # document = Document(file_path)

            # paragraphs = [
            #     paragraph.text.strip()
            #     for paragraph in document.paragraphs
            #     if paragraph.text.strip()
            # ]

            # text = "\n".join(paragraphs)

            # return self._base_result(
            #     file_row, 1, "docx_text", text, "success"
            # )

        except Exception as e:
            return self._base_result(
                file_row, 1, None, "", "failed", str(e)
            )

    def _unsupported_file(self, file_row, message: str) -> dict:
        return self._base_result(
            file_row, None, None, "", "skipped", message
        )

    def _correct_orientation(self, full_image: Image.Image) -> Image.Image:
        width, height = full_image.size
        
        # 2. Extract a crisp 1024x1024 sample from the TOP-RIGHT corner
        # This keeps Tesseract processing fast and prevents out-of-memory crashes
        crop_size = min(1024, width, height)
        left = width - crop_size
        top = 0
        right = width
        bottom = crop_size
        
        orientation_sample = full_image.crop((left, top, right, bottom))

        print("[INFO] Analyzing top-right text layout via PyTesseract OSD...")
        try:
            # 3. Run Orientation and Script Detection (OSD) on the crop
            # --psm 0 tells Tesseract to ONLY look for orientation/script details, not read words
            osd_data = pytesseract.image_to_osd(orientation_sample, config='--psm 0')
            
            # Parse Tesseract's raw string output into a clean dictionary
            results = {}
            for line in osd_data.strip().split("\n"):
                if ":" in line:
                    key, val = line.split(":", 1)
                    results[key.strip()] = val.strip()
                    
            detected_orientation = int(results.get("Orientation in degrees", 0))
            rotate_angle = int(results.get("Rotate", 0))
            script = results.get("Script", "Unknown")
            
            print(f"[INFO] Detected baseline orientation: {detected_orientation}°")
            print(f"[INFO] Rotate by {rotate_angle} degrees to correct.")
            print(f"[INFO] Detected script: {script}")

        except Exception as e:
            print(f"[WARN] Tesseract failed to determine orientation: {e}. Defaulting to 0°.")
            rotate_angle = 0

        # 4. Rotate the image to correct the orientation (replaces imutils.rotate_bound)
        # expand=True changes canvas boundaries so text doesn't clip on 90/270 degree turns
        if rotate_angle != 0:
            # Tesseract returns degrees clockwise needed to fix, 
            # PIL rotates counter-clockwise, so we subtract from 360 to flip it right
            pil_rotation_angle = (360 - rotate_angle) % 360
            rotated_image = full_image.rotate(pil_rotation_angle, expand=True)
        else:
            rotated_image = full_image

        return rotated_image
    
    def _slice_to_chunks(self, pil_img, chunk_size=512, overlap=32) -> list[list[Image.Image]]:
        """
        Slices a large image into a grid of square chunks, dynamically shifting
        edge chunks backward to eliminate whitespace padding.
        """
        width, height = pil_img.size
        chunks = []
        
        step = chunk_size - overlap
        
        y_coords = list(range(0, height, step))
        x_coords = list(range(0, width, step))
        
        for y in y_coords:
            line_chunks = []
            
            y_start = y
            y_end = y_start + chunk_size
            
            if y_end > height:
                y_end = height
                y_start = max(0, height - chunk_size)
                
            for x in x_coords:
                x_start = x
                x_end = x_start + chunk_size
                
                if x_end > width:
                    x_end = width
                    x_start = max(0, width - chunk_size)
                
                box = (x_start, y_start, x_end, y_end)
                chunk = pil_img.crop(box)
                
                # Fallback: If the entire image is smaller than the chunk size,
                # only then pad it out to a square.
                if chunk.size != (chunk_size, chunk_size):
                    new_chunk = Image.new("RGB", (chunk_size, chunk_size), (255, 255, 255))
                    new_chunk.paste(chunk, (0, 0))
                    chunk = new_chunk
                    
                line_chunks.append(chunk)
            chunks.append(line_chunks)
                
        return chunks
    
    def _merge_overlapping_text(self, text1: str, text2: str, min_overlap_chars=5) -> str:
        """
        Finds overlapping phrases at the end of text1 and beginning of text2 
        to cleanly merge them without repeating sentences.
        """
        text1 = text1.strip()
        text2 = text2.strip()
        
        if not text1: return text2
        if not text2: return text1

        # Check for overlapping substrings from longest possible to min_overlap_chars
        max_check = min(len(text1), len(text2))
        for i in range(max_check, min_overlap_chars - 1, -1):
            if text1.endswith(text2[:i]):
                return text1 + text2[i:]
                
        # Fallback if no clean overlapping sequence is found
        return text1 + " " + text2

    def _get_text_from_image(self, full_image: Image.Image) -> str:
        full_image = self._correct_orientation(full_image)

        image_chunks = self._slice_to_chunks(full_image)
        url = "http://127.0.0.1:7777/ocr"

        # Keywords to catch GLM-OCR refusal messages 
        refusal_keywords = ["too blurry", "appears to be a blank", "pixelated area", "no discernible"]
        
        final_rows = []

        for y, row_chunks in enumerate(image_chunks):
            row_text = ""  # Reconstruct a single horizontal row first
            
            for x, chunk in enumerate(row_chunks):
                image_buffer = io.BytesIO()
                chunk.save(image_buffer, format="PNG")
                image_buffer.seek(0)

                files = {
                    "image": (f"{y}_{x}.png", image_buffer, "image/png")
                }

                try:
                    response = requests.post(url, files=files)
                    if response.status_code == 200:
                        result_text = response.json().get("result", "").strip()
                        
                        if any(kw in result_text.lower() for kw in refusal_keywords):
                            continue
                            
                        row_text = self._merge_overlapping_text(row_text, result_text)
                    else:
                        print(f"Server Error on chunk {x}_{y}: {response.status_code}")
                except Exception as e:
                    print(f"Network error on chunk {x}_{y}: {str(e)}")
                    
            if row_text.strip():
                final_rows.append(row_text.strip())

        return "\n\n".join(final_rows)
                        