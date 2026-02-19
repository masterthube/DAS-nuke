import nuke
import nuke.rotopaint as rp

def create_face_roto(face_session):
    if not face_session:
        return

    # 1. Create Roto Node
    roto_node = nuke.createNode("Roto")
    roto_node['label'].setValue("MediaPipe_FaceRoto")
    
    # Get the Roto "Layer" structure
    roto_knob = roto_node['curves']
    root_layer = roto_knob.rootLayer
    
    sorted_frames = sorted(face_session.keys())
    first_frame = sorted_frames[0]
    landmark_names = list(face_session[first_frame].keys())

    # 2. Create a Point (Shape) for each landmark
    for name in landmark_names:
        # Create a tiny 10x10 circle (Shape)
        shape = rp.Shape(roto_knob)
        shape.name = name
        
        # Add it to the root layer
        root_layer.append(shape)
        
        # 3. Animate the shape's center
        # The 'center' of a shape is controlled by a Transform attribute
        trans = shape.getTransform()
        
        for frame in sorted_frames:
            if name in face_session[frame]:
                x, y = face_session[frame][name]
                
                # Set a keyframe for the translation (center)
                # trans.setTranslation(value, dimension, time)
                trans.getTranslationAnimCurve(0).addKey(frame, x)
                trans.getTranslationAnimCurve(1).addKey(frame, y)

    # Refresh UI
    roto_node.showControlPanel()
    print(f"Roto created with {len(landmark_names)} animated points.")
    return roto_node