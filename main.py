import logging
from pathlib import Path

from fpdf import FPDF, XPos, YPos
from pypdf import PdfWriter, PdfReader
from playwright.sync_api import sync_playwright

logging.basicConfig(level=logging.INFO)

urls = [
    "https://cs231n.github.io/",
    "https://cs231n.github.io/classification/",
    "https://cs231n.github.io/linear-classify/",
    "https://cs231n.github.io/optimization-1/",
    "https://cs231n.github.io/optimization-2/",
    "https://cs231n.github.io/neural-networks-1/",
    "https://cs231n.github.io/neural-networks-2/",
    "https://cs231n.github.io/neural-networks-3/",
    "https://cs231n.github.io/neural-networks-case-study/",
    "https://cs231n.github.io/convolutional-networks/",
    "https://cs231n.github.io/understanding-cnn/",
    "https://cs231n.github.io/transfer-learning/",
]


def capture_webpage(url: str) -> tuple[str, bytes]:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url)
        logging.info(f"Capturing {page.url}.")
        page_name = page.url.split("/")[-2]
        pdf_content = page.pdf()
        browser.close()
    return page_name, pdf_content


def merge_pdfs(pdf_files: list[Path], output_file: Path) -> None:
    merger = PdfWriter()
    for pdf_file in pdf_files:
        merger.append(pdf_file)
    merger.write(output_file)
    merger.close()


def create_toc(chapters: list[tuple[str, Path]], output_file: Path) -> None:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_left_margin(10)
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(
        0, 10, "Table of Contents", 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C"
    )  # Updated ln parameter
    pdf.set_font("Helvetica", "", 12)

    current_page = 1  # Start counting from the ToC page
    page_width = pdf.w - 2 * pdf.l_margin  # Calculate the usable page width

    for chapter, path in chapters:
        reader = PdfReader(str(path))
        num_pages = len(reader.pages)

        chapter_str = f"{chapter}"
        page_num_str = f"{current_page + 1}"  # +1 to account for the ToC page itself
        page_num_width = pdf.get_string_width(page_num_str)

        pdf.cell(
            0, 10, chapter_str, new_x=XPos.LMARGIN, new_y=YPos.NEXT
        )
        pdf.ln(-10)
        pdf.cell(
            page_width - page_num_width,
            10,
            page_num_str,
            0,
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT,
            align="R",
        )

        current_page += num_pages

    pdf.output(str(output_file))


if __name__ == "__main__":
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)

    chapters: list[tuple[str, Path]] = []
    for i, url in enumerate(urls):
        page_name, pdf_content = capture_webpage(url)
        if page_name == "cs231n.github.io":
            page_name = "home"
        output_path = data_dir / f"cs231n_{i}_{page_name}.pdf"
        logging.info(f"Writing {output_path}.")
        output_path.write_bytes(pdf_content)
        chapters.append((page_name, output_path))

    logging.info("Creating Table of Contents.")
    toc_path = data_dir / "cs231n-toc.pdf"
    create_toc(chapters, toc_path)
    output_paths = [toc_path] + [path for _, path in chapters]

    logging.info("Merging PDFs.")
    merge_pdfs(output_paths, data_dir / "cs231n-book.pdf")
