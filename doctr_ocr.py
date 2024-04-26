from doctr.io import read_pdf
from doctr.models import ocr_predictor

predictor = ocr_predictor(
    pretrained=True,
    detect_orientation=True,
    straighten_pages=True,
)


def pdf_extractor(pdf_file_path: str):
    try:
        docs = read_pdf(pdf_file_path)
        result = predictor(docs)
        return result.render()
    except Exception as e:
        print(f"Error in pdf_extractor: {e}")
