import nuke
import cv2
import os
import mp_face_mesh

class FaceProcessor:
    def __init__(self):
        # Initialize the MediaPipe FaceMesh engine in high-accuracy mode
        self.engine = mp_face_mesh.FaceMesh(
            static_image_mode=True, 
            max_num_faces=1,
            refine_landmarks=True
        )
        
        # Mapping specific indices to human-readable names
        # Forehead (10), Chin (152), Left Eye (33), Right Eye (263)
        self.map = {
            "nose": 1,
            "l_eye": 33,
            "r_eye": 263,
            "mouth_top": 13,
            "chin": 152,
            "forehead": 10
        }

    def extract_frame(self, node, frame):
        """Renders a frame, analyzes landmarks, and converts to Nuke pixel space."""
        # 1. Get Node Resolution (The tracking must match the input size)
        w = node.width()
        h = node.height()

        # 2. Render Temporary Frame for Analysis
        temp_file = os.path.join(os.environ['TEMP'], f"mp_analysis_{frame}.jpg").replace("\\", "/")
        write = nuke.nodes.Write(file=temp_file, file_type="jpeg", _jpeg_quality=0.8)
        write.setInput(0, node)
        
        try:
            nuke.execute(write, frame, frame)
        finally:
            nuke.delete(write)

        # 3. MediaPipe Processing
        img = cv2.imread(temp_file)
        if img is None:
            return None
        
        # Convert BGR (OpenCV) to RGB (MediaPipe)
        results = self.engine.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        
        # Cleanup disk immediately
        if os.path.exists(temp_file):
            os.remove(temp_file)

        if not results.multi_face_landmarks:
            return None

        # 4. Data Extraction & Coordinate Transformation
        landmarks = results.multi_face_landmarks[0].landmark
        frame_data = {}
        
        for name, idx in self.map.items():
            lm = landmarks[idx]
            
            # X Calculation: Normalized value * Width
            pixel_x = lm.x * w
            
            # Y Calculation: MediaPipe is 0 (top), Nuke is 0 (bottom).
            # Transformation: (1 - normalized_y) * Height
            pixel_y = (1 - lm.y) * h 
            
            frame_data[name] = (pixel_x, pixel_y)
            
        return frame_data

    def run_range(self, node, start, end):
        """Processes a sequence and returns a dict of results."""
        all_data = {}
        
        # Create a progress bar in the Nuke UI
        task = nuke.ProgressTask("Tracking Face...")
        total_frames = end - start + 1

        for i, frame in enumerate(range(start, end + 1)):
            if task.isCancelled():
                nuke.message("Tracking Cancelled by User.")
                break
                
            task.setMessage(f"Processing: Frame {frame}")
            data = self.extract_frame(node, frame)
            
            if data:
                all_data[frame] = data
            
            # Update progress bar percentage
            task.setProgress(int((i / total_frames) * 100))
            
        return all_data