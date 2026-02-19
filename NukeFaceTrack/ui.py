import nuke
import nukescripts
import nuke.rotopaint as rp
import math

class FaceTrackUI(nukescripts.PythonPanel):
    def __init__(self, node):
        super(FaceTrackUI, self).__init__('NukeFaceTrack v1.0', 'com.dario.FaceTrack')
        self.node = node
        self.range = nuke.String_Knob('range', 'Frame Range', '1-3')
        self.addKnob(self.range)

def get_stats(data):
    l_pts, r_pts = data['l_eye'], data['r_eye']
    lex = sum(p[0] for p in l_pts) / len(l_pts)
    ley = sum(p[1] for p in l_pts) / len(l_pts)
    rex = sum(p[0] for p in r_pts) / len(r_pts)
    rey = sum(p[1] for p in r_pts) / len(r_pts)
    
    avg_x, avg_y = (lex + rex) / 2.0, (ley + rey) / 2.0
    dx, dy = rex - lex, rey - ley
    dist = math.sqrt(dx**2 + dy**2)
    angle = math.degrees(math.atan2(dy, dx))
    return avg_x, avg_y, dist, angle

def create_all_tools(face_session, node):
    if not face_session:
        nuke.message("No face data found.")
        return
    
    sorted_frames = sorted(face_session.keys())
    start_f = sorted_frames[0]
    
    roto = nuke.nodes.Roto(name="Face_Mesh_Track")
    trans = nuke.nodes.Transform(name="Face_Matchmove")
    roto.setXYpos(node.xpos() + 100, node.ypos() + 80)
    trans.setXYpos(node.xpos() + 220, node.ypos() + 80)

    curves = roto['curves']
    root = curves.rootLayer
    shape_map = {}

    for group_name, pts in face_session[start_f].items():
        shape = rp.Shape(curves)
        shape.name = group_name
        root.append(shape)
        
        ctrl_pts = []
        for p in pts:
            cp = rp.ShapeControlPoint()
            # FIX: Must pass a single tuple/list, not two arguments
            cp.center.setPosition((p[0], p[1])) 
            shape.append(cp)
            ctrl_pts.append(cp)
        shape_map[group_name] = ctrl_pts

    for k in ['translate', 'rotate', 'scale', 'center']: 
        trans[k].setAnimated()
        
    rx, ry, rd, ra = get_stats(face_session[start_f])

    for f in sorted_frames:
        data = face_session[f]
        cx, cy, cd, ca = get_stats(data)

        # Update Roto
        for group_name, pts in data.items():
            if group_name in shape_map:
                for i, p in enumerate(pts):
                    # Using addPositionKey for animation
                    shape_map[group_name][i].center.addPositionKey(f, (p[0], p[1]))

        # Update SRT
        trans['translate'].setValueAt(cx - rx, f, 0)
        trans['translate'].setValueAt(cy - ry, f, 1)
        trans['rotate'].setValueAt(ca - ra, f)
        trans['scale'].setValueAt(cd / rd, f)
        trans['center'].setValueAt(rx, f, 0)
        trans['center'].setValueAt(ry, f, 1)

    curves.changed()