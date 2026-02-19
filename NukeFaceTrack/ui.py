import nuke
import nuke.rotopaint as rp

def create_all_tools(face_session, node):
    if not face_session:
        return

    # 1. SETUP DIMENSIONS & RANGE
    w, h = node.width(), node.height()
    sorted_frames = sorted(face_session.keys())
    start_f, end_f = sorted_frames[0], sorted_frames[-1]

    # Set Viewer Range
    nuke.Root()['first_frame'].setValue(start_f)
    nuke.Root()['last_frame'].setValue(end_f)
    for v in nuke.allNodes("Viewer"):
        v['frame_range'].setValue(f"{int(start_f)}-{int(end_f)}")
        v['frame_range_lock'].setValue(True)

    # 2. CREATE NODES
    cp = nuke.nodes.CornerPin2D(name="Face_Matchmove_MP")
    trans = nuke.nodes.Transform(name="Face_Stabilize_MP")
    roto = nuke.nodes.Roto(name="Face_Points_MP")
    
    # Position nodes
    cp.setXYpos(node.xpos(), node.ypos() + 100)
    trans.setXYpos(cp.xpos() + 150, cp.ypos())
    roto.setXYpos(trans.xpos() + 150, trans.ypos())

    # 3. CALCULATE REFERENCE (First Frame)
    ref_data = face_session[start_f]
    ref_x_list = [pos[0] for pos in ref_data.values()]
    ref_y_list = [pos[1] for pos in ref_data.values()]
    ref_avg_x = sum(ref_x_list) / len(ref_x_list)
    ref_avg_y = sum(ref_y_list) / len(ref_y_list)

    # 4. FIX CORNERPIN STRETCHING (Set 'from' to frame boundaries)
    # This makes the CP act as a tracker/matchmove rather than a face-crusher
    cp['from1'].setValue(0, 0); cp['from1'].setValue(0, 1)        # Bottom Left
    cp['from2'].setValue(w, 0); cp['from2'].setValue(0, 1)        # Bottom Right
    cp['from3'].setValue(w, 0); cp['from3'].setValue(h, 1)        # Top Right
    cp['from4'].setValue(0, 0); cp['from4'].setValue(h, 1)        # Top Left
    
    # Initialize 'to' animation
    for k in ["to1", "to2", "to3", "to4"]:
        cp[k].setAnimated()
    trans['translate'].setAnimated()

    # 5. PREPARE ROTO SHAPES
    curves = roto['curves']
    root = curves.rootLayer
    shape_map = {}
    for name in ref_data.keys():
        shape = rp.Shape(curves)
        shape.name = name
        shape.append(rp.ShapeControlPoint(nuke.math.Vector2(0, 0)))
        root.append(shape)
        shape_map[name] = shape

    # 6. THE ANIMATION LOOP
    for f in sorted_frames:
        data = face_session[f]
        current_x_list = [pos[0] for pos in data.values()]
        current_y_list = [pos[1] for pos in data.values()]
        curr_avg_x = sum(current_x_list) / len(current_x_list)
        curr_avg_y = sum(current_y_list) / len(current_y_list)

        # A. TRANSFORM: Relative translation (Current - Reference)
        # This keeps the image centered!
        trans['translate'].setValueAt(float(curr_avg_x - ref_avg_x), f, 0)
        trans['translate'].setValueAt(float(curr_avg_y - ref_avg_y), f, 1)
        trans['center'].setValue(ref_avg_x, 0)
        trans['center'].setValue(ref_avg_y, 1)

        # B. CORNERPIN: Offset the corners by the face movement
        # (This is a simplified planar track approach)
        dx = curr_avg_x - ref_avg_x
        dy = curr_avg_y - ref_avg_y
        cp['to1'].setValueAt(0 + dx, f, 0); cp['to1'].setValueAt(0 + dy, f, 1)
        cp['to2'].setValueAt(w + dx, f, 0); cp['to2'].setValueAt(0 + dy, f, 1)
        cp['to3'].setValueAt(w + dx, f, 0); cp['to3'].setValueAt(h + dy, f, 1)
        cp['to4'].setValueAt(0 + dx, f, 0); cp['to4'].setValueAt(h + dy, f, 1)

        # C. ROTO: Animate all shapes
        for name, pos in data.items():
            if name in shape_map:
                sh_trans = shape_map[name].getTransform()
                sh_trans.getTranslationAnimCurve(0).addKey(f, float(pos[0]))
                sh_trans.getTranslationAnimCurve(1).addKey(f, float(pos[1]))

    print(f"Done! Range: {start_f}-{end_f}")