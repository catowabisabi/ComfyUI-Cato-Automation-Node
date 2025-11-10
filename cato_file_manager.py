import os
import shutil

try:
    from comfy.comfy_types.node_typing import IO
    from comfy_api.latest import io
    
    # 使用新的 ANY 类型定义
    anything = io.Custom(IO.ANY)
    
    class FileManagerNode(io.ComfyNode):
        @classmethod
        def define_schema(cls):
            return io.Schema(
                node_id="FileManagerNode",
                category="Cato Automation/File Management",
                display_name="💾 File Manager",
                description="执行文件操作（复制、移动、删除、重命名等）的自定义节点",
                inputs=[
                    io.String.Input("input_filepath", default=""),
                    io.Combo.Input("operation", options=["COPY", "MOVE", "DELETE", "RENAME", "CHANGE_EXT", "ADD_PREFIX", "ADD_SUFFIX"]),
                    anything.Input("trigger", optional=True),
                    io.String.Input("target_path", default="", optional=True),
                    io.String.Input("new_filename", default="", optional=True),
                    io.String.Input("new_extension", default="", optional=True),
                    io.String.Input("prefix", default="", optional=True),
                    io.String.Input("suffix", default="", optional=True),
                    io.Boolean.Input("confirm_delete", default=False, optional=True),
                ],
                outputs=[
                    anything.Output("passthrough", display_name="passthrough"),
                    io.Boolean.Output("success", display_name="success"), 
                    io.String.Output("original_filepath", display_name="original_filepath"),
                    io.String.Output("output_filepath", display_name="output_filepath"),
                    io.String.Output("operation_info", display_name="operation_info"),
                ],
            )
        
        @classmethod
        def execute(cls, input_filepath, operation, trigger=None, target_path="", 
                   new_filename="", new_extension="", prefix="", suffix="", 
                   confirm_delete=False):
            """
            执行文件操作
            """
            success = False
            output_filepath = "process fail"
            
            # 检查输入文件是否存在(DELETE 操作除外)
            if operation != "DELETE" and not os.path.exists(input_filepath):
                error_msg = f"Error: Input file not found at {input_filepath}"
                operation_info = cls._format_operation_info(operation, False, input_filepath, error_msg)
                return io.NodeOutput(trigger, False, input_filepath, error_msg, operation_info)

            try:
                if operation == "COPY":
                    if not target_path:
                        raise ValueError("Target path must be provided for COPY operation.")
                    
                    if os.path.isdir(target_path):
                        new_filepath = os.path.join(target_path, os.path.basename(input_filepath))
                    else:
                        new_filepath = target_path
                        target_dir = os.path.dirname(new_filepath)
                        if target_dir:
                            os.makedirs(target_dir, exist_ok=True)
                        
                    shutil.copy2(input_filepath, new_filepath)
                    success = True
                    output_filepath = new_filepath

                elif operation == "MOVE":
                    if not target_path:
                        raise ValueError("Target path must be provided for MOVE operation.")
                         
                    if os.path.isdir(target_path):
                        new_filepath = os.path.join(target_path, os.path.basename(input_filepath))
                    else:
                        new_filepath = target_path
                        target_dir = os.path.dirname(new_filepath)
                        if target_dir:
                            os.makedirs(target_dir, exist_ok=True)
                        
                    shutil.move(input_filepath, new_filepath)
                    success = True
                    output_filepath = new_filepath

                elif operation == "DELETE":
                    if not confirm_delete:
                        raise ValueError("Deletion not confirmed. Set 'confirm_delete' to True to proceed.")
                    
                    if not os.path.exists(input_filepath):
                        success = True
                        output_filepath = "File already deleted/not found."
                    else:
                        os.remove(input_filepath)
                        success = True
                        output_filepath = "File successfully deleted."

                elif operation == "RENAME":
                    if not new_filename:
                        raise ValueError("New file name must be provided for RENAME operation.")
                        
                    dir_name = os.path.dirname(input_filepath)
                    new_filepath = os.path.join(dir_name, new_filename)
                    os.rename(input_filepath, new_filepath)
                    success = True
                    output_filepath = new_filepath

                elif operation == "CHANGE_EXT":
                    if not new_extension:
                        raise ValueError("New extension must be provided for CHANGE_EXT operation.")

                    base, _ = os.path.splitext(input_filepath)
                    new_ext = new_extension if new_extension.startswith('.') else '.' + new_extension
                    new_filepath = base + new_ext
                    os.rename(input_filepath, new_filepath)
                    success = True
                    output_filepath = new_filepath

                elif operation == "ADD_PREFIX":
                    if not prefix:
                        raise ValueError("Prefix must be provided for ADD_PREFIX operation.")
                        
                    dir_name = os.path.dirname(input_filepath)
                    file_name = os.path.basename(input_filepath)
                    new_file_name = prefix + file_name
                    new_filepath = os.path.join(dir_name, new_file_name)
                    os.rename(input_filepath, new_filepath)
                    success = True
                    output_filepath = new_filepath

                elif operation == "ADD_SUFFIX":
                    if not suffix:
                        raise ValueError("Suffix must be provided for ADD_SUFFIX operation.")
                        
                    dir_name = os.path.dirname(input_filepath)
                    base, ext = os.path.splitext(os.path.basename(input_filepath))
                    new_file_name = base + suffix + ext
                    new_filepath = os.path.join(dir_name, new_file_name)
                    os.rename(input_filepath, new_filepath)
                    success = True
                    output_filepath = new_filepath

            except Exception as e:
                success = False
                output_filepath = f"Process failed: {str(e)}"

            # 生成操作信息摘要
            operation_info = cls._format_operation_info(
                operation, success, input_filepath, output_filepath
            )

            return io.NodeOutput(trigger, success, input_filepath, output_filepath, operation_info)
        
        @classmethod
        def _format_operation_info(cls, operation, success, original_path, output_path):
            """格式化操作信息用于显示"""
            status = "✅ SUCCESS" if success else "❌ FAILED"
            
            info = f"""╔══════════════════════════════════════════════════════════════
║ FILE MANAGER OPERATION INFO
╠══════════════════════════════════════════════════════════════
║ Operation:        {operation}
║ Operation Status: {status}
║ Original Path:    {original_path}
║ Output Path:      {output_path}
╚══════════════════════════════════════════════════════════════"""
            
            return info

except ImportError:
    # 回退到旧API实现
    class FileManagerNode:
        """
        一个用于执行文件操作（复制、移动、删除、重命名等）的自定义节点。
        添加了 any 类型的触发输入和输出,确保节点按顺序执行。
        """
        def __init__(self):
            pass

        @classmethod
        def IS_CHANGED(cls, **kwargs):
            # 每次都执行,确保节点按顺序运行
            return float("nan")
        
        @classmethod
        def INPUT_TYPES(cls):
            return {
                "required": {
                    "input_filepath": ("STRING", {"default": ""}),
                    "operation": (["COPY", "MOVE", "DELETE", "RENAME", "CHANGE_EXT", "ADD_PREFIX", "ADD_SUFFIX"],),
                },
                "optional": {
                    # any 类型的触发输入,可以接受任何类型
                    "trigger": ("*",),
                    # 目标路径 (用于 COPY, MOVE)
                    "target_path": ("STRING", {"default": "", "multiline": False}),
                    # 新文件名 (用于 RENAME)
                    "new_filename": ("STRING", {"default": "", "multiline": False}),
                    # 新扩展名 (用于 CHANGE_EXT, 如: .png 或 png)
                    "new_extension": ("STRING", {"default": "", "multiline": False}),
                    # 前缀 (用于 ADD_PREFIX)
                    "prefix": ("STRING", {"default": "", "multiline": False}),
                    # 后缀 (用于 ADD_SUFFIX)
                    "suffix": ("STRING", {"default": "", "multiline": False}),
                    # 仅用于 DELETE 操作,防止误删
                    "confirm_delete": ("BOOLEAN", {"default": False}),
                }
            }

        RETURN_TYPES = ("*", "BOOLEAN", "STRING", "STRING", "STRING",)
        RETURN_NAMES = ("passthrough", "success", "original_filepath", "output_filepath", "operation_info",)
        FUNCTION = "execute_operation"
        CATEGORY = "Cato Automation/File Management"
        OUTPUT_NODE = True

        def execute_operation(self, input_filepath, operation, 
                             trigger=None, target_path="", new_filename="", new_extension="", 
                             prefix="", suffix="", confirm_delete=False):
            """
            执行文件操作
            """
            success = False
            output_filepath = "process fail"
            
            # 检查输入文件是否存在(DELETE 操作除外)
            if operation != "DELETE" and not os.path.exists(input_filepath):
                error_msg = f"Error: Input file not found at {input_filepath}"
                operation_info = self._format_operation_info(operation, False, input_filepath, error_msg)
                return (trigger, False, input_filepath, error_msg, operation_info)

            try:
                if operation == "COPY":
                    if not target_path:
                        raise ValueError("Target path must be provided for COPY operation.")
                    
                    if os.path.isdir(target_path):
                        new_filepath = os.path.join(target_path, os.path.basename(input_filepath))
                    else:
                        new_filepath = target_path
                        target_dir = os.path.dirname(new_filepath)
                        if target_dir:
                            os.makedirs(target_dir, exist_ok=True)
                        
                    shutil.copy2(input_filepath, new_filepath)
                    success = True
                    output_filepath = new_filepath

                elif operation == "MOVE":
                    if not target_path:
                        raise ValueError("Target path must be provided for MOVE operation.")
                         
                    if os.path.isdir(target_path):
                        new_filepath = os.path.join(target_path, os.path.basename(input_filepath))
                    else:
                        new_filepath = target_path
                        target_dir = os.path.dirname(new_filepath)
                        if target_dir:
                            os.makedirs(target_dir, exist_ok=True)
                        
                    shutil.move(input_filepath, new_filepath)
                    success = True
                    output_filepath = new_filepath

                elif operation == "DELETE":
                    if not confirm_delete:
                        raise ValueError("Deletion not confirmed. Set 'confirm_delete' to True to proceed.")
                    
                    if not os.path.exists(input_filepath):
                        success = True
                        output_filepath = "File already deleted/not found."
                    else:
                        os.remove(input_filepath)
                        success = True
                        output_filepath = "File successfully deleted."

                elif operation == "RENAME":
                    if not new_filename:
                        raise ValueError("New file name must be provided for RENAME operation.")
                        
                    dir_name = os.path.dirname(input_filepath)
                    new_filepath = os.path.join(dir_name, new_filename)
                    os.rename(input_filepath, new_filepath)
                    success = True
                    output_filepath = new_filepath

                elif operation == "CHANGE_EXT":
                    if not new_extension:
                        raise ValueError("New extension must be provided for CHANGE_EXT operation.")

                    base, _ = os.path.splitext(input_filepath)
                    new_ext = new_extension if new_extension.startswith('.') else '.' + new_extension
                    new_filepath = base + new_ext
                    os.rename(input_filepath, new_filepath)
                    success = True
                    output_filepath = new_filepath

                elif operation == "ADD_PREFIX":
                    if not prefix:
                        raise ValueError("Prefix must be provided for ADD_PREFIX operation.")
                        
                    dir_name = os.path.dirname(input_filepath)
                    file_name = os.path.basename(input_filepath)
                    new_file_name = prefix + file_name
                    new_filepath = os.path.join(dir_name, new_file_name)
                    os.rename(input_filepath, new_filepath)
                    success = True
                    output_filepath = new_filepath

                elif operation == "ADD_SUFFIX":
                    if not suffix:
                        raise ValueError("Suffix must be provided for ADD_SUFFIX operation.")
                        
                    dir_name = os.path.dirname(input_filepath)
                    base, ext = os.path.splitext(os.path.basename(input_filepath))
                    new_file_name = base + suffix + ext
                    new_filepath = os.path.join(dir_name, new_file_name)
                    os.rename(input_filepath, new_filepath)
                    success = True
                    output_filepath = new_filepath

            except Exception as e:
                success = False
                output_filepath = f"Process failed: {str(e)}"

            # 生成操作信息摘要
            operation_info = self._format_operation_info(
                operation, success, input_filepath, output_filepath
            )

            # 返回五个输出
            return (trigger, success, input_filepath, output_filepath, operation_info)
        
        def _format_operation_info(self, operation, success, original_path, output_path):
            """格式化操作信息用于显示"""
            status = "✅ SUCCESS" if success else "❌ FAILED"
            
            info = f"""╔══════════════════════════════════════════════════════════════
║ FILE MANAGER OPERATION INFO
╠══════════════════════════════════════════════════════════════
║ Operation:        {operation}
║ Operation Status: {status}
║ Original Path:    {original_path}
║ Output Path:      {output_path}
╚══════════════════════════════════════════════════════════════"""
            
            return info

# 注册节点映射
NODE_CLASS_MAPPINGS = {
    "FileManagerNode": FileManagerNode
}

# 节点显示的友好名称
NODE_DISPLAY_NAME_MAPPINGS = {
    "FileManagerNode": "💾 File Manager"
}