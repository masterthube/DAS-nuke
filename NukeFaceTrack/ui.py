import nuke
import nukescripts
import math

VERSION = "1.1.4"

def get_face_metrics(data):
    pts = data['all_pts']
    cx = (pts[33][0] + pts[263][0]) / 2.0
    cy = (pts[33][1] + pts[263][1]) / 2.0
    dist = math.sqrt((pts[263][0]-pts[33][0])**2 + (pts[263][1]-pts[33][1])**2)
    return cx, cy, dist

class FaceTrackUI(nukescripts.PythonPanel):
    def __init__(self, node):
        super(FaceTrackUI, self).__init__(f'NukeFaceTrack v{VERSION}', 'com.dario.FaceTrack')
        self.range = nuke.String_Knob('range', 'Frame Range', f"{int(nuke.root().firstFrame())}-{int(nuke.root().lastFrame())}")
        self.smooth = nuke.Double_Knob('smooth', 'Smoothing')
        self.smooth.setValue(0.25)
        self.addKnob(self.range)
        self.addKnob(self.smooth)

def create_all_tools(face_session, node, smooth_val=0.25):
    print(f"--- [EMERGENCY REVERT v{VERSION}] ---")
    
    # 1. RAW DATA CHECK
    sorted_frames = sorted(face_session.keys())
    ref_f = sorted_frames[0]
    raw_x, raw_y, raw_d = get_face_metrics(face_session[ref_f])
    print(f"[DEBUG] RAW DATA START: x={raw_x}, y={raw_y}")

    # 2. NODES
    stab = nuke.nodes.Transform(name="Face_UV_Stabilizer", inputs=[node])
    
    for k in ['translate', 'rotate', 'scale', 'center']: 
        stab[k].setAnimated()

    # 3. THE WORKING MATH (NO WIDTH MULTIPLICATION)
    rx, ry, rd = raw_x, raw_y, raw_d
    s_cx, s_cy, s_cd = rx, ry, rd

    for f in sorted_frames:
        data = face_session[f]
        cx, cy, cd = get_face_metrics(data)
        
        f_w = max(0.01, smooth_val)
        s_cx = (cx * f_w) + (s_cx * (1.0 - f_w))
        s_cy = (cy * f_w) + (s_cy * (1.0 - f_w))
        s_cd = (cd * f_w) + (s_cd * (1.0 - f_w))

        # SET KNOBS
        stab['center'].setValueAt(s_cx, f, 0)
        stab['center'].setValueAt(s_cy, f, 1)
        stab['translate'].setValueAt(rx - s_cx, f, 0)
        stab['translate'].setValueAt(ry - s_cy, f, 1)
        stab['scale'].setValueAt(rd / s_cd, f)

    print("--- TRANSFORM RESTORED ---")