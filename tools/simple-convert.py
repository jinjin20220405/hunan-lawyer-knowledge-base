# -*- coding: utf-8 -*-
import sys
import os
from pathlib import Path

try:
    from docx import Document
except ImportError:
    print("python-docx not found")
    sys.exit(1)

def convert_docx_to_markdown(docx_path, output_path):
    """转换单个docx文件"""
    try:
        doc = Document(docx_path)
        md_content = []

        # 添加标题
        title = Path(docx_path).stem
        md_content.append(f'# {title}\n\n')

        # 遍历所有段落
        for para in doc.paragraphs:
            text = para.text.strip()
            if text:
                md_content.append(text + '\n')

        # 保存文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(''.join(md_content))

        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

# 转换所有Word文档
base_dir = Path(__file__).parent.parent
input_dir = base_dir
output_dir = base_dir / 'knowledge-base' / '01-法律法规'

output_dir.mkdir(parents=True, exist_ok=True)

# 查找所有docx文件
docx_files = list(input_dir.glob('*.docx'))

print(f"Found {len(docx_files)} docx files")
print(f"Output directory: {output_dir}")

for docx_file in docx_files:
    print(f"Converting: {docx_file.name}")
    md_file = output_dir / (docx_file.stem + '.md')

    if convert_docx_to_markdown(docx_file, md_file):
        print(f"  Success: {md_file.name}")
    else:
        print(f"  Failed")

print("Conversion complete!")
