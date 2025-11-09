import os
import shutil

# 定义节点类
class FileManagerNode:
    """
    一个用于执行文件操作（复制、移动、删除、重命名等）的自定义节点。
    """
    def __init__(self):
        # 节点执行时不需要特殊初始化
        pass

    # 节点信息定义
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "input_filepath": ("STRING", {"default": ""}),
                "operation": (["COPY", "MOVE", "DELETE", "RENAME", "CHANGE_EXT", "ADD_PREFIX", "ADD_SUFFIX"],),
            },
            "optional": {
                # 目标路径或新名称/前缀/后缀/扩展名
                "target_param": ("STRING", {"default": "", "multiline": False}),
                # 仅用于 DELETE 操作，防止误删
                "confirm_delete": ("BOOLEAN", {"default": False}),
            }
        }

    RETURN_TYPES = ("BOOLEAN", "STRING", "STRING",)
    RETURN_NAMES = ("success", "original_filepath", "output_filepath",)
    FUNCTION = "execute_operation"
    CATEGORY = "file_management" # 您可以在 ComfyUI 菜单中找到的类别

    def execute_operation(self, input_filepath, operation, target_param="", confirm_delete=False):
        # 初始化输出
        success = False
        output_filepath = "process fail"
        
        # 检查输入文件是否存在
        if operation != "DELETE" and not os.path.exists(input_filepath):
            return (False, input_filepath, f"Error: Input file not found at {input_filepath}")

        try:
            if operation == "COPY":
                # target_param 应为目标文件夹或完整目标路径
                if not target_param:
                     raise ValueError("Target path must be provided for COPY operation.")
                
                # 如果 target_param 是文件夹，则在其中使用原文件名
                if os.path.isdir(target_param):
                    new_filepath = os.path.join(target_param, os.path.basename(input_filepath))
                else:
                    new_filepath = target_param
                    
                shutil.copy2(input_filepath, new_filepath)
                success = True
                output_filepath = new_filepath

            elif operation == "MOVE":
                # target_param 应为目标文件夹或完整目标路径
                if not target_param:
                     raise ValueError("Target path must be provided for MOVE operation.")
                     
                if os.path.isdir(target_param):
                    new_filepath = os.path.join(target_param, os.path.basename(input_filepath))
                else:
                    new_filepath = target_param
                    
                shutil.move(input_filepath, new_filepath)
                success = True
                output_filepath = new_filepath

            elif operation == "DELETE":
                if not confirm_delete:
                    raise ValueError("Deletion not confirmed. Set 'confirm_delete' to True to proceed.")
                
                if not os.path.exists(input_filepath):
                    # 如果文件不存在，也算作操作成功（目标状态已达成）
                    success = True
                    output_filepath = "File already deleted/not found."
                else:
                    os.remove(input_filepath)
                    success = True
                    output_filepath = "File successfully deleted."

            elif operation == "RENAME":
                # target_param 应为新的**完整**文件名（包含扩展名）
                if not target_param:
                    raise ValueError("New file name must be provided for RENAME operation.")
                    
                dir_name = os.path.dirname(input_filepath)
                new_filepath = os.path.join(dir_name, target_param)
                os.rename(input_filepath, new_filepath)
                success = True
                output_filepath = new_filepath

            elif operation == "CHANGE_EXT":
                # target_param 应为新的扩展名（如：.png 或 png）
                if not target_param:
                    raise ValueError("New extension must be provided for CHANGE_EXT operation.")

                base, _ = os.path.splitext(input_filepath)
                # 确保扩展名以点开头
                new_ext = target_param if target_param.startswith('.') else '.' + target_param
                new_filepath = base + new_ext
                os.rename(input_filepath, new_filepath)
                success = True
                output_filepath = new_filepath

            elif operation == "ADD_PREFIX":
                # target_param 应为前缀
                if not target_param:
                    raise ValueError("Prefix must be provided for ADD_PREFIX operation.")
                    
                dir_name = os.path.dirname(input_filepath)
                file_name = os.path.basename(input_filepath)
                new_file_name = target_param + file_name
                new_filepath = os.path.join(dir_name, new_file_name)
                os.rename(input_filepath, new_filepath)
                success = True
                output_filepath = new_filepath

            elif operation == "ADD_SUFFIX":
                # target_param 应为后缀
                if not target_param:
                    raise ValueError("Suffix must be provided for ADD_SUFFIX operation.")
                    
                dir_name = os.path.dirname(input_filepath)
                base, ext = os.path.splitext(os.path.basename(input_filepath))
                new_file_name = base + target_param + ext
                new_filepath = os.path.join(dir_name, new_file_name)
                os.rename(input_filepath, new_filepath)
                success = True
                output_filepath = new_filepath

        except Exception as e:
            # 任何异常发生时，设置 success 为 False 并记录错误信息
            success = False
            output_filepath = f"Process failed: {str(e)}"

        # 返回三个输出
        return (success, input_filepath, output_filepath)

# 注册节点映射
NODE_CLASS_MAPPINGS = {
    "FileManagerNode": FileManagerNode
}

# 节点显示的友好名称
NODE_DISPLAY_NAME_MAPPINGS = {
    "FileManagerNode": "💾 File Manager"
}