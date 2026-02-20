import nuke
import nukescripts
import math

VERSION = "1.1.9"

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

def bake_camera_matchmove(face_session, smooth_val=0.5, pos_x=0, pos_y=0):
    """Bakes 3D Camera and Axis with proximity placement."""
    try:
        cam = nuke.nodes.Camera3(name="Face_Matchmove_Cam")
        axis = nuke.nodes.Axis3(name="Face_Rotation_Axis")
        
        # Position 3D nodes to the right of the main pipe
        cam.setXYpos(pos_x + 300, pos_y)
        axis.setXYpos(pos_x + 300, pos_y + 50)
        
        for n in [cam, axis]:
            n['translate'].setAnimated()
            n['rotate'].setAnimated()
            
        sorted_frames = sorted(face_session.keys())
        f_w = max(0.01, smooth_val)
        s_trans = list(face_session[sorted_frames[0]]['trans'])
        s_rot = list(face_session[sorted_frames[0]]['rot'])
        
        for f in sorted_frames:
            data = face_session[f]
            for i in range(3):
                s_trans[i] = (data['trans'][i] * f_w) + (s_trans[i] * (1.0 - f_w))
                s_rot[i] = (data['rot'][i] * f_w) + (s_rot[i] * (1.0 - f_w))
                cam['translate'].setValueAt(s_trans[i], f, i)
                cam['rotate'].setValueAt(s_rot[i], f, i)
                axis['translate'].setValueAt(s_trans[i], f, i)
                axis['rotate'].setValueAt(s_rot[i], f, i)
    except: pass

def bake_roto_shapes(roto_node, face_session, smooth_val=0.5):
    import nuke.rotopaint as rp
    curves = roto_node['curves']
    root = curves.rootLayer
    COLORS = {"FACE": (0.3, 0.2, 0.2, 0.5), "EYE": (0.2, 0.5, 0.8, 1.0), "LIP": (0.2, 0.8, 0.4, 1.0), "NOSE": (0.7, 0.7, 0.7, 1.0)}
    
    shape_configs = [
        {"name": "Lips_Outer", "idx": [61, 37, 0, 267, 291, 321, 14, 91], "color": COLORS["LIP"]},
        {"name": "R_Brow", "idx": [336, 296, 334, 293, 300], "color": COLORS["EYE"]},
        {"name": "L_Brow", "idx": [70, 63, 105, 66, 107], "color": COLORS["EYE"]},
        {"name": "R_Eye", "idx": [362, 385, 387, 263, 373, 380], "color": COLORS["EYE"]},
        {"name": "L_Eye", "idx": [33, 160, 158, 133, 153, 144], "color": COLORS["EYE"]},
        {"name": "Nose_Bridge", "idx": [168, 6, 197, 195, 5], "color": COLORS["NOSE"]},
        {"name": "Face_Boundary", "idx": [10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288, 397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136, 172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109], "color": COLORS["FACE"]}
    ]

    sorted_frames = sorted(face_session.keys())
    f_w = max(0.01, smooth_val)
    for config in shape_configs:
        shape = rp.Shape(curves)
        shape.name = config["name"]
        for i, c in enumerate(['r', 'g', 'b', 'a']): shape.getAttributes().set(c, config["color"][i])
        for _ in config["idx"]: shape.append(rp.ShapeControlPoint())
        root.append(shape)
        
        prev_pts = {i: [face_session[sorted_frames[0]]['all_pts'][idx][0], face_session[sorted_frames[0]]['all_pts'][idx][1]] for i, idx in enumerate(config["idx"])}
        for f in sorted_frames:
            for i, pt_idx in enumerate(config["idx"]):
                raw_pt = face_session[f]['all_pts'][pt_idx]
                s_px = (raw_pt[0] * f_w) + (prev_pts[i][0] * (1.0 - f_w))
                s_py = (raw_pt[1] * f_w) + (prev_pts[i][1] * (1.0 - f_w))
                prev_pts[i] = [s_px, s_py]
                shape[i].center.addPositionKey(f, nuke.math.Vector3(s_px, s_py, 0))
    curves.changed()

def create_all_tools(face_session, node, smooth_val=0.5):
    print(f"--- [START SESSION v{VERSION}] ---")
    orig_x, orig_y = node.xpos(), node.ypos()

    # 1. ROTO (Left of Read)
    roto_node = nuke.nodes.Roto(name="Face_Roto_Overlay")
    roto_node.setXYpos(orig_x - 200, orig_y + 100)
    bake_roto_shapes(roto_node, face_session, smooth_val)

    # 2. MERGE (A = Roto, B = Read)
    merge_node = nuke.nodes.Merge2(name="Roto_Check_Merge", operation="over", mix=0.5)
    merge_node.setInput(0, roto_node) # Pipe A
    merge_node.setInput(1, node)      # Pipe B
    merge_node.setXYpos(orig_x, orig_y + 150)

    # 3. STABILIZER (Below Merge)
    stab = nuke.nodes.Transform(name="Face_UV_Stabilizer")
    stab.setInput(0, merge_node)
    stab.setXYpos(orig_x, orig_y + 250)
    
    for k in ['translate', 'rotate', 'scale', 'center']: stab[k].setAnimated()
    sorted_frames = sorted(face_session.keys()); ref_f = sorted_frames[0]
    rx, ry, rd = get_face_metrics(face_session[ref_f]); s_cx, s_cy, s_cd = rx, ry, rd
    
    for f in sorted_frames:
        cx, cy, cd = get_face_metrics(face_session[f])
        f_w = max(0.01, smooth_val)
        s_cx = (cx * f_w) + (s_cx * (1.0 - f_w)); s_cy = (cy * f_w) + (s_cy * (1.0 - f_w)); s_cd = (cd * f_w) + (s_cd * (1.0 - f_w))
        stab['center'].setValueAt(s_cx, f, 0); stab['center'].setValueAt(s_cy, f, 1)
        stab['translate'].setValueAt(rx - s_cx, f, 0); stab['translate'].setValueAt(ry - s_cy, f, 1); stab['scale'].setValueAt(rd / s_cd, f)

    # 4. 3D NODES (Spawned near the Read node)
    bake_camera_matchmove(face_session, smooth_val, orig_x, orig_y)
    
    print(f"--- [END SESSION v{VERSION}] ---")