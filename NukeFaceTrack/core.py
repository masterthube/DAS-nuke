import cv2
import mediapipe as mp
import numpy as np
import nuke
import time
import os

class FaceProcessor:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False, 
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        self.GROUPS = {
            "silhouette": [10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288, 397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136, 172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109],
            "l_eye": [33, 133, 159, 145, 468], # Added iris
            "r_eye": [362, 263, 386, 374, 473], # Added iris
            "lips": [61, 291, 0, 17]
        }

    def run_range(self, node, start, end):
        face_session = {}
        w, h = node.width(), node.height()

        # Define a single temp file path
        temp_dir = os.path.join(os.environ.get('TEMP', '/tmp'), 'nuke_face_track').replace('\\', '/')
        if not os.path.exists(temp_dir): os.makedirs(temp_dir)
        temp_file = os.path.join(temp_dir, "temp_frame_buffer.jpg").replace('\\', '/')

        write = nuke.nodes.Write(inputs=[node], file=temp_file, file_type="jpeg", _jpeg_quality=0.85)

        try:
            for f in range(start, end + 1):
                # Overwrites the same file every time
                nuke.execute(write, f, f)
                
                img = cv2.imread(temp_file)
                if img is None: continue
                
                img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                results = self.face_mesh.process(img_rgb)

                if results.multi_face_landmarks:
                    mesh = results.multi_face_landmarks[0]
                    frame_data = {}
                    
                    for name, indices in self.GROUPS.items():
                        frame_data[name] = [(lm.x * w, (1.0 - lm.y) * h) for lm in [mesh.landmark[i] for i in indices]]
                    
                    face_session[f] = frame_data
        finally:
            nuke.delete(write)
            # Delete the final temp file so 0 JPEGs remain
            if os.path.exists(temp_file):
                os.remove(temp_file)
            
        return face_session