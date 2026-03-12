import os
import sys
from PIL import Image
from pypdf import PdfReader, PdfWriter

IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp")

def main():
    output_name = "combined.pdf"
    writer = PdfWriter()
    temp_pdfs = []
    current_dir = os.getcwd()

    for filename in sorted(os.listdir(current_dir)):
        filepath = os.path.join(current_dir, filename)

        if not os.path.isfile(filepath):
            continue

        if filename == output_name:
            continue

        # PDFs
        if filename.lower().endswith(".pdf"):
            reader = PdfReader(filepath)
            for page in reader.pages:
                writer.add_page(page)

        # Images
        elif filename.lower().endswith(IMAGE_EXTENSIONS):
            image = Image.open(filepath)
            if image.mode != "RGB":
                image = image.convert("RGB")

            temp_pdf = filepath + ".tmp.pdf"
            image.save(temp_pdf)
            temp_pdfs.append(temp_pdf)

            reader = PdfReader(temp_pdf)
            for page in reader.pages:
                writer.add_page(page)

    if not writer.pages:
        print("❌ No PDFs or images found.")
        return

    with open(output_name, "wb") as f:
        writer.write(f)

    for temp in temp_pdfs:
        os.remove(temp)

    print(f"✅ Created: {os.path.join(current_dir, output_name)}")

if __name__ == "__main__":
    main()
