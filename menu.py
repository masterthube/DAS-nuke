import os
import nuke
from pathlib import Path
import comfyui2nuke as comfyui
import NukeFaceTrack as NFT


##############################################################################
####################-------------DEFAULTS-------------########################
##############################################################################

comfyui.setup()

# Framehold on current frame
def frameHoldCB():
    n = nuke.thisNode()
    n["first_frame"].setValue(nuke.frame())


nuke.addOnUserCreate(frameHoldCB, nodeClass="FrameHold")
nuke.addOnUserCreate(
    lambda: nuke.thisNode()["reference_frame"].setValue(nuke.frame()),
    nodeClass="Tracker4",
)   

##############################################################################
####################-------------SHORTCUTS-------------#######################
##############################################################################


def premultMerge():
    nuke.createNode("Copy")
    premult = nuke.createNode("Premult")
    yPos = premult.ypos()
    premult.setYpos(yPos + 20)
    merge = nuke.createNode("Merge")
    xpos = merge.xpos()
    merge.setXpos(xpos + 60)


def channelMerge():
    nuke.createNode("ChannelMerge")


def cryptomatteShortcut():
    nuke.createNode("Cryptomatte")


def close():
    for node in nuke.allNodes():
        node.hideControlPanel()


def disconnectViewers():
    nuke.selectAll()
    nuke.invertSelection()

    for n in nuke.allNodes():
        if n.Class() == "Viewer":
            n["selected"].setValue(True)

    nuke.extractSelected()


def RotoBlur_Shortcut():
    y_offset = 60
    r = nuke.createNode("Roto", "output alpha")
    r["cliptype"].setValue("no clip")
    y = int(r.ypos() + y_offset)
    b = nuke.nodes.Blur()
    b["size"].setValue(2)
    b["channels"].setValue("alpha")
    b["label"].setValue("Size: [value size]")
    b["xpos"].setValue(r.xpos())
    b["ypos"].setValue(y)
    b.setInput(0, r)
    b.hideControlPanel()


def SharpenSandwhich():
    y_offset = 60
    Lo1 = nuke.createNode("Log2Lin")
    Lo1["operation"].setValue("lin2log")
    Lo1.hideControlPanel()
    ySh = int(Lo1.ypos() + y_offset)
    yLo = int(Lo1.ypos() + (90 + y_offset))
    Sh = nuke.nodes.Sharpen()
    Sh["size"].setValue(3)
    Sh["label"].setValue("Size: [value size]")
    Sh["xpos"].setValue(Lo1.xpos())
    Sh["ypos"].setValue(ySh)
    Sh.setInput(0, Lo1)
    Lo2 = nuke.nodes.Log2Lin()
    Lo2["operation"].setValue("log2lin")
    Lo2["xpos"].setValue(Lo1.xpos())
    Lo2["ypos"].setValue(yLo)
    Lo2.setInput(0, Sh)
    Lo2.hideControlPanel()
    Sh.showControlPanel()


def createReadFromWrite():
    sel = nuke.selectedNode()
    if sel.Class() == "Write":
        file = sel['file'].value()
        if file:
            # resolve path (handles relative paths / TCL)
            path = nuke.filename(sel)
            if os.path.exists(os.path.dirname(path)):
                readNode = nuke.createNode("Read", "file {%s}" % path)
                readNode['first'].setValue(int(nuke.Root()['first_frame'].value()))
                readNode['last'].setValue(int(nuke.Root()['last_frame'].value()))
                readNode['origfirst'].setValue(int(nuke.Root()['first_frame'].value()))
                readNode['origlast'].setValue(int(nuke.Root()['last_frame'].value()))
                readNode["xpos"].setValue(sel.xpos())
                readNode["ypos"].setValue(int(sel.ypos()+150))
                readNode["colorspace"].setValue("rec709")
                # readNode["name"].setValue("Render")
                # nuke.selectNode
                #nuke.message("Read created from Write:\n%s" % path)
            else:
                nuke.message("⚠️ Path doesn’t exist:\n%s" % path)
    else:
        nuke.message("Select a Write node first!")


def placeDot90(tolerance=2):
    sel = nuke.selectedNodes()
    if len(sel) != 1:
        return

    node = sel[0]

    node_cx = node.xpos() + node.screenWidth() / 2
    node_cy = node.ypos() + node.screenHeight() / 2

    for i in range(node.inputs()):
        inp = node.input(i)
        if not inp:
            continue

        inp_cx = inp.xpos() + inp.screenWidth() / 2

        # if input is vertically aligned → skip
        if abs(inp_cx - node_cx) <= tolerance:
            continue

        # insert Dot on this input
        dot = nuke.nodes.Dot()
        dot.setInput(0, inp)
        node.setInput(i, dot)

        # orthogonal placement
        dot_x = inp_cx
        dot_y = node_cy

        dot.setXYpos(
            int(dot_x - dot.screenWidth() / 2),
            int(dot_y - dot.screenHeight() / 2)
        )


def paste_for_all():

    all_selected = nuke.selectedNodes()
    if not all_selected:
        return

    paste_file = nukescripts.cut_paste_file()

    for node in all_selected:

        dependents = node.dependent(nuke.INPUTS)

        # deselect everything
        for n in nuke.allNodes():
            n.setSelected(False)

        node.setSelected(True)

        # paste nodes
        nuke.nodePaste(paste_file)

        pasted_nodes = nuke.selectedNodes()

        if not pasted_nodes:
            continue

        # find top & bottom of pasted chain
        top = min(pasted_nodes, key=lambda n: n.ypos())
        bottom = max(pasted_nodes, key=lambda n: n.ypos())

        # connect top to current node
        top.setInput(0, node)

        if dependents:
            # reconnect dependents to bottom
            for dep in dependents:
                for i in range(dep.inputs()):
                    if dep.input(i) == node:
                        dep.setInput(i, bottom)
        else:
            # no dependents → paste continues the chain
            pass


def createBackdropFromSelection():

    sel = nuke.selectedNodes()
    if not sel:
        return

    # -----------------------------
    # Color presets (RGBA ints)
    # -----------------------------
    COLOR_PRESETS = {
        "Gray":  int("0x808080ff", 16),
        "Red":   int("0xef4444ff", 16),
        "Green": int("0x22c55eff", 16),
        "Blue":  int("0x3b82f6ff", 16),
        "Black": int("0x000000ff", 16),
        "White": int("0xffffffff", 16),
    }

    # -----------------------------
    # Panel
    # -----------------------------
    panel = nuke.Panel("Create Backdrop")
    panel.addSingleLineInput("Label", "")
    panel.addEnumerationPulldown(
        "Color presets",
        " ".join(COLOR_PRESETS.keys())
    )
    # panel.addBooleanCheckBox('Custom color?', False)    
    # panel.addRGBColorChip('Color custom', '2576980479')

    if not panel.show():
        return

    label = panel.value("Label")
    color_name = panel.value("Color")
    tile_color = COLOR_PRESETS.get(color_name, COLOR_PRESETS["Gray"])

    # -----------------------------
    # Bounding box + padding
    # -----------------------------
    padding = 100

    min_x = min(n.xpos() for n in sel)
    min_y = min(n.ypos() for n in sel)
    max_x = max(n.xpos() + n.screenWidth() for n in sel)
    max_y = max(n.ypos() + n.screenHeight() for n in sel)

    bd_x = min_x - padding
    bd_y = min_y - padding
    bd_w = (max_x - min_x) + padding * 2
    bd_h = (max_y - min_y) + padding * 2

    # -----------------------------
    # Z-order logic (nested safe)
    # -----------------------------
    z_order = 0
    for n in sel:
        if n.Class() == "BackdropNode":
            z_order = min(z_order, int(n["z_order"].value()) - 1)

    # -----------------------------
    # Create backdrop
    # -----------------------------
    bd = nuke.nodes.BackdropNode(
        xpos=bd_x,
        ypos=bd_y,
        bdwidth=bd_w,
        bdheight=bd_h,
        tile_color=tile_color,
        label="<center>"+label
    )

    # Appearance + typography
    bd["appearance"].setValue("Border")
    bd["note_font"].setValue("Impact")
    bd["note_font_size"].setValue(50)
    bd["z_order"].setValue(z_order)


nuke.addOnScriptLoad(disconnectViewers)
nukebar = nuke.menu('Nuke')
utilitiesMenu = nukebar.addMenu('DAS_nuke', icon = "logo.jpg")
# nuke.menu('Nodes').addMenu('Draw').addCommand('Create Roto and Blur node.', 'RotoBlur_Shortcut()', shortcut='o', icon='Roto.png')
# nuke.menu('Nodes').addMenu('Filter').addCommand('SharpenSandwhich', 'SharpenSandwhich()', shortcut='ctrl+l', icon='Sharpen.png', index=26) 
#utilitiesMenu.addCommand("Shortcuts/RotoBlur", "RotoBlur_Shortcut()", "o")
utilitiesMenu.addCommand("Shortcuts/Create Read from Write", "createReadFromWrite()", "shift+r")
utilitiesMenu.addCommand("Shortcuts/Close property panels", "close()", "shift+d")
utilitiesMenu.addCommand("Shortcuts/ChannelMerge", "channelMerge()", "shift+c")
utilitiesMenu.addCommand("Shortcuts/SharpenSandwich", "SharpenSandwhich()", "ctrl+l")
utilitiesMenu.addCommand("Shortcuts/Premult Merge", "premultMerge()", "ctrl+shift+1")
utilitiesMenu.addCommand("Shortcuts/Cryptomatte", "cryptomatteShortcut()", "ctrl+shift+2")
utilitiesMenu.addCommand("Shortcuts/Paste for all", paste_for_all, 'Shift+Ctrl+V')
utilitiesMenu.addCommand("Shortcuts/Create Backdrop from Selection", createBackdropFromSelection, "Alt+b")
utilitiesMenu.addCommand("Shortcuts/Dots90", placeDot90, ",")
utilitiesMenu.addCommand("NukeFaceTrack", NFT.run_tool, "shift+f")