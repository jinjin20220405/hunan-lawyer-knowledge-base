#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量转换Word文档为Markdown格式
支持 .docx 和 .doc 格式
"""

import os
import sys
from pathlib import Path

try:
    from docx import Document
    from docx.oxml.text.paragraph import CT_P
    from docx.oxml.table import CT_Tbl
    from docx.table import Table, Cell
    from docx.text.paragraph import Paragraph
except ImportError:
    print("请安装依赖: pip install python-docx")
    sys.exit(1)


class DocxConverter:
    """Word文档转Markdown转换器"""

    def __init__(self, input_dir, output_dir):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def iter_block_items(self, parent):
        """
        遍历文档中的所有块元素（段落和表格）
        """
        if hasattr(parent, 'element'):
            parent_elm = parent.element.body
        else:
            parent_elm = parent

        for child in parent_elm.iterchildren():
            if isinstance(child, CT_P):
                yield Paragraph(child, parent)
            elif isinstance(child, CT_Tbl):
                yield Table(child, parent)

    def parse_table(self, table):
        """
        解析表格为Markdown格式
        """
        md_lines = []
        for row_idx, row in enumerate(table.rows):
            # 提取单元格内容
            cells = []
            for cell in row.cells:
                cell_text = cell.text.strip().replace('\n', ' ')
                cells.append(cell_text)

            # 生成Markdown表格行
            md_lines.append('| ' + ' | '.join(cells) + ' |')

            # 添加表头分隔线
            if row_idx == 0:
                separator = '| ' + ' | '.join(['---'] * len(cells)) + ' |'
                md_lines.append(separator)

        return '\n'.join(md_lines)

    def parse_paragraph(self, paragraph):
        """
        解析段落为Markdown格式
        """
        text = paragraph.text.strip()
        if not text:
            return ''

        # 检测标题
        style_name = paragraph.style.name
        if 'Heading' in style_name:
            level = style_name.replace('Heading ', '')
            try:
                level = int(level)
                return '\n' + '#' * level + ' ' + text + '\n'
            except ValueError:
                return '\n## ' + text + '\n'

        # 检测格式（粗体、斜体等）
        for run in paragraph.runs:
            if run.bold:
                text = text.replace(run.text, f"**{run.text}**")
            elif run.italic:
                text = text.replace(run.text, f"*{run.text}*")

        return text + '\n'

    def convert_docx(self, docx_path):
        """
        转换单个docx文件为Markdown
        """
        try:
            doc = Document(docx_path)

            md_content = []

            # 提取标题（从文件名或第一个段落）
            title = docx_path.stem
            md_content.append(f'# {title}\n')
            md_content.append('---\n\n')

            # 遍历所有块元素
            for block in self.iter_block_items(doc):
                if isinstance(block, Paragraph):
                    md_text = self.parse_paragraph(block)
                    if md_text:
                        md_content.append(md_text)
                elif isinstance(block, Table):
                    md_table = self.parse_table(block)
                    md_content.append('\n' + md_table + '\n')

            return ''.join(md_content)

        except Exception as e:
            print(f"转换文件 {docx_path} 时出错: {str(e)}")
            return None

    def convert_all(self):
        """
        转换目录下所有Word文档
        """
        # 支持的文件格式
        extensions = ['*.docx', '*.doc']

        converted_count = 0
        failed_count = 0

        print(f"开始扫描目录: {self.input_dir}")
        print(f"输出目录: {self.output_dir}")
        print("-" * 60)

        for ext in extensions:
            for docx_file in self.input_dir.glob(ext):
                print(f"正在转换: {docx_file.name}")

                # 转换文档
                md_content = self.convert_docx(docx_file)

                if md_content:
                    # 保存Markdown文件
                    md_filename = docx_file.stem + '.md'
                    md_path = self.output_dir / md_filename

                    with open(md_path, 'w', encoding='utf-8') as f:
                        f.write(md_content)

                    print(f"  ✓ 成功保存: {md_filename}")
                    converted_count += 1
                else:
                    print(f"  ✗ 转换失败")
                    failed_count += 1

        print("-" * 60)
        print(f"转换完成! 成功: {converted_count}, 失败: {failed_count}")


def main():
    """主函数"""
    # 设置路径
    base_dir = Path(__file__).parent.parent
    input_dir = base_dir  # 项目根目录
    output_dir = base_dir / 'knowledge-base' / '01-法律法规'

    # 创建转换器并执行转换
    converter = DocxConverter(input_dir, output_dir)
    converter.convert_all()


if __name__ == '__main__':
    main()
