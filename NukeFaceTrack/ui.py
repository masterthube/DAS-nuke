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
        self.smooth.setValue(0.5)
        self.addKnob(self.range)
        self.addKnob(self.smooth)

def bake_roto_shapes(roto_node, face_session, smooth_val=0.5):
    print("\n--- [ROTO BAKE: FULL FACE] ---")
    try:
        import nuke.rotopaint as rp
        curves = roto_node['curves']
        root = curves.rootLayer
        
        # Color Definitions (RGBA)
        COLORS = {
            "FACE": (0.3, 0.2, 0.2, 0.5), 
            "EYE": (0.2, 0.5, 0.8, 1.0),  
            "LIP": (0.2, 0.8, 0.4, 1.0),  
            "NOSE": (0.7, 0.7, 0.7, 1.0)  
        }

        shape_configs = [
            {"name": "Face_Boundary", "idx": [10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288, 397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136, 172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109], "color": COLORS["FACE"]},
            {"name": "Nose_Bridge", "idx": [168, 6, 197, 195, 5], "color": COLORS["NOSE"]},
            {"name": "L_Eye", "idx": [33, 160, 158, 133, 153, 144], "color": COLORS["EYE"]},
            {"name": "R_Eye", "idx": [362, 385, 387, 263, 373, 380], "color": COLORS["EYE"]},
            {"name": "L_Brow", "idx": [70, 63, 105, 66, 107], "color": COLORS["EYE"]},
            {"name": "R_Brow", "idx": [336, 296, 334, 293, 300], "color": COLORS["EYE"]},
            {"name": "Lips_Outer", "idx": [61, 37, 0, 267, 291, 321, 14, 91], "color": COLORS["LIP"]}
        ]
        
        sorted_frames = sorted(face_session.keys())
        f_w = max(0.01, smooth_val)

        for config in shape_configs:
            name = config["name"]
            indices = config["idx"]
            color = config["color"]
            
            shape = rp.Shape(curves)
            shape.name = name
            
            # Use string keys for attributes - bypasses 'kColorRedAttribute' errors
            attrs = shape.getAttributes()
            attrs.set('r', color[0])
            attrs.set('g', color[1])
            attrs.set('b', color[2])
            attrs.set('a', color[3])
            
            for _ in indices:
                shape.append(rp.ShapeControlPoint())
            root.append(shape)
            
            # Smoothing state
            prev_pts = {i: [face_session[sorted_frames[0]]['all_pts'][idx][0], 
                            face_session[sorted_frames[0]]['all_pts'][idx][1]] 
                        for i, idx in enumerate(indices)}

            for f in sorted_frames:
                for i, pt_idx in enumerate(indices):
                    raw_pt = face_session[f]['all_pts'][pt_idx]
                    s_px = (raw_pt[0] * f_w) + (prev_pts[i][0] * (1.0 - f_w))
                    s_py = (raw_pt[1] * f_w) + (prev_pts[i][1] * (1.0 - f_w))
                    prev_pts[i] = [s_px, s_py]

                    cp = shape[i].center
                    cp.addPositionKey(f, nuke.math.Vector3(s_px, s_py, 0))

            print(f"[DEBUG] Shape Created: {name}")

        curves.changed()
        print("[DEBUG] Full Roto bake successful.")
    except Exception as e:
        print(f"[DEBUG] Roto Error Detail: {type(e).__name__} - {str(e)}")
    print("--- [ROTO BAKE END] ---\n")

def create_all_tools(face_session, node, smooth_val=0.5):
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

    roto_node = nuke.nodes.Roto(name="Face_Roto_Mesh", inputs=[stab])
    bake_roto_shapes(roto_node, face_session, smooth_val)

    print(f"--- [END SESSION v{VERSION}] ---")