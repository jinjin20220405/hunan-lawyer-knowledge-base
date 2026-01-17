# -*- coding: utf-8 -*-
"""
湖南律师网行业规范爬虫
爬取行业规范栏目的所有文章并转换为Markdown格式
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime
from urllib.parse import urljoin, urlparse

try:
    import requests
    from bs4 import BeautifulSoup
    import html2text
except ImportError as e:
    print(f"缺少依赖库: {e}")
    print("请运行: pip install requests beautifulsoup4 html2text")
    sys.exit(1)


class HunanLawyerCrawler:
    """湖南律师网爬虫"""

    def __init__(self, base_dir=None):
        """初始化爬虫"""
        self.base_url = "https://www.hnlx.org.cn"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

        # 设置知识库路径
        if base_dir is None:
            base_dir = Path(__file__).parent.parent
        self.base_dir = Path(base_dir)
        self.knowledge_base = self.base_dir / 'knowledge-base'

        # 记录文件
        self.record_file = self.base_dir / 'tools' / 'crawler_record.json'

        # 加载历史记录
        self.load_records()

    def load_records(self):
        """加载爬取记录"""
        if self.record_file.exists():
            with open(self.record_file, 'r', encoding='utf-8') as f:
                self.records = json.load(f)
        else:
            self.records = {
                'last_check': None,
                'articles': {}
            }

    def save_records(self):
        """保存爬取记录"""
        with open(self.record_file, 'w', encoding='utf-8') as f:
            json.dump(self.records, f, ensure_ascii=False, indent=2)

    def get_page(self, url):
        """获取页面内容"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            response.encoding = 'utf-8'
            return response.text
        except Exception as e:
            print(f"获取页面失败 {url}: {e}")
            return None

    def get_article_list(self, category_id):
        """
        获取文章列表
        category_id: 栏目ID (1=法律法规, 2=行业规范, 3=业务指引等)
        """
        url = f"{self.base_url}/index.php?m=content&c=index&a=lists&catid={category_id}"
        html = self.get_page(url)

        if not html:
            return []

        soup = BeautifulSoup(html, 'html.parser')
        articles = []

        # 查找文章链接
        for link in soup.find_all('a', href=True):
            href = link['href']

            # 匹配文章页面URL
            if 'show_n.php' in href:
                # 提取文章ID
                if 'id=' in href:
                    article_id = href.split('id=')[1].split('&')[0]
                    title = link.get_text(strip=True)

                    if title and article_id:
                        articles.append({
                            'id': article_id,
                            'title': title,
                            'url': urljoin(self.base_url, href)
                        })

        return articles

    def get_article_content(self, article_url):
        """获取文章内容"""
        html = self.get_page(article_url)
        if not html:
            return None

        soup = BeautifulSoup(html, 'html.parser')

        # 查找文章内容区域
        content_div = soup.find('div', class_='content') or soup.find('div', id='content')

        if not content_div:
            # 尝试其他选择器
            content_div = soup.find('article') or soup.find('main')

        if content_div:
            # 转换为Markdown
            h = html2text.HTML2Text()
            h.ignore_links = False
            h.ignore_images = False
            h.ignore_emphasis = False
            h.body_width = 0  # 不换行

            md_content = h.handle(str(content_div))
            return md_content.strip()

        return None

    def download_category(self, category_id, category_name):
        """下载某个分类的所有文章"""
        print(f"\n{'='*60}")
        print(f"正在爬取分类: {category_name}")
        print(f"{'='*60}")

        # 获取文章列表
        articles = self.get_article_list(category_id)

        if not articles:
            print(f"  未找到文章")
            return

        print(f"  找到 {len(articles)} 篇文章")

        # 创建输出目录
        output_dir = self.knowledge_base / self.get_category_dir(category_id)
        output_dir.mkdir(parents=True, exist_ok=True)

        # 下载每篇文章
        success_count = 0
        for idx, article in enumerate(articles, 1):
            article_id = article['id']
            title = article['title']
            url = article['url']

            print(f"\n[{idx}/{len(articles)}] {title}")

            # 检查是否已下载
            if article_id in self.records['articles']:
                last_update = self.records['articles'][article_id].get('download_time')
                print(f"  已下载 (上次: {last_update})")
                continue

            # 获取文章内容
            content = self.get_article_content(url)

            if content:
                # 保存为Markdown文件
                filename = f"{title}.md"
                # 替换文件名中的非法字符
                invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
                for char in invalid_chars:
                    filename = filename.replace(char, '_')

                file_path = output_dir / filename

                # 写入文件
                md_content = f"# {title}\n\n"
                md_content += f"**来源**: {url}\n"
                md_content += f"**爬取时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                md_content += "---\n\n"
                md_content += content

                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(md_content)

                # 记录
                self.records['articles'][article_id] = {
                    'title': title,
                    'url': url,
                    'category': category_name,
                    'download_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'file': str(file_path)
                }

                print(f"  [OK] 保存成功: {filename}")
                success_count += 1
            else:
                print(f"  [FAIL] 下载失败")

            # 延迟，避免请求过快
            time.sleep(1)

        print(f"\n分类 {category_name} 完成! 成功: {success_count}/{len(articles)}")

    def get_category_dir(self, category_id):
        """根据分类ID返回目录名"""
        categories = {
            '1': '04-行政文件',
            '2': '02-行业规范',
            '3': '03-执业指引',
            '8': '01-法律法规',
            '19': '02-行业规范',
        }
        return categories.get(str(category_id), '99-其他')

    def check_updates(self):
        """检查是否有更新"""
        print("检查更新...")
        print(f"上次检查时间: {self.records.get('last_check', '从未')}")

        # 获取当前文章列表
        current_articles = {}

        # 检查各个分类
        categories = {
            '8': '法律法规',
            '2': '行业规范',
            '3': '执业指引',
            '1': '行政文件',
        }

        for cat_id, cat_name in categories.items():
            articles = self.get_article_list(cat_id)
            for article in articles:
                current_articles[article['id']] = {
                    'title': article['title'],
                    'url': article['url'],
                    'category': cat_name
                }

        # 比较差异
        existing_ids = set(self.records['articles'].keys())
        current_ids = set(current_articles.keys())

        new_articles = current_ids - existing_ids

        if new_articles:
            print(f"\n发现 {len(new_articles)} 篇新文章:")
            for article_id in new_articles:
                info = current_articles[article_id]
                print(f"  - [{info['category']}] {info['title']}")
            return True
        else:
            print("\n没有发现新文章")
            return False

    def download_all(self):
        """下载所有分类"""
        categories = {
            '8': '法律法规',
            '2': '行业规范',
            '3': '执业指引',
            '1': '行政文件',
        }

        for cat_id, cat_name in categories.items():
            self.download_category(cat_id, cat_name)

        # 更新检查时间
        self.records['last_check'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.save_records()

        print(f"\n{'='*60}")
        print("全部完成!")
        print(f"{'='*60}")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='湖南律师网爬虫')
    parser.add_argument('--check', action='store_true', help='检查更新')
    parser.add_argument('--download', action='store_true', help='下载更新')
    parser.add_argument('--all', action='store_true', help='下载所有内容')

    args = parser.parse_args()

    crawler = HunanLawyerCrawler()

    if args.check:
        crawler.check_updates()
    elif args.download:
        crawler.download_all()
    elif args.all:
        print("开始下载所有内容...")
        crawler.download_all()
    else:
        print("用法:")
        print("  检查更新: python crawler.py --check")
        print("  下载更新: python crawler.py --download")
        print("  下载全部: python crawler.py --all")


if __name__ == '__main__':
    main()
