import pdfplumber
from PIL import Image

def slice_to_grid(pil_img, chunk_size=512, overlap=32) -> list[list[Image.Image]]:
    """
    Slices a large image into a grid of square chunks for TrOCR.
    """
    width, height = pil_img.size
    chunks = []
    
    step = chunk_size - overlap
    
    for y in range(0, height, step):
        line_chunks = []
        for x in range(0, width, step):
            right = min(x + chunk_size, width)
            bottom = min(y + chunk_size, height)
            box = (x, y, right, bottom)
            
            chunk = pil_img.crop(box)
            
            if chunk.size != (chunk_size, chunk_size):
                new_chunk = Image.new("RGB", (chunk_size, chunk_size), (255, 255, 255))
                new_chunk.paste(chunk, (0, 0))
                chunk = new_chunk
                
            line_chunks.append(chunk)
        chunks.append(line_chunks)
            
    return chunks

def get_page_images(pdf_object:pdfplumber.pdf.PDF) -> list[Image.Image]:
    pdf_page_images = []

    for page in pdf_object.pages:
        pdf_page_images.append(slice_to_grid(page.to_image(resolution=200).original.convert("RGB").rotate(-90, expand=True)))

    return pdf_page_images

