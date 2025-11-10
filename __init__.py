# 从同一个目录下的 file_manager.py 文件中导入我们的节点类
from .cato_file_manager import FileManagerNode

# 1. 节点类映射 (必须导出)
# 键是 ComfyUI 内部使用的唯一名称，值是对应的 Python 类
NODE_CLASS_MAPPINGS = {
    "FileManagerNode": FileManagerNode
}

# 2. 节点显示名称映射 (可选，用于在菜单中显示更友好的名称)
NODE_DISPLAY_NAME_MAPPINGS = {
    "FileManagerNode": "💾 File Manager"
}

# 3. 必须在 __init__.py 中导出所有需要被 ComfyUI 发现的变量
# 确保 ComfyUI 能够找到 NODE_CLASS_MAPPINGS
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']

# 4. 尝试使用新的 ComfyExtension API
try:
    from comfy_api.latest import ComfyExtension, io
    
    async def comfy_entrypoint() -> ComfyExtension:
        class CatoAutomationExtension(ComfyExtension):
            async def get_node_list(self) -> list[type[io.ComfyNode]]:
                return [FileManagerNode]
        
        return CatoAutomationExtension()
    
    # 如果成功导入新API，将 comfy_entrypoint 添加到导出列表
    __all__.append('comfy_entrypoint')
    
except ImportError:
    # 如果新API不可用，回退到传统方式
    pass