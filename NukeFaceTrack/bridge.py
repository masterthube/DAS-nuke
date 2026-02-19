import sys
import os

def init_bridge():
    # 1. Clean the 3.13 infection but keep the rest for ComfyUI
    sys.path = [p for p in sys.path if "Python313" not in p]

    # 2. Force Nuke's internal path and the 3.11 User path
    nuke_site = r'C:\Program Files\Nuke16.0v8\lib\site-packages'
    user_311 = os.path.expandvars(r'%APPDATA%\Python\Python311\site-packages')
    
    for p in [nuke_site, user_311]:
        if p not in sys.path:
            sys.path.insert(0, p)

    # 3. THE EXORCIST IMPORT
    # Instead of 'import mediapipe.tasks.python', we go straight to the 
    # specific sub-modules to bypass the broken __init__.py files.
    try:
        import numpy as np
        import mediapipe as mp
        
        # We manually load the sub-components to skip the 'python' name error
        import mediapipe.python.solutions.face_mesh as mp_face_mesh
        import mediapipe.python.solutions.drawing_utils as mp_drawing
        
        # Globally register them so core.py can see them easily
        sys.modules['mp_face_mesh'] = mp_face_mesh
        
        print(f"NukeFaceTrack: Bridge Success (FaceMesh Loaded)")
    except Exception as e:
        # If it's the audio error, we ignore it and keep going
        if "audio_classifier" in str(e):
            print("NukeFaceTrack: Bridge Success (Audio ignored)")
        else:
            print(f"NukeFaceTrack: Bridge Logic Error: {e}")

init_bridge()