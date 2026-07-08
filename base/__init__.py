import os
import sys
# 获取当前文件所在目录的绝对路径
module_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(module_dir)
if module_dir not in sys.path:
    sys.path.insert(0, module_dir)

# 根目录页进行系统路径的添加
if project_root not in sys.path:
    sys.path.insert(0, project_root)
from config import Config
from logger import logger