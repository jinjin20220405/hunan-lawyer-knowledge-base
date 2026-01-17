#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
湖南省律师协会行业规范爬虫
爬取 https://www.hnlx.org.cn/ 网站行业规范下的所有内容
支持增量更新：自动检测新增知识并提示用户确认
"""

import os
import re
import sys
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from pathlib import Path
import json

# 修复Windows控制台编码问题
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 配置
BASE_URL = "https://www.hnlx.org.cn/"
# 使用脚本所在目录的相对路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "hunan_lawyer_data")

# 行业规范分类配置
CATEGORIES = {
    "法律法规": {"t": "8", "pages": 1},
    "行政文件": {"t": "1", "pages": 1},
    "行业文件": {"t": "2", "pages": 3},
    "业务指引": {"t": "4", "pages": 2},
    "办事指南": {"t": "5", "pages": 1},
}

# 请求头（模拟浏览器）
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}


def create_output_dir():
    """创建输出目录"""
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    for category in CATEGORIES.keys():
        Path(os.path.join(OUTPUT_DIR, category)).mkdir(parents=True, exist_ok=True)
    print(f"[OK] 输出目录已创建: {OUTPUT_DIR}")


def get_page(url, max_retries=3):
    """获取页面内容，带重试机制"""
    for i in range(max_retries):
        try:
            response = requests.get(url, headers=HEADERS, timeout=30, verify=False)
            response.encoding = response.apparent_encoding or 'utf-8'
            if response.status_code == 200:
                return response
            else:
                print(f"  [!] 状态码: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"  [!] 请求失败 ({i+1}/{max_retries}): {e}")
            if i < max_retries - 1:
                time.sleep(2)
    return None


def sanitize_filename(name):
    """清理文件名，移除不合法字符"""
    # 移除或替换不合法的文件名字符
    name = re.sub(r'[<>:"/\\|?*]', '', name)
    name = name.strip()
    # 限制文件名长度
    if len(name) > 150:
        name = name[:150]
    return name


def extract_article_content(url, title, category):
    """提取文章内容"""
    print(f"  [->] 正在下载: {title[:50]}...")
    response = get_page(url)
    if not response:
        return None

    soup = BeautifulSoup(response.text, 'html.parser')

    # 查找文章内容区域 - 尝试多种可能的选择器
    content_div = None
    possible_selectors = [
        ('div', {'class': 'article-content'}),
        ('div', {'class': 'content'}),
        ('div', {'class': 'article'}),
        ('article', {}),
        ('div', {'class': 'main-content'}),
        ('div', {'class': 'detail-content'}),
        ('div', {'id': 'content'}),
        ('div', {'id': 'article-content'}),
    ]

    for tag, attrs in possible_selectors:
        content_div = soup.find(tag, attrs)
        if content_div:
            break

    # 如果还是找不到，尝试查找包含大量文本的div
    if not content_div:
        for div in soup.find_all('div'):
            text = div.get_text(strip=True)
            if len(text) > 200:  # 至少200个字符
                content_div = div
                break

    if content_div:
        # 清理内容
        # 移除脚本和样式
        for script in content_div.find_all(['script', 'style', 'noscript']):
            script.decompose()

        # 获取文本
        content = content_div.get_text(separator='\n', strip=True)
        # 清理多余的空行
        content = re.sub(r'\n{3,}', '\n\n', content)
        # 清理多余的空格
        content = re.sub(r' +', ' ', content)
        return content

    return None


def get_article_list(category_name, category_config):
    """获取某分类下的所有文章列表"""
    articles = []
    t_param = category_config["t"]
    max_pages = category_config["pages"]

    print(f"\n[LIST] 正在获取 [{category_name}] 的文章列表...")

    for page in range(1, max_pages + 1):
        print(f"  [PAGE] 第 {page}/{max_pages} 页...")
        url = f"{BASE_URL}list.php?t={t_param}"
        if page > 1:
            url += f"&page={page}"

        response = get_page(url)
        if not response:
            print(f"  [!] 第 {page} 页获取失败")
            continue

        soup = BeautifulSoup(response.text, 'html.parser')

        # 查找文章链接 - 使用更精确的选择器
        seen_urls = set()
        for link in soup.find_all('a', href=True):
            href = link['href']
            if 'show_n.php' in href:
                # 去重
                if href in seen_urls:
                    continue
                seen_urls.add(href)

                # 提取文章标题
                # 通常链接在 <h3><a>标题</a></h3> 结构中
                parent = link.find_parent()
                if parent and parent.name in ['h3', 'h2', 'h4']:
                    title = link.get_text(strip=True)
                else:
                    title = link.get_text(strip=True)

                # 过滤掉无意义的标题
                if title and title not in ['▶', '更多', '下一页', '上一页'] and len(title) > 2:
                    # 构建完整URL
                    full_url = urljoin(BASE_URL, href)
                    articles.append({
                        'title': title,
                        'url': full_url,
                        'category': category_name
                    })

        time.sleep(0.5)  # 避免请求过快

    print(f"  [OK] 找到 {len(articles)} 篇文章")
    return articles


def save_article(article, content):
    """保存文章为Markdown文件"""
    category = article['category']
    title = article['title']

    # 创建安全的文件名
    safe_title = sanitize_filename(title)
    filename = f"{safe_title}.md"

    # 文件路径
    filepath = os.path.join(OUTPUT_DIR, category, filename)

    # 写入文件
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"# {title}\n\n")
        f.write(f"> **来源**: {article['url']}\n")
        f.write(f"> **分类**: {category}\n")
        f.write(f"> **爬取时间**: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("---\n\n")
        f.write(content)

    return filepath


def save_progress(articles_data):
    """保存进度到JSON文件"""
    progress_file = os.path.join(OUTPUT_DIR, "progress.json")
    with open(progress_file, 'w', encoding='utf-8') as f:
        json.dump(articles_data, f, ensure_ascii=False, indent=2)


def load_progress():
    """加载进度"""
    progress_file = os.path.join(OUTPUT_DIR, "progress.json")
    if os.path.exists(progress_file):
        with open(progress_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def check_new_articles(online_articles):
    """检查是否有新文章"""
    progress = load_progress()
    new_articles = []

    for article in online_articles:
        article_key = f"{article['category']}_{article['title']}"
        if article_key not in progress:
            new_articles.append(article)

    return new_articles


def ask_user_confirmation(new_articles):
    """询问用户是否下载新文章"""
    print("\n" + "=" * 60)
    print("[发现新内容] 检测到有新的知识文档！")
    print("=" * 60)

    if not new_articles:
        print("[OK] 没有新文章需要下载")
        return False

    print(f"\n新增文章总数: {len(new_articles)} 篇\n")

    # 按分类显示新文章
    categories = {}
    for article in new_articles:
        cat = article['category']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(article)

    for category, articles in categories.items():
        print(f"【{category}】({len(articles)}篇)")
        for i, article in enumerate(articles[:5], 1):  # 每个分类只显示前5篇
            print(f"  {i}. {article['title'][:60]}")
        if len(articles) > 5:
            print(f"  ... 还有 {len(articles) - 5} 篇")
        print()

    print("=" * 60)

    while True:
        try:
            choice = input("[询问] 是否下载这些新文章？(y/n/a=全部): ").strip().lower()
            if choice in ['y', 'yes', '是', 'Y']:
                return True
            elif choice in ['n', 'no', '否', 'N']:
                return False
            elif choice in ['a', 'all', '全部', 'A']:
                print("[INFO] 将下载所有文章（包括已存在的）")
                return 'all'
            else:
                print("[!] 请输入 y(是) 或 n(否)")
        except (EOFError, KeyboardInterrupt):
            print("\n[!] 操作已取消")
            return False


def download_articles(articles, force=False):
    """下载文章列表"""
    progress = load_progress()
    success_count = 0
    failed_count = 0

    total = len(articles)
    for i, article in enumerate(articles, 1):
        print(f"\n[{i}/{total}] ", end='')

        # 检查是否已经下载过
        article_key = f"{article['category']}_{article['title']}"
        if article_key in progress and not force:
            print(f"[SKIP] {article['title'][:50]}... (已存在)")
            continue

        # 提取内容
        content = extract_article_content(article['url'], article['title'], article['category'])

        if content and len(content) > 100:  # 确保内容不为空且有一定长度
            # 保存文章
            filepath = save_article(article, content)
            print(f"[OK] 已保存: {os.path.basename(filepath)}")
            success_count += 1

            # 记录进度
            progress[article_key] = {
                'title': article['title'],
                'url': article['url'],
                'category': article['category'],
                'filepath': filepath,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            save_progress(progress)
        else:
            print(f"[FAIL] 内容提取失败: {article['title'][:50]}...")
            failed_count += 1

        # 延迟避免请求过快
        time.sleep(0.5)

    return success_count, failed_count


def generate_index(all_articles):
    """生成索引文件"""
    print("\n[INDEX] 生成索引文件...")
    index_file = os.path.join(OUTPUT_DIR, "索引.md")

    with open(index_file, 'w', encoding='utf-8') as f:
        f.write("# 湖南省律师协会行业规范知识库索引\n\n")
        f.write(f"**更新时间**: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"**文章总数**: {len(all_articles)}\n\n")
        f.write("---\n\n")

        for category in CATEGORIES.keys():
            f.write(f"## {category}\n\n")
            category_articles = [a for a in all_articles if a['category'] == category]
            for i, article in enumerate(category_articles, 1):
                safe_title = sanitize_filename(article['title'])
                f.write(f"{i}. [{article['title']}]({category}/{safe_title}.md)\n")
            f.write("\n")

    print(f"[OK] 索引文件已生成: {index_file}")


def main():
    """主函数"""
    print("=" * 60)
    print("[CRAWLER] 湖南省律师协会行业规范爬虫")
    print("=" * 60)

    # 创建输出目录
    create_output_dir()

    # 检查是否已有数据
    progress = load_progress()
    has_existing_data = len(progress) > 0

    if has_existing_data:
        print(f"\n[INFO] 检测到已有 {len(progress)} 篇文章")
        print("[INFO] 将检查是否有新内容...\n")

    all_articles = []
    new_articles = []

    # 遍历所有分类
    for category_name, category_config in CATEGORIES.items():
        # 获取文章列表
        articles = get_article_list(category_name, category_config)
        all_articles.extend(articles)

    # 检查新文章
    new_articles = check_new_articles(all_articles)

    # 生成索引（包含所有文章）
    generate_index(all_articles)

    # 根据情况决定是否下载
    if has_existing_data:
        if not new_articles:
            print("\n" + "=" * 60)
            print("[COMPLETE] 知识库已是最新，无需更新")
            print("=" * 60)
            return
        else:
            # 询问用户
            choice = ask_user_confirmation(new_articles)
            if choice is False:
                print("\n[CANCEL] 已取消下载")
                return
            elif choice == 'all':
                # 下载所有文章
                print("\n[DOWNLOAD] 开始下载所有文章...")
                success, failed = download_articles(all_articles, force=True)
            else:
                # 只下载新文章
                print("\n[DOWNLOAD] 开始下载新文章...")
                success, failed = download_articles(new_articles)
    else:
        # 首次运行，下载所有
        print("\n[FIRST RUN] 首次运行，开始下载所有文章...")
        success, failed = download_articles(all_articles)

    # 输出结果
    print("\n" + "=" * 60)
    print(f"[COMPLETE] 爬取完成！")
    print(f"  - 成功: {success} 篇")
    if failed > 0:
        print(f"  - 失败: {failed} 篇")
    print(f"  - 总数: {len(all_articles)} 篇")
    print(f"  - 位置: {OUTPUT_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    import ssl
    import warnings

    # 禁用SSL警告（因为该网站SSL证书有问题）
    ssl._create_default_https_context = ssl._create_unverified_context
    warnings.filterwarnings('ignore', message='Unverified HTTPS request')

    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[INTERRUPT] 用户中断操作")
    except Exception as e:
        print(f"\n\n[ERROR] 发生错误: {e}")
        import traceback
        traceback.print_exc()
