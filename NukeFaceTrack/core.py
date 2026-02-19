import nuke
import cv2
import os
import json
import mp_face_mesh

class FaceProcessor:
    def __init__(self):
        self.engine = mp_face_mesh.FaceMesh(
            static_image_mode=True, 
            max_num_faces=1,
            refine_landmarks=True
        )
        # Expanded map for better tracking stability
        self.map = {
            "nose": 1,
            "l_eye": 33,
            "r_eye": 263,
            "mouth_top": 13,
            "chin": 152,
            "forehead": 10
        }

    def extract_frame(self, node, frame):
        # ... (Keep your existing extract_frame code here) ...
        temp_file = os.path.join(os.environ['TEMP'], f"mp_track_{frame}.jpg").replace("\\", "/")
        w_node = nuke.nodes.Write(file=temp_file, file_type="jpeg", _jpeg_quality=0.8)
        w_node.setInput(0, node)
        nuke.execute(w_node, frame, frame)
        nuke.delete(w_node)

        img = cv2.imread(temp_file)
        if img is None: return None
        h, w, _ = img.shape
        results = self.engine.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        if os.path.exists(temp_file): os.remove(temp_file)

        if not results.multi_face_landmarks: return None

        landmarks = results.multi_face_landmarks[0].landmark
        return {name: (landmarks[idx].x * w, (1 - landmarks[idx].y) * h) for name, idx in self.map.items()}

    def run_range(self, node, start, end):
        """Processes a range and returns a structured dictionary."""
        all_data = {}
        
        # Use a progress bar because processing takes time
        task = nuke.ProgressTask("Extracting Face Data")
        total = end - start + 1

        for i, frame in enumerate(range(start, end + 1)):
            if task.isCancelled():
                break
            task.setMessage(f"Processing frame {frame}")
            
            data = self.extract_frame(node, frame)
            if data:
                all_data[frame] = data
            
            task.setProgress(int((i / total) * 100))
            
        return all_data