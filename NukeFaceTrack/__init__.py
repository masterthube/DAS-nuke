import nuke
import importlib
import sys

def run_tool():
    # Only reload if it actually exists in memory
    if 'NukeFaceTrack.ui' in sys.modules:
        importlib.reload(sys.modules['NukeFaceTrack.ui'])
    if 'NukeFaceTrack.core' in sys.modules:
        importlib.reload(sys.modules['NukeFaceTrack.core'])

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
        fr_val = p.range.value()
        first = int(fr_val.split('-')[0])
        last = int(fr_val.split('-')[1])
        
        session = processor.run_range(target_node, first, last)
        if session:
            ui.create_all_tools(session, target_node, p.smooth.value())