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
        start, end = int(nuke.root().firstFrame()), int(nuke.root().lastFrame())
        self.range = nuke.String_Knob('range', 'Frame Range', f"{start}-{end}")
        self.smooth = nuke.Double_Knob('smooth', 'Smoothing')
        self.smooth.setValue(0.25)
        self.addKnob(self.range)
        self.addKnob(self.smooth)

def bake_roto_shapes(roto_node, face_session):
    print("\n--- [ROTO KEYING START] ---")
    try:
        import nuke.rotopaint as rp
        curves = roto_node['curves']
        root = curves.rootLayer
        
        indices = [61, 37, 0, 267, 291, 321, 14, 91] # Lips
        shape = rp.Shape(curves)
        shape.name = "Lips_Final"
        
        for _ in indices:
            shape.append(rp.ShapeControlPoint())
        root.append(shape)
        
        sorted_frames = sorted(face_session.keys())

        for f in sorted_frames:
            for i, pt_idx in enumerate(indices):
                pt = face_session[f]['all_pts'][pt_idx]
                px, py = pt[0], pt[1]
                
                # THE NUKE 16 DISCOVERY:
                # Based on our debug, 'center' is an AnimControlPoint.
                # It has 'addPositionKey' which takes (time, Vector3).
                cp = shape[i].center
                
                # Create a Nuke Vector3 for the position
                pos_vec = nuke.math.Vector3(px, py, 0)
                
                # Method: addPositionKey(time, value)
                cp.addPositionKey(f, pos_vec)
                
            if f % 25 == 0:
                print(f"[DEBUG] Frame {f} | addPositionKey used at ({px:.1f}, {py:.1f})")

        curves.changed()
        print("[DEBUG] Roto bake successful via addPositionKey.")
    except Exception as e:
        print(f"[DEBUG] Roto Final Attempt Failed: {e}")
    print("--- [ROTO KEYING END] ---\n")

def create_all_tools(face_session, node, smooth_val=0.25):
    print(f"--- [START SESSION v{VERSION}] ---")
    
    # PROTECTED TRANSFORM MATH
    stab = nuke.nodes.Transform(name="Face_UV_Stabilizer", inputs=[node])
    for k in ['translate', 'rotate', 'scale', 'center']: 
        stab[k].setAnimated()

    sorted_frames = sorted(face_session.keys())
    ref_f = sorted_frames[0]
    rx, ry, rd = get_face_metrics(face_session[ref_f])
    s_cx, s_cy, s_cd = rx, ry, rd
    
    for f in sorted_frames:
        cx, cy, cd = get_face_metrics(face_session[f])
        f_w = max(0.01, smooth_val)
        s_cx = (cx * f_w) + (s_cx * (1.0 - f_w))
        s_cy = (cy * f_w) + (s_cy * (1.0 - f_w))
        s_cd = (cd * f_w) + (s_cd * (1.0 - f_w))

        stab['center'].setValueAt(s_cx, f, 0)
        stab['center'].setValueAt(s_cy, f, 1)
        stab['translate'].setValueAt(rx - s_cx, f, 0)
        stab['translate'].setValueAt(ry - s_cy, f, 1)
        stab['scale'].setValueAt(rd / s_cd, f)

    # MODULAR ROTO CALL
    roto_node = nuke.nodes.Roto(name="Face_Roto_Mesh", inputs=[stab])
    bake_roto_shapes(roto_node, face_session)

    print(f"--- [END SESSION v{VERSION}] ---")