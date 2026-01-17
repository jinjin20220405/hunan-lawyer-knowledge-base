# -*- coding: utf-8 -*-
"""
湖南律师网知识库更新工具
提供检查更新和下载更新的功能
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# 尝试导入MCP工具支持
try:
    # 检查是否在Claude Code环境中运行
    IN_CLAUDE = os.environ.get('CLAUDE_CODE', False)
except:
    IN_CLAUDE = False


class KnowledgeBaseUpdater:
    """知识库更新工具"""

    def __init__(self, base_dir=None):
        """初始化更新工具"""
        if base_dir is None:
            base_dir = Path(__file__).parent.parent
        self.base_dir = Path(base_dir)
        self.knowledge_base = self.base_dir / 'knowledge-base'
        self.tools_dir = self.base_dir / 'tools'

        # 配置文件
        self.config_file = self.tools_dir / 'update_config.json'
        self.pending_file = self.tools_dir / 'pending_downloads.json'

        # 加载配置
        self.load_config()

        # 已知的重要文章URL
        self.known_articles = {
            '法律法规': [
                {'id': '8956', 'title': '律师执业管理办法', 'url': 'https://www.hnlx.org.cn/show_n.php?t=8&id=8956', 'category': '01-法律法规'},
            ],
            '行业规范': [
                {'id': '11637', 'title': '湖南省律师协会章程', 'url': 'https://www.hnlx.org.cn/show_n.php?t=2&id=11637', 'category': '02-行业规范'},
                {'id': '11528', 'title': '申请律师执业人员实习管理规则', 'url': 'https://www.hnlx.org.cn/show_n.php?t=2&id=11528', 'category': '02-行业规范'},
                {'id': '9384', 'title': '中华全国律师协会章程', 'url': 'https://www.hnlx.org.cn/show_n.php?t=2&id=9384', 'category': '02-行业规范'},
                {'id': '8986', 'title': '关于进一步规范律师服务收费的意见', 'url': 'https://www.hnlx.org.cn/show_n.php?t=1&id=8986', 'category': '02-行业规范'},
                {'id': '8959', 'title': '加强和规范律师事务所内部管理的规定', 'url': 'https://www.hnlx.org.cn/show_n.php?t=2&id=8959', 'category': '02-行业规范'},
            ],
        }

    def load_config(self):
        """加载配置文件"""
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        else:
            self.config = {
                'last_check': None,
                'last_update': None,
                'downloaded_articles': {}
            }

    def save_config(self):
        """保存配置文件"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)

    def check_existing_files(self):
        """检查现有文件"""
        existing = {}
        for category_dir in self.knowledge_base.iterdir():
            if category_dir.is_dir() and category_dir.name.startswith(('01', '02', '03', '04', '05', '06')):
                for file in category_dir.glob('*.md'):
                    # 读取文件获取标题
                    try:
                        with open(file, 'r', encoding='utf-8') as f:
                            first_line = f.readline().strip()
                            if first_line.startswith('# '):
                                title = first_line[2:].strip()
                                existing[title] = {
                                    'file': str(file),
                                    'category': category_dir.name
                                }
                    except:
                        pass
        return existing

    def check_updates(self):
        """检查是否有更新"""
        print("=" * 70)
        print("湖南律师网知识库更新检查")
        print("=" * 70)
        print(f"\n上次检查时间: {self.config.get('last_check', '从未')}")
        print(f"上次更新时间: {self.config.get('last_update', '从未')}")

        # 检查现有文件
        existing = self.check_existing_files()
        print(f"\n当前知识库文章数: {len(existing)} 篇")

        # 对比已知文章
        pending = []
        for category, articles in self.known_articles.items():
            for article in articles:
                title = article['title']
                if title not in existing:
                    pending.append(article)

        # 保存待下载列表
        with open(self.pending_file, 'w', encoding='utf-8') as f:
            json.dump(pending, f, ensure_ascii=False, indent=2)

        print(f"\n待下载文章数: {len(pending)} 篇")

        if pending:
            print("\n待下载文章列表:")
            print("-" * 70)
            for article in pending:
                print(f"  - [{article['category']}] {article['title']}")
                print(f"    URL: {article['url']}")
            print("\n请运行以下命令下载待下载文章:")
            print(f"  python {Path(__file__).name} --download")
        else:
            print("\n知识库已是最新，无需更新。")

        # 更新检查时间
        self.config['last_check'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.save_config()

        print("\n" + "=" * 70)

        return len(pending) > 0

    def generate_download_guide(self):
        """生成下载指南（用于Claude Code环境）"""
        if not self.pending_file.exists():
            print("请先运行检查更新: python update.py --check")
            return

        with open(self.pending_file, 'r', encoding='utf-8') as f:
            pending = json.load(f)

        if not pending:
            print("没有待下载的文章")
            return

        guide_file = self.tools_dir / 'DOWNLOAD_NEEDED.md'
        content = f"# 待下载文章清单\n\n"
        content += f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        content += f"待下载数量: {len(pending)} 篇\n\n"
        content += "---\n\n"
        content += "## 下载方法\n\n"
        content += "在Claude Code中，对每个URL使用以下命令:\n\n"
        content += "```\n"
        content += "webReader <URL>\n"
        content += "```\n\n"
        content += "然后将输出内容保存为Markdown文件。\n\n"
        content += "---\n\n"
        content += "## 待下载文章\n\n"

        for idx, article in enumerate(pending, 1):
            content += f"### {idx}. {article['title']}\n\n"
            content += f"- **分类**: {article['category']}\n"
            content += f"- **URL**: {article['url']}\n\n"
            content += f"```bash\n"
            content += f"webReader {article['url']}\n"
            content += f"```\n\n"
            content += f"保存路径: `knowledge-base/{article['category']}/{article['title']}.md`\n\n"
            content += "---\n\n"

        with open(guide_file, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"\n已生成下载指南: {guide_file}")
        print("\n请在Claude Code中查看该文件，按指南逐个下载文章。")

    def show_status(self):
        """显示知识库状态"""
        print("=" * 70)
        print("湖南律师网知识库状态")
        print("=" * 70)

        # 统计各分类文章数
        stats = {}
        total = 0
        for category_dir in sorted(self.knowledge_base.iterdir()):
            if category_dir.is_dir() and category_dir.name.startswith(('01', '02', '03', '04', '05', '06')):
                count = len(list(category_dir.glob('*.md')))
                if count > 0:
                    stats[category_dir.name] = count
                    total += count

        print(f"\n文章总数: {total} 篇\n")
        print("分类统计:")
        print("-" * 70)
        for category, count in sorted(stats.items()):
            category_name = category.split('-', 1)[1] if '-' in category else category
            print(f"  {category_name:20s}: {count:3d} 篇")

        print("\n最近更新:")
        print("-" * 70)
        print(f"  上次检查: {self.config.get('last_check', '从未')}")
        print(f"  上次更新: {self.config.get('last_update', '从未')}")

        print("\n" + "=" * 70)

    def add_manual_article(self, url, title, category):
        """手动添加文章到待下载列表"""
        # 检查分类目录是否存在
        category_dir = self.knowledge_base / category
        if not category_dir.exists():
            print(f"错误: 分类目录不存在: {category}")
            print(f"可用分类: {', '.join([d.name for d in self.knowledge_base.iterdir() if d.is_dir()])}")
            return False

        article = {
            'id': url.split('id=')[-1].split('&')[0] if 'id=' in url else 'manual',
            'title': title,
            'url': url,
            'category': category,
            'manual': True
        }

        # 加载现有待下载列表
        pending = []
        if self.pending_file.exists():
            with open(self.pending_file, 'r', encoding='utf-8') as f:
                pending = json.load(f)

        # 检查是否已存在
        for p in pending:
            if p['url'] == url:
                print(f"该URL已在待下载列表中: {title}")
                return False

        # 检查文件是否已存在
        existing = self.check_existing_files()
        if title in existing:
            print(f"该文章已存在: {existing[title]['file']}")
            return False

        pending.append(article)

        # 保存
        with open(self.pending_file, 'w', encoding='utf-8') as f:
            json.dump(pending, f, ensure_ascii=False, indent=2)

        print(f"已添加到待下载列表: {title}")
        return True


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(
        description='湖南律师网知识库更新工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  检查更新:     python update.py --check
  查看状态:     python update.py --status
  生成下载指南: python update.py --guide
  添加文章:     python update.py --add <URL> --title "标题" --category "02-行业规范"
        """
    )

    parser.add_argument('--check', action='store_true', help='检查是否有更新')
    parser.add_argument('--download', action='store_true', help='生成下载指南')
    parser.add_argument('--status', action='store_true', help='显示知识库状态')
    parser.add_argument('--add', metavar='URL', help='手动添加文章URL')
    parser.add_argument('--title', metavar='TITLE', help='文章标题（与--add一起使用）')
    parser.add_argument('--category', metavar='CATEGORY', help='分类目录（与--add一起使用）')

    args = parser.parse_args()

    updater = KnowledgeBaseUpdater()

    if args.check:
        has_updates = updater.check_updates()
        if has_updates:
            updater.generate_download_guide()

    elif args.download:
        updater.generate_download_guide()

    elif args.status:
        updater.show_status()

    elif args.add:
        if not args.title or not args.category:
            print("错误: 使用--add时必须同时提供--title和--category参数")
            return
        updater.add_manual_article(args.add, args.title, args.category)

    else:
        # 默认显示状态
        updater.show_status()
        print("\n使用 --help 查看详细帮助")


if __name__ == '__main__':
    main()
