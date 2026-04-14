"""
文件工具测试脚本
用于测试5个文件操作功能
"""
import os
import json
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from practice02.file_tools import (
    list_files,
    rename_file,
    delete_file,
    create_file_with_content,
    read_file_content
)


def test_all_functions():
    """测试所有文件操作功能"""
    
    # 创建测试目录
    test_dir = "test_directory"
    if not os.path.exists(test_dir):
        os.makedirs(test_dir)
        print(f"✓ 创建测试目录: {test_dir}")
    
    print("\n" + "="*60)
    print("测试1: 创建文件并写入内容")
    print("="*60)
    result = create_file_with_content(test_dir, "test1.txt", "这是第一个测试文件的内容\nHello World!")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    print("\n" + "="*60)
    print("测试2: 再创建一个文件")
    print("="*60)
    result = create_file_with_content(test_dir, "test2.txt", "这是第二个测试文件\nPython is great!")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    print("\n" + "="*60)
    print("测试3: 列出目录下的所有文件")
    print("="*60)
    result = list_files(test_dir)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    print("\n" + "="*60)
    print("测试4: 读取文件内容")
    print("="*60)
    result = read_file_content(test_dir, "test1.txt")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    print("\n" + "="*60)
    print("测试5: 重命名文件")
    print("="*60)
    result = rename_file(test_dir, "test1.txt", "renamed_test.txt")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    print("\n" + "="*60)
    print("测试6: 再次列出文件（查看重命名结果）")
    print("="*60)
    result = list_files(test_dir)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    print("\n" + "="*60)
    print("测试7: 删除文件")
    print("="*60)
    result = delete_file(test_dir, "test2.txt")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    print("\n" + "="*60)
    print("测试8: 最后列出文件（查看删除结果）")
    print("="*60)
    result = list_files(test_dir)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    # 清理测试目录
    print("\n" + "="*60)
    print("清理测试文件...")
    print("="*60)
    try:
        for item in os.listdir(test_dir):
            item_path = os.path.join(test_dir, item)
            if os.path.isfile(item_path):
                os.remove(item_path)
        os.rmdir(test_dir)
        print("✓ 测试目录已清理")
    except Exception as e:
        print(f"清理时出错: {e}")


if __name__ == '__main__':
    test_all_functions()
