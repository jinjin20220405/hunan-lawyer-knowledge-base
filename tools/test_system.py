# -*- coding: utf-8 -*-
"""
湖南律师行业规范管理系统 - 系统测试脚本
测试核心功能是否正常工作
"""

import os
import sys
from pathlib import Path


def test_directory_structure():
    """测试目录结构"""
    print("\n" + "="*70)
    print("测试1: 目录结构检查")
    print("="*70)

    base_dir = Path(__file__).parent.parent
    required_dirs = [
        'knowledge-base',
        'knowledge-base/01-法律法规',
        'knowledge-base/02-行业规范',
        'knowledge-base/03-执业指引',
        'knowledge-base/04-行政文件',
        'knowledge-base/05-办事指南',
        'knowledge-base/06-地方规范',
        'tools',
        'skills'
    ]

    all_ok = True
    for dir_path in required_dirs:
        full_path = base_dir / dir_path
        if full_path.exists() and full_path.is_dir():
            print(f"  [OK] {dir_path}")
        else:
            print(f"  [FAIL] {dir_path} - 不存在")
            all_ok = False

    return all_ok


def test_knowledge_base_files():
    """测试知识库文件"""
    print("\n" + "="*70)
    print("测试2: 知识库文件检查")
    print("="*70)

    base_dir = Path(__file__).parent.parent
    kb_dir = base_dir / 'knowledge-base'

    # 统计各目录的文件数
    stats = {}
    total = 0
    for category_dir in sorted(kb_dir.iterdir()):
        if category_dir.is_dir() and category_dir.name.startswith(('01', '02', '03', '04', '05', '06')):
            count = len(list(category_dir.glob('*.md')))
            if count > 0:
                stats[category_dir.name] = count
                total += count
                print(f"  {category_dir.name}: {count} 篇")

    print(f"\n  总计: {total} 篇")

    # 检查必需文件
    required_files = [
        'knowledge-base/01-法律法规/中华人民共和国律师法.md',
        'knowledge-base/01-法律法规/律师执业管理办法.md',
        'knowledge-base/02-行业规范/湖南省律师协会章程.md',
        'skills/hunan-lawyer-management.skill.md',
        'tools/update.py',
        'README.md'
    ]

    all_ok = True
    print("\n  必需文件检查:")
    for file_path in required_files:
        full_path = base_dir / file_path
        if full_path.exists():
            print(f"    [OK] {file_path}")
        else:
            print(f"    [FAIL] {file_path} - 不存在")
            all_ok = False

    return all_ok and total >= 5


def test_skill_file():
    """测试Skill文件"""
    print("\n" + "="*70)
    print("测试3: Skill文件检查")
    print("="*70)

    base_dir = Path(__file__).parent.parent
    skill_file = base_dir / 'skills' / 'hunan-lawyer-management.skill.md'

    if not skill_file.exists():
        print("  [FAIL] Skill文件不存在")
        return False

    print("  [OK] Skill文件存在")

    # 读取并检查内容
    with open(skill_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查关键章节
    required_sections = [
        '# 湖南律师行业规范管理助手',
        '## 核心功能模块',
        '### 1️⃣ 收案审查和风险控制',
        '### 2️⃣ 利益冲突审查',
        '### 3️⃣ 律师违规行为认定',
        '## 使用示例'
    ]

    all_ok = True
    for idx, section in enumerate(required_sections, 1):
        if section in content:
            print(f"  [OK] 包含章节 {idx}")
        else:
            print(f"  [FAIL] 缺少章节 {idx}")
            all_ok = False

    return all_ok


def test_update_tool():
    """测试更新工具"""
    print("\n" + "="*70)
    print("测试4: 更新工具检查")
    print("="*70)

    base_dir = Path(__file__).parent.parent
    update_tool = base_dir / 'tools' / 'update.py'

    if not update_tool.exists():
        print("  [FAIL] update.py 不存在")
        return False

    print("  [OK] update.py 存在")

    # 读取并检查关键函数
    with open(update_tool, 'r', encoding='utf-8') as f:
        content = f.read()

    required_functions = [
        'def check_updates',
        'def generate_download_guide',
        'def show_status',
        'def add_manual_article'
    ]

    all_ok = True
    for func in required_functions:
        if func in content:
            print(f"  [OK] 包含函数: {func}")
        else:
            print(f"  [FAIL] 缺少函数: {func}")
            all_ok = False

    return all_ok


def test_file_content():
    """测试文件内容质量"""
    print("\n" + "="*70)
    print("测试5: 文件内容质量检查")
    print("="*70)

    base_dir = Path(__file__).parent.parent
    test_file = base_dir / 'knowledge-base/01-法律法规/中华人民共和国律师法.md'

    if not test_file.exists():
        print("  [FAIL] 测试文件不存在")
        return False

    with open(test_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查内容质量指标
    checks = []

    # 检查是否有标题
    if content.startswith('# '):
        checks.append(('有标题', True))
    else:
        checks.append(('有标题', False))

    # 检查内容长度
    if len(content) > 1000:
        checks.append(('内容长度充足', True))
    else:
        checks.append(('内容长度充足', False))

    # 检查是否有关键词
    keywords = ['律师', '执业', '应当']
    found_keywords = sum(1 for kw in keywords if kw in content)
    if found_keywords == len(keywords):
        checks.append(('包含关键词', True))
    else:
        checks.append(('包含关键词', False))

    all_ok = True
    for check_name, result in checks:
        if result:
            print(f"  [OK] {check_name}")
        else:
            print(f"  [FAIL] {check_name}")
            all_ok = False

    return all_ok


def test_readme():
    """测试README文档"""
    print("\n" + "="*70)
    print("测试6: README文档检查")
    print("="*70)

    base_dir = Path(__file__).parent.parent
    readme_file = base_dir / 'README.md'

    if not readme_file.exists():
        print("  [FAIL] README.md 不存在")
        return False

    print("  [OK] README.md 存在")

    with open(readme_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查关键章节
    required_sections = [
        '# 湖南律师行业规范管理系统',
        '## 快速开始',
        '## 使用律师管理Skill',
        '## 常用命令'
    ]

    all_ok = True
    for section in required_sections:
        if section in content:
            print(f"  [OK] 包含章节: {section}")
        else:
            print(f"  [FAIL] 缺少章节: {section}")
            all_ok = False

    return all_ok


def run_all_tests():
    """运行所有测试"""
    print("\n" + "#"*70)
    print("# 湖南律师行业规范管理系统 - 系统测试")
    print("#"*70)

    tests = [
        ("目录结构检查", test_directory_structure),
        ("知识库文件检查", test_knowledge_base_files),
        ("Skill文件检查", test_skill_file),
        ("更新工具检查", test_update_tool),
        ("文件内容质量检查", test_file_content),
        ("README文档检查", test_readme),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n  [ERROR] {test_name} 执行出错: {e}")
            results.append((test_name, False))

    # 总结
    print("\n" + "="*70)
    print("测试总结")
    print("="*70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"  {status} {test_name}")

    print(f"\n通过率: {passed}/{total} ({passed*100//total}%)")

    if passed == total:
        print("\n[OK] 所有测试通过！系统运行正常。")
        return 0
    else:
        print(f"\n[FAIL] {total - passed} 个测试失败，请检查上述问题。")
        return 1


if __name__ == '__main__':
    sys.exit(run_all_tests())
