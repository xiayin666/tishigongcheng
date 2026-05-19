"""
链式调用上下文管理器 - ChainedCallContext

用于在多个工具调用之间传递数据和状态，记录每一步的调用和结果，
存储中间变量供后续步骤使用，设置最大迭代次数防止无限循环。
"""
import json
from typing import Dict, List, Any, Optional


class ChainedCallContext:
    """
    链式调用上下文管理器
    
    用于管理多轮工具调用的状态和数据传递
    """
    
    def __init__(self, max_iterations: int = 10):
        """
        初始化链式调用上下文
        
        Args:
            max_iterations: 最大迭代次数，防止无限循环
        """
        self.max_iterations = max_iterations
        self.current_iteration = 0
        
        # 记录每一步的调用历史
        self.call_history: List[Dict[str, Any]] = []
        
        # 存储中间变量，供后续步骤使用
        self.variables: Dict[str, Any] = {}
        
        # 最终结果
        self.final_result: Optional[str] = None
        
        # 是否完成任务
        self.is_completed = False
        
        # 错误信息
        self.error: Optional[str] = None
    
    def add_call_record(self, step_info: Dict[str, Any]):
        """
        添加调用记录
        
        Args:
            step_info: 步骤信息，包含工具名称、参数、结果等
        """
        self.call_history.append({
            "iteration": self.current_iteration,
            **step_info
        })
    
    def set_variable(self, key: str, value: Any):
        """
        设置中间变量
        
        Args:
            key: 变量名
            value: 变量值
        """
        self.variables[key] = value
    
    def get_variable(self, key: str, default=None) -> Any:
        """
        获取中间变量
        
        Args:
            key: 变量名
            default: 默认值
            
        Returns:
            变量值或默认值
        """
        return self.variables.get(key, default)
    
    def get_all_variables(self) -> Dict[str, Any]:
        """
        获取所有中间变量
        
        Returns:
            所有变量的字典
        """
        return self.variables.copy()
    
    def can_continue(self) -> bool:
        """
        检查是否可以继续迭代
        
        Returns:
            True表示可以继续，False表示应该停止
        """
        if self.is_completed:
            return False
        
        if self.error:
            return False
        
        if self.current_iteration >= self.max_iterations:
            self.error = f"达到最大迭代次数限制 ({self.max_iterations})"
            return False
        
        return True
    
    def next_iteration(self):
        """进入下一次迭代"""
        self.current_iteration += 1
    
    def complete(self, result: str):
        """
        标记任务完成
        
        Args:
            result: 最终结果
        """
        self.is_completed = True
        self.final_result = result
    
    def fail(self, error_message: str):
        """
        标记任务失败
        
        Args:
            error_message: 错误信息
        """
        self.error = error_message
        self.is_completed = True
    
    def get_summary(self) -> Dict[str, Any]:
        """
        获取上下文摘要
        
        Returns:
            包含关键信息的摘要字典
        """
        return {
            "current_iteration": self.current_iteration,
            "max_iterations": self.max_iterations,
            "is_completed": self.is_completed,
            "has_error": self.error is not None,
            "error": self.error,
            "total_steps": len(self.call_history),
            "variables_count": len(self.variables),
            "final_result": self.final_result
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """
        将上下文转换为字典（用于序列化）
        
        Returns:
            上下文字典
        """
        return {
            "max_iterations": self.max_iterations,
            "current_iteration": self.current_iteration,
            "call_history": self.call_history,
            "variables": self.variables,
            "final_result": self.final_result,
            "is_completed": self.is_completed,
            "error": self.error
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChainedCallContext':
        """
        从字典恢复上下文
        
        Args:
            data: 上下文字典
            
        Returns:
            ChainedCallContext实例
        """
        context = cls(max_iterations=data.get('max_iterations', 10))
        context.current_iteration = data.get('current_iteration', 0)
        context.call_history = data.get('call_history', [])
        context.variables = data.get('variables', {})
        context.final_result = data.get('final_result')
        context.is_completed = data.get('is_completed', False)
        context.error = data.get('error')
        return context
    
    def __str__(self) -> str:
        """字符串表示"""
        summary = self.get_summary()
        return (
            f"ChainedCallContext(\n"
            f"  迭代次数: {summary['current_iteration']}/{summary['max_iterations']}\n"
            f"  已完成: {summary['is_completed']}\n"
            f"  步骤数: {summary['total_steps']}\n"
            f"  变量数: {summary['variables_count']}\n"
            f"  有错误: {summary['has_error']}\n"
            f")"
        )
