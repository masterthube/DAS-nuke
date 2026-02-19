import os

# ENVIRONMENT VARIABLES
# COMFYUI_DIR = os.getenv('NUKE_COMFYUI_DIR', 'C:/ComfyUI_windows_portable')
COMFYUI_DIR = 'C:/ComfyUI_windows_portable/ComfyUI'
# IP = os.getenv('NUKE_COMFYUI_IP', '127.0.0.1')
IP = '127.0.0.1'
# PORT = int(os.getenv('NUKE_COMFYUI_PORT', '8188'))
PORT = 8188
COMFYUI2NUKE = os.path.dirname(__file__)
IMAGE_OUTPUT_WITHIN_PROJECT = os.getenv('IMAGE_OUTPUT_WITHIN_PROJECT', False)

# SETTINGS
UPDATE_MENU_AT_START = False
USE_EXR_TO_LOAD_IMAGES = False
DISPLAY_META_IN_READ_NODE = True
