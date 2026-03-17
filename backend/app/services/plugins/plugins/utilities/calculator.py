"""
计算器插件

提供数学表达式计算功能，支持基本运算、三角函数、对数等。
使用安全的表达式解析，避免代码注入风险。
"""
import math
import operator
import re
from typing import Any, Dict, List
import logging

from app.services.plugins.plugin_interface import PluginInterface, PluginResult
from app.services.plugins.registry import register_plugin

logger = logging.getLogger(__name__)


@register_plugin
class CalculatorPlugin(PluginInterface):
    """
    计算器插件
    
    安全地计算数学表达式，支持：
    - 基本运算：+, -, *, /, //, %, **
    - 数学函数：sin, cos, tan, sqrt, log, log10, exp, abs, round, ceil, floor
    - 常量：pi, e
    """
    
    # ============ 元数据 ============
    name = "calculator"
    display_name = "计算器"
    description = "计算数学表达式。支持基本运算（+、-、*、/、**）和数学函数（sin、cos、sqrt、log等）。当需要进行精确计算时使用。"
    version = "1.0.0"
    author = "AI Creator"
    category = "utility"
    tags = ["计算", "数学", "工具"]
    icon = "Calculator"
    
    # 不需要用户配置
    config_schema = {}
    
    # 参数定义（用于 OpenAI function calling）
    parameters_schema = {
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "要计算的数学表达式，例如：'2 + 3 * 4'、'sqrt(16)'、'sin(pi/2)'"
            }
        },
        "required": ["expression"]
    }
    
    # ============ 安全计算支持的操作 ============
    
    # 允许的运算符
    OPERATORS = {
        '+': operator.add,
        '-': operator.sub,
        '*': operator.mul,
        '/': operator.truediv,
        '//': operator.floordiv,
        '%': operator.mod,
        '**': operator.pow,
    }
    
    # 允许的函数
    FUNCTIONS = {
        'abs': abs,
        'round': round,
        'min': min,
        'max': max,
        'sum': sum,
        # 数学函数
        'sin': math.sin,
        'cos': math.cos,
        'tan': math.tan,
        'asin': math.asin,
        'acos': math.acos,
        'atan': math.atan,
        'atan2': math.atan2,
        'sinh': math.sinh,
        'cosh': math.cosh,
        'tanh': math.tanh,
        'sqrt': math.sqrt,
        'log': math.log,
        'log10': math.log10,
        'log2': math.log2,
        'exp': math.exp,
        'pow': math.pow,
        'ceil': math.ceil,
        'floor': math.floor,
        'factorial': math.factorial,
        'gcd': math.gcd,
        'degrees': math.degrees,
        'radians': math.radians,
    }
    
    # 允许的常量
    CONSTANTS = {
        'pi': math.pi,
        'e': math.e,
        'tau': math.tau,
        'inf': math.inf,
    }
    
    def __init__(self, **config):
        super().__init__(**config)
    
    async def execute(self, expression: str = None, **kwargs) -> Dict[str, Any]:
        """
        计算数学表达式
        
        Args:
            expression: 数学表达式字符串
            
        Returns:
            计算结果
        """
        if not expression:
            return PluginResult.fail("请提供要计算的数学表达式").model_dump()
        
        try:
            # 预处理表达式
            processed = self._preprocess_expression(expression)
            
            # 安全计算
            result = self._safe_eval(processed)
            
            # 格式化结果
            if isinstance(result, float):
                # 如果结果是整数（如 4.0），显示为整数
                if result.is_integer() and abs(result) < 1e15:
                    result = int(result)
                # 否则保留合理精度
                elif abs(result) < 1e-10:
                    result = 0
                else:
                    # 保留最多 10 位有效数字
                    result = float(f"{result:.10g}")
            
            logger.info(f"Calculator: {expression} = {result}")
            
            return PluginResult.ok(
                data={
                    "expression": expression,
                    "result": result,
                    "formatted": f"{expression} = {result}"
                },
                metadata={"plugin": self.name}
            ).model_dump()
            
        except ZeroDivisionError:
            return PluginResult.fail(
                f"计算错误：除以零（表达式：{expression}）"
            ).model_dump()
        except ValueError as e:
            return PluginResult.fail(
                f"计算错误：{str(e)}（表达式：{expression}）"
            ).model_dump()
        except Exception as e:
            logger.error(f"Calculator error: {e}", exc_info=True)
            return PluginResult.fail(
                f"无法计算表达式：{expression}（{str(e)}）"
            ).model_dump()
    
    def _preprocess_expression(self, expression: str) -> str:
        """
        预处理表达式
        
        - 移除空白
        - 支持 ^ 作为幂运算
        - 支持隐式乘法 (如 2pi -> 2*pi)
        """
        # 移除多余空白
        expr = expression.strip()
        
        # 替换 ^ 为 **
        expr = expr.replace('^', '**')
        
        # 支持隐式乘法：数字后跟函数或常量
        # 2pi -> 2*pi, 3sqrt(4) -> 3*sqrt(4)
        func_names = '|'.join(self.FUNCTIONS.keys())
        const_names = '|'.join(self.CONSTANTS.keys())
        
        # 数字后跟常量
        expr = re.sub(rf'(\d)({const_names})', r'\1*\2', expr, flags=re.IGNORECASE)
        # 数字后跟函数
        expr = re.sub(rf'(\d)({func_names})\(', r'\1*\2(', expr, flags=re.IGNORECASE)
        # 右括号后跟数字或常量
        expr = re.sub(rf'\)(\d)', r')*\1', expr)
        expr = re.sub(rf'\)({const_names})', r')*\1', expr, flags=re.IGNORECASE)
        
        return expr
    
    def _safe_eval(self, expression: str) -> float:
        """
        安全地计算表达式
        
        使用 AST 解析而不是 eval()，避免代码注入
        """
        import ast
        
        # 构建安全的命名空间
        safe_namespace = {}
        safe_namespace.update(self.CONSTANTS)
        safe_namespace.update(self.FUNCTIONS)
        
        # 解析 AST
        try:
            tree = ast.parse(expression, mode='eval')
        except SyntaxError as e:
            raise ValueError(f"表达式语法错误：{e}")
        
        # 验证并计算
        return self._eval_node(tree.body, safe_namespace)
    
    def _eval_node(self, node, namespace: dict):
        """
        递归计算 AST 节点
        
        只允许安全的操作
        """
        import ast
        
        if isinstance(node, ast.Constant):  # Python 3.8+
            return node.value
        
        elif isinstance(node, ast.Name):
            name = node.id.lower()
            if name in namespace:
                return namespace[name]
            raise ValueError(f"未知的变量或常量：{node.id}")
        
        elif isinstance(node, ast.BinOp):
            left = self._eval_node(node.left, namespace)
            right = self._eval_node(node.right, namespace)
            
            op_map = {
                ast.Add: operator.add,
                ast.Sub: operator.sub,
                ast.Mult: operator.mul,
                ast.Div: operator.truediv,
                ast.FloorDiv: operator.floordiv,
                ast.Mod: operator.mod,
                ast.Pow: operator.pow,
            }
            
            op_type = type(node.op)
            if op_type in op_map:
                return op_map[op_type](left, right)
            raise ValueError(f"不支持的运算符：{op_type.__name__}")
        
        elif isinstance(node, ast.UnaryOp):
            operand = self._eval_node(node.operand, namespace)
            
            if isinstance(node.op, ast.UAdd):
                return +operand
            elif isinstance(node.op, ast.USub):
                return -operand
            raise ValueError(f"不支持的一元运算符：{type(node.op).__name__}")
        
        elif isinstance(node, ast.Call):
            # 函数调用
            if not isinstance(node.func, ast.Name):
                raise ValueError("只支持直接函数调用")
            
            func_name = node.func.id.lower()
            if func_name not in self.FUNCTIONS:
                raise ValueError(f"不支持的函数：{node.func.id}")
            
            func = self.FUNCTIONS[func_name]
            args = [self._eval_node(arg, namespace) for arg in node.args]
            
            return func(*args)
        
        elif isinstance(node, ast.Tuple):
            # 元组（用于多参数函数如 max, min）
            return tuple(self._eval_node(el, namespace) for el in node.elts)
        
        elif isinstance(node, ast.List):
            # 列表
            return [self._eval_node(el, namespace) for el in node.elts]
        
        else:
            raise ValueError(f"不支持的表达式类型：{type(node).__name__}")
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """计算器不需要配置，始终返回 True"""
        return True


# 方便测试的同步版本
def calculate(expression: str) -> Dict[str, Any]:
    """
    同步计算数学表达式（用于测试）
    """
    import asyncio
    plugin = CalculatorPlugin()
    return asyncio.run(plugin.execute(expression=expression))
