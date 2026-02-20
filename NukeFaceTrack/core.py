import cv2
import mediapipe as mp
import numpy as np
import nuke
import os
import math  # <--- CRITICAL: Must be in this file!

# Import project metadata
try:
    from . import metadata
    VERSION = metadata.metadata.get("version", "1.1.4")
except ImportError:
    VERSION = "1.1.4"

class FaceProcessor:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Canonical 3D Face Model (Proportional head for solvePnP)
        self.model_points = np.array([
            (0.0, 0.0, 0.0),             # Nose tip
            (0.0, -330.0, -65.0),        # Chin
            (-225.0, 170.0, -135.0),     # Left eye corner
            (225.0, 170.0, -135.0),      # Right eye corner
            (-150.0, -150.0, -125.0),    # Left mouth corner
            (150.0, -150.0, -125.0)      # Right mouth corner
        ], dtype=np.float64)

    def solve_3d_pose(self, mesh, w, h):
        """Translates 2D points into 3D Rotation and Translation."""
        image_points = np.array([
            (mesh.landmark[1].x * w, mesh.landmark[1].y * h),
            (mesh.landmark[152].x * w, mesh.landmark[152].y * h),
            (mesh.landmark[33].x * w, mesh.landmark[33].y * h),
            (mesh.landmark[263].x * w, mesh.landmark[263].y * h),
            (mesh.landmark[61].x * w, mesh.landmark[61].y * h),
            (mesh.landmark[291].x * w, mesh.landmark[291].y * h)
        ], dtype=np.float64)

        focal_length = w
        camera_matrix = np.array([[focal_length, 0, w/2], [0, focal_length, h/2], [0, 0, 1]], dtype="double")
        dist_coeffs = np.zeros((4,1))
        
        _, rot_vec, trans_vec = cv2.solvePnP(self.model_points, image_points, camera_matrix, dist_coeffs)
        
        # Decompose rotation matrix to Euler angles
        rmat, _ = cv2.Rodrigues(rot_vec)
        sy = math.sqrt(rmat[0,0] * rmat[0,0] + rmat[1,0] * rmat[1,0])
        if sy > 1e-6:
            x = math.atan2(rmat[2,1], rmat[2,2])
            y = math.atan2(-rmat[2,0], sy)
            z = math.atan2(rmat[1,0], rmat[0,0])
        else:
            x = math.atan2(-rmat[1,2], rmat[1,1])
            y = math.atan2(-rmat[2,0], sy)
            z = 0
        
        return [math.degrees(x), math.degrees(y), math.degrees(z)], trans_vec.flatten().tolist()

    def run_range(self, node, start, end):
        face_session = {}
        w, h = node.width(), node.height()
        temp_file = os.path.join(os.environ.get('TEMP', '/tmp'), "nuke_face_tmp.jpg").replace('\\', '/')
        
        # Temporary Write node for frame extraction
        write = nuke.nodes.Write(inputs=[node], file=temp_file, file_type="jpeg", _jpeg_quality=0.8)

        try:
            for f in range(start, end + 1):
                nuke.execute(write, f, f)
                img = cv2.imread(temp_file)
                if img is None: continue
                
                results = self.face_mesh.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

                if results.multi_face_landmarks:
                    mesh = results.multi_face_landmarks[0]
                    rot, trans = self.solve_3d_pose(mesh, w, h)
                    
                    face_session[f] = {
                        "all_pts": [(lm.x * w, (1.0 - lm.y) * h, lm.z * w) for lm in mesh.landmark],
                        "rot": rot,
                        "trans": trans
                    }
        finally:
            nuke.delete(write)
            if os.path.exists(temp_file): os.remove(temp_file)
            
        return face_session