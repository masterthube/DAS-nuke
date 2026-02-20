import nuke

def run_tool():
    # We import INSIDE the function. 
    # This is "Lazy Loading" - it only happens when you click the button.
    from . import ui
    from . import core
    
    try:
        target_node = nuke.selectedNode()
    except ValueError:
        nuke.message("Select a node first.")
        return

    p = ui.FaceTrackUI(target_node)
    if p.showModalDialog():
        processor = core.FaceProcessor()
        fr = nuke.FrameRange(p.range.value())
        smooth_val = p.smooth.value()
        
        session = processor.run_range(target_node, fr.first(), fr.last())
        if session:
            ui.create_all_tools(session, target_node, smooth_val)