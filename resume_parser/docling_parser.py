# resume_parser/docling_parser.py
from docling.extract import Extractor

def parse_resume(filepath):
    extractor = Extractor()
    result = extractor.parse(filepath)
    return result.to_dict()
