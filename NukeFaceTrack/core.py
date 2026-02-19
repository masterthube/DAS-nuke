import cv2
import mediapipe as mp
import numpy as np
import nuke
import time

class FaceProcessor:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=True,
            refine_landmarks=True,
            min_detection_confidence=0.5
        )
        
        self.GROUPS = {
            "silhouette": [10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288, 397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136, 172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109],
            "l_eye": [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246],
            "r_eye": [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398],
            "lips": [61, 146, 91, 181, 84, 17, 314, 405, 321, 375, 291, 308, 324, 318, 402, 317, 14, 87, 178, 88, 95, 185, 40, 39, 37, 0, 267, 269, 270, 409]
        }

    def run_range(self, node, start, end):
        face_session = {}
        # Ensure we are using the format of the incoming node
        w, h = node.width(), node.height()
        proc_res = 512 

        ct = nuke.nodes.CurveTool(inputs=[node])
        
        for f in range(start, end + 1):
            rgb_buffer = np.zeros((proc_res, proc_res, 3), dtype=np.uint8)
            nuke.execute(ct, f, f) 

            for y in range(proc_res):
                sample_y = (y / float(proc_res)) * h
                for x in range(proc_res):
                    sample_x = (x / float(proc_res)) * w
                    
                    # Manual clip and scale
                    r = max(0, min(1, node.sample('r', sample_x, sample_y, f)))
                    g = max(0, min(1, node.sample('g', sample_x, sample_y, f)))
                    b = max(0, min(1, node.sample('b', sample_x, sample_y, f)))
                    
                    # MediaPipe wants (0,0) at top-left
                    rgb_buffer[(proc_res - 1) - y, x] = [int(r*255), int(g*255), int(b*255)]

            results = self.face_mesh.process(rgb_buffer)
            
            if results.multi_face_landmarks:
                mesh = results.multi_face_landmarks[0]
                frame_data = {}
                for name, indices in self.GROUPS.items():
                    # COORDINATE FIX: lm.x * w gives us the absolute Nuke pixel X.
                    # (1.0 - lm.y) * h flips it from AI space to Nuke space.
                    frame_data[name] = [(lm.x * w, (1.0 - lm.y) * h) for lm in [mesh.landmark[i] for i in indices]]
                face_session[f] = frame_data
                print(f"Frame {f}: Success.")
            else:
                print(f"Frame {f}: No face found.")
            
        nuke.delete(ct)
        return face_session