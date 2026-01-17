# -*- coding: utf-8 -*-
"""
湖南律师网智能爬虫 v2.0
使用Claude MCP webReader工具，更可靠地爬取内容
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime


class SmartCrawler:
    """智能爬虫 - 使用MCP webReader"""

    def __init__(self, base_dir=None):
        """初始化爬虫"""
        # 设置知识库路径
        if base_dir is None:
            base_dir = Path(__file__).parent.parent
        self.base_dir = Path(base_dir)
        self.knowledge_base = self.base_dir / 'knowledge-base'

        # 记录文件
        self.record_file = self.base_dir / 'tools' / 'articles.json'

        # 加载文章列表
        self.load_article_list()

    def load_article_list(self):
        """加载文章列表"""
        if self.record_file.exists():
            with open(self.record_file, 'r', encoding='utf-8') as f:
                self.articles = json.load(f)
        else:
            self.articles = {
                '法律法规': [
                    {'id': '8956', 'title': '律师执业管理办法', 'url': 'https://www.hnlx.org.cn/show_n.php?t=8&id=8956'},
                ],
                '行业规范': [
                    {'id': '11637', 'title': '湖南省律师协会章程', 'url': 'https://www.hnlx.org.cn/show_n.php?t=2&id=11637'},
                    {'id': '11528', 'title': '申请律师执业人员实习管理规则', 'url': 'https://www.hnlx.org.cn/show_n.php?t=2&id=11528'},
                    {'id': '9384', 'title': '中华全国律师协会章程', 'url': 'https://www.hnlx.org.cn/show_n.php?t=2&id=9384'},
                    {'id': '8986', 'title': '关于进一步规范律师服务收费的意见', 'url': 'https://www.hnlx.org.cn/show_n.php?t=1&id=8986'},
                    {'id': '8959', 'title': '加强和规范律师事务所内部管理的规定', 'url': 'https://www.hnlx.org.cn/show_n.php?t=2&id=8959'},
                ],
                '执业指引': [],
                '行政文件': [],
                '办事指南': []
            }

    def save_article_list(self):
        """保存文章列表"""
        with open(self.record_file, 'w', encoding='utf-8') as f:
            json.dump(self.articles, f, ensure_ascii=False, indent=2)

    def get_category_dir(self, category):
        """根据分类返回目录名"""
        mapping = {
            '法律法规': '01-法律法规',
            '行业规范': '02-行业规范',
            '执业指引': '03-执业指引',
            '行政文件': '04-行政文件',
            '办事指南': '05-办事指南',
            '地方规范': '06-地方规范'
        }
        return mapping.get(category, '99-其他')

    def clean_filename(self, filename):
        """清理文件名中的非法字符"""
        invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        return filename

    def create_manual_download_guide(self):
        """创建手动下载指南"""
        guide_file = self.base_dir / 'tools' / 'MANUAL_DOWNLOAD.md'

        content = """# 湖南律师网内容下载指南

## 方法一：使用Claude MCP webReader工具（推荐）

在Claude Code中使用以下命令：

```
# 使用webReader工具
webReader https://www.hnlx.org.cn/show_n.php?t=2&id=11637
```

然后将输出内容保存为Markdown文件。

## 方法二：手动复制粘贴

1. 访问湖南律师网：https://www.hnlx.org.cn
2. 进入"行业规范"栏目
3. 打开需要的文章
4. 全选复制内容
5. 粘贴到Markdown文件中

## 已知重要文章URL

### 行业规范
- 湖南省律师协会章程: https://www.hnlx.org.cn/show_n.php?t=2&id=11637
- 申请律师执业人员实习管理规则: https://www.hnlx.org.cn/show_n.php?t=2&id=11528
- 中华全国律师协会章程: https://www.hnlx.org.cn/show_n.php?t=2&id=9384
- 关于进一步规范律师服务收费的意见: https://www.hnlx.org.cn/show_n.php?t=1&id=8986
- 加强和规范律师事务所内部管理的规定: https://www.hnlx.org.cn/show_n.php?t=2&id=8959

### 法律法规
- 律师执业管理办法: https://www.hnlx.org.cn/show_n.php?t=8&id=8956

## 文件命名规范

所有文档使用Markdown格式，放在对应目录下：
- 01-法律法规/
- 02-行业规范/
- 03-执业指引/
- 04-行政文件/
- 05-办事指南/
- 06-地方规范/

## 快速下载脚本

如果想批量下载，可以逐个运行以下命令（在Claude Code中）：
"""

        # 添加所有文章的下载命令
        for category, articles in self.articles.items():
            if articles:
                content += f"\n### {category}\n\n"
                for article in articles[:5]:  # 只显示前5个
                    content += f"```\nwebReader {article['url']}\n```\n\n"

        with open(guide_file, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"已创建下载指南: {guide_file}")
        return guide_file


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='湖南律师网智能爬虫')
    parser.add_argument('--guide', action='store_true', help='创建手动下载指南')
    parser.add_argument('--list', action='store_true', help='列出所有文章')

    args = parser.parse_args()

    crawler = SmartCrawler()

    if args.guide:
        crawler.create_manual_download_guide()
    elif args.list:
        print("\n文章列表:")
        print("=" * 60)
        for category, articles in crawler.articles.items():
            print(f"\n{category} ({len(articles)}篇):")
            for article in articles:
                print(f"  - {article['title']}")
                print(f"    URL: {article['url']}")
    else:
        print("用法:")
        print("  创建下载指南: python smart-crawler.py --guide")
        print("  列出文章列表: python smart-crawler.py --list")


if __name__ == '__main__':
    main()
