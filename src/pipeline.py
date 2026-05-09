from pathlib import Path
import argparse

from src.file_classifier import FileClassifier
from src.content_extractor import ContentExtractor


def main():
    parser = argparse.ArgumentParser(
        description="Classify files and extract text from PDFs, images, and DOCX files."
    )

    parser.add_argument(
        "root_folder",
        help="Folder containing the files to process."
    )

    parser.add_argument(
        "--output-dir",
        default="outputs",
        help="Folder where CSV outputs will be saved."
    )

    parser.add_argument(
        "--tesseract-cmd",
        default=None,
        help="Optional path to tesseract.exe."
    )

    parser.add_argument(
        "--min-direct-text-length",
        type=int,
        default=30,
        help="Minimum PDF text length before OCR is used."
    )

    args = parser.parse_args()

    root_folder = Path(args.root_folder)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    inventory_output = output_dir / "inventory.csv"
    extraction_output = output_dir / "page_extraction.csv"

    classifier = FileClassifier(root_folder)
    inventory_df = classifier.discover_files()
    inventory_df.to_csv(inventory_output, index=False)

    extractor = ContentExtractor(
        min_direct_text_length=args.min_direct_text_length,
        tesseract_cmd=args.tesseract_cmd
    )

    extraction_df = extractor.process_inventory(inventory_df)
    extraction_df.to_csv(extraction_output, index=False)

    print(f"Inventory saved to: {inventory_output}")
    print(f"Extraction saved to: {extraction_output}")


if __name__ == "__main__":
    main()