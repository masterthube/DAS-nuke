import nuke
import nukescripts
import math

class FaceTrackUI(nukescripts.PythonPanel):
    def __init__(self, node):
        super(FaceTrackUI, self).__init__('NukeFaceTrack Pro', 'com.dario.FaceTrack')
        start = int(nuke.root().firstFrame())
        end = int(nuke.root().lastFrame())
        
        self.range = nuke.String_Knob('range', 'Frame Range', f"{start}-{end}")
        
        # FIXED: Correct way to initialize Double_Knob with a value
        self.smooth = nuke.Double_Knob('smooth', 'Smoothing')
        self.smooth.setValue(0.5) 
        self.smooth.setRange(0, 1)
        
        self.addKnob(self.range)
        self.addKnob(self.smooth)

def get_face_metrics(data):
    """Calculates center, eye-width for scale, and eye-angle for rotation."""
    l_eye = data['l_eye'][1] 
    r_eye = data['r_eye'][0] 
    
    # Stable Center (Midpoint of eyes)
    cx = (l_eye[0] + r_eye[0]) / 2.0
    cy = (l_eye[1] + r_eye[1]) / 2.0
    
    dx = r_eye[0] - l_eye[0]
    dy = r_eye[1] - l_eye[1]
    dist = math.sqrt(dx**2 + dy**2)
    angle = math.degrees(math.atan2(dy, dx))
    
    return cx, cy, dist, angle

def create_all_tools(face_session, node, smooth_val=0.5):
    if not face_session: return
    sorted_frames = sorted(face_session.keys())
    ref_f = sorted_frames[0]

    stab = nuke.nodes.Transform(name="Face_UV_Stabilizer", inputs=[node])
    for k in ['translate', 'rotate', 'scale', 'center']:
        stab[k].setAnimated()

    rx, ry, rd, ra = get_face_metrics(face_session[ref_f])
    
    # EMA Smoothing variables initialized to first frame
    s_cx, s_cy, s_cd, s_ca = rx, ry, rd, ra

    for f in sorted_frames:
        data = face_session.get(f)
        if not data: continue
        
        raw_cx, raw_cy, raw_cd, raw_ca = get_face_metrics(data)
        
        # Apply Exponential Moving Average smoothing
        # Weight current frame vs historical average
        f_weight = max(0.01, smooth_val)
        s_cx = (raw_cx * f_weight) + (s_cx * (1.0 - f_weight))
        s_cy = (raw_cy * f_weight) + (s_cy * (1.0 - f_weight))
        s_cd = (raw_cd * f_weight) + (s_cd * (1.0 - f_weight))
        s_ca = (raw_ca * f_weight) + (s_ca * (1.0 - f_weight))

        # Set Center (The pivot point)
        stab['center'].setValueAt(s_cx, f, 0)
        stab['center'].setValueAt(s_cy, f, 1)
        
        # Set Translation (Difference between Reference and Current Smoothed Center)
        stab['translate'].setValueAt(rx - s_cx, f, 0)
        stab['translate'].setValueAt(ry - s_cy, f, 1)
        
        # Scale and Rotate
        scale_val = rd / s_cd if s_cd != 0 else 1.0
        stab['scale'].setValueAt(scale_val, f)
        stab['rotate'].setValueAt(ra - s_ca, f)

    print(f"Stabilization complete. Smoothing: {smooth_val}")