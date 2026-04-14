import os
import json
import shutil
from datetime import datetime
from practice02.weather_tool import get_weather, WEATHER_TOOL_DEFINITION


def list_files(directory: str) -> dict:
    """
    列出某个目录下有哪些文件（包括文件的基本属性、大小等信息）
    
    Args:
        directory: 目录路径
        
    Returns:
        包含文件列表的字典
    """
    try:
        if not os.path.exists(directory):
            return {"error": f"目录不存在: {directory}"}
        
        if not os.path.isdir(directory):
            return {"error": f"路径不是目录: {directory}"}
        
        files = []
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            stat_info = os.stat(item_path)
            
            file_info = {
                "name": item,
                "path": item_path,
                "is_directory": os.path.isdir(item_path),
                "size_bytes": stat_info.st_size,
                "size_human": _format_size(stat_info.st_size),
                "created_time": datetime.fromtimestamp(stat_info.st_ctime).strftime('%Y-%m-%d %H:%M:%S'),
                "modified_time": datetime.fromtimestamp(stat_info.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                "accessed_time": datetime.fromtimestamp(stat_info.st_atime).strftime('%Y-%m-%d %H:%M:%S'),
            }
            files.append(file_info)
        
        return {
            "directory": directory,
            "total_items": len(files),
            "files": files
        }
    except Exception as e:
        return {"error": f"列出文件时出错: {str(e)}"}


def rename_file(directory: str, old_name: str, new_name: str) -> dict:
    """
    修改某个目录下某个文件的名字
    
    Args:
        directory: 目录路径
        old_name: 原文件名
        new_name: 新文件名
        
    Returns:
        操作结果字典
    """
    try:
        old_path = os.path.join(directory, old_name)
        new_path = os.path.join(directory, new_name)
        
        if not os.path.exists(old_path):
            return {"error": f"文件不存在: {old_path}"}
        
        if os.path.exists(new_path):
            return {"error": f"目标文件已存在: {new_path}"}
        
        os.rename(old_path, new_path)
        
        return {
            "success": True,
            "message": f"文件重命名成功",
            "old_path": old_path,
            "new_path": new_path
        }
    except Exception as e:
        return {"error": f"重命名文件时出错: {str(e)}"}


def delete_file(directory: str, filename: str) -> dict:
    """
    删除某个目录下的某个文件
    
    Args:
        directory: 目录路径
        filename: 要删除的文件名
        
    Returns:
        操作结果字典
    """
    try:
        file_path = os.path.join(directory, filename)
        
        if not os.path.exists(file_path):
            return {"error": f"文件不存在: {file_path}"}
        
        if os.path.isdir(file_path):
            return {"error": f"路径是目录，请使用删除目录功能: {file_path}"}
        
        os.remove(file_path)
        
        return {
            "success": True,
            "message": f"文件删除成功",
            "deleted_file": file_path
        }
    except Exception as e:
        return {"error": f"删除文件时出错: {str(e)}"}


def create_file_with_content(directory: str, filename: str, content: str) -> dict:
    """
    在某个目录下新建1个文件，并且写入内容
    
    Args:
        directory: 目录路径
        filename: 文件名
        content: 要写入的内容
        
    Returns:
        操作结果字典
    """
    try:
        if not os.path.exists(directory):
            return {"error": f"目录不存在: {directory}"}
        
        file_path = os.path.join(directory, filename)
        
        if os.path.exists(file_path):
            return {"error": f"文件已存在: {file_path}"}
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return {
            "success": True,
            "message": f"文件创建成功",
            "file_path": file_path,
            "content_length": len(content)
        }
    except Exception as e:
        return {"error": f"创建文件时出错: {str(e)}"}


def read_file_content(directory: str, filename: str) -> dict:
    """
    读取某个目录下的某个文件的内容
    
    Args:
        directory: 目录路径
        filename: 文件名
        
    Returns:
        包含文件内容的字典
    """
    try:
        file_path = os.path.join(directory, filename)
        
        if not os.path.exists(file_path):
            return {"error": f"文件不存在: {file_path}"}
        
        if os.path.isdir(file_path):
            return {"error": f"路径是目录，不是文件: {file_path}"}
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        stat_info = os.stat(file_path)
        
        return {
            "success": True,
            "file_path": file_path,
            "filename": filename,
            "size_bytes": stat_info.st_size,
            "content": content
        }
    except Exception as e:
        return {"error": f"读取文件时出错: {str(e)}"}


def _format_size(size_bytes: int) -> str:
    """将字节大小转换为人类可读格式"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.2f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"


# 工具定义（用于发送给 LLM）
TOOLS_DEFINITION = [
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "列出某个目录下有哪些文件，包括文件的基本属性、大小等信息",
            "parameters": {
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "要列出文件的目录路径"
                    }
                },
                "required": ["directory"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "rename_file",
            "description": "修改某个目录下某个文件的名字",
            "parameters": {
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "文件所在的目录路径"
                    },
                    "old_name": {
                        "type": "string",
                        "description": "原文件名"
                    },
                    "new_name": {
                        "type": "string",
                        "description": "新文件名"
                    }
                },
                "required": ["directory", "old_name", "new_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_file",
            "description": "删除某个目录下的某个文件",
            "parameters": {
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "文件所在的目录路径"
                    },
                    "filename": {
                        "type": "string",
                        "description": "要删除的文件名"
                    }
                },
                "required": ["directory", "filename"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_file_with_content",
            "description": "在某个目录下新建一个文件，并且写入内容",
            "parameters": {
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "要创建文件的目录路径"
                    },
                    "filename": {
                        "type": "string",
                        "description": "要创建的文件名"
                    },
                    "content": {
                        "type": "string",
                        "description": "要写入文件的内容"
                    }
                },
                "required": ["directory", "filename", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file_content",
            "description": "读取某个目录下的某个文件的内容",
            "parameters": {
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "文件所在的目录路径"
                    },
                    "filename": {
                        "type": "string",
                        "description": "要读取的文件名"
                    }
                },
                "required": ["directory", "filename"]
            }
        }
    },
    WEATHER_TOOL_DEFINITION
]

# 工具函数映射
AVAILABLE_FUNCTIONS = {
    "list_files": list_files,
    "rename_file": rename_file,
    "delete_file": delete_file,
    "create_file_with_content": create_file_with_content,
    "read_file_content": read_file_content,
    "get_weather": get_weather,
}
