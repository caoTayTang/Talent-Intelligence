import os
print("Đang chuẩn bị import thư viện...")

import json
from docling.document_converter import DocumentConverter

print("Import thành công! Đang khởi động test...")

def test_docling(file_path: str):
    print(f"🚀 Đang khởi động Docling và phân tích file: {file_path}...")
    
    # Khởi tạo converter
    converter = DocumentConverter()
    
    # Thực hiện convert
    result = converter.convert(file_path)
    document = result.document
    
    # Xuất file Markdown để test nhanh
    markdown_output = document.export_to_markdown()
    with open("output_test.md", "w", encoding="utf-8") as f:
        f.write(markdown_output)
    print("✅ Đã xuất thành công file: output_test.md")

if __name__ == "__main__":
    print("123")
    SAMPLE_PDF_PATH = "/mnt/d/bku_docs/Research/monoIA.pdf"
    test_docling(SAMPLE_PDF_PATH)