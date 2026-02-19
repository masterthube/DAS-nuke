import nuke
import os

# def createReadFromWrite():
#     sel = nuke.selectedNode()
#     if sel.Class() == "Write":
#         file = sel['file'].value()
#         if file:
#             # resolve path (handles relative paths / TCL)
#             path = nuke.filename(sel)
#             if os.path.exists(os.path.dirname(path)):
#                 readNode = nuke.createNode("Read", "file {%s}" % path)
#                 readNode['first'].setValue(int(nuke.Root()['first_frame'].value()))
#                 readNode['last'].setValue(int(nuke.Root()['last_frame'].value()))
#                 readNode['origfirst'].setValue(int(nuke.Root()['first_frame'].value()))
#                 readNode['origlast'].setValue(int(nuke.Root()['last_frame'].value()))
#                 nuke.message("Read created from Write:\n%s" % path)
#             else:
#                 nuke.message("⚠️ Path doesn’t exist:\n%s" % path)
#     else:
#         nuke.message("Select a Write node first!")


