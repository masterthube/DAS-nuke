##############################################################################
####################-------------DEFAULTS LABELS------########################
##############################################################################
import nuke

def nuke_default():

    # image
    nuke.knobDefault(
        "Read.label",
        "Fr. range: [value first] - [value last]\nRes: [value width] * [value height]\nColorspace: [value colorspace]",
    )
    nuke.knobDefault("Write.label", "Channels: [string toupper [value channel]]")
    nuke.knobDefault("Constant.label", "Res: [value width] * [value height]")
    nuke.knobDefault("CheckerBoard2.label", "Res: [value width] * [value height]")

    # draw

    # time
    nuke.knobDefault("TimeOffset.label", "Value: [value time_offset]")
    nuke.knobDefault("Retime.label", "Out: [value output.first] - [value output.last]")

    # channel
    nuke.knobDefault("Shuffle.label", "[string toupper [value in1]]")
    nuke.knobDefault("ShuffleCopy.label", "[string toupper [value in1]]")
    nuke.knobDefault("Remove.label", "[string toupper [value channels]]")

    # color
    nuke.knobDefault("Colorspace.label", "[value colorspace_in] to [value colorspace_out]")
    nuke.knobDefault(
        "OCIOColorSpace.label", "[value in_colorspace] to [value out_colorspace]"
    )
    nuke.knobDefault("Saturation.label", "Value: [value saturation]")
    nuke.knobDefault("Multiply.label", "Value: [value value]")

    # filter
    nuke.knobDefault("Blur.label", "Size: [value size]")
    nuke.knobDefault("Defocus.label", "Size: [value defocus]")
    nuke.knobDefault("ZDefocus2.label", "Size: [value size]")
    nuke.knobDefault("EdgeBlur.label", "Size: [value size]")
    nuke.knobDefault("Sharpen.label", "Size: [value size]")
    nuke.knobDefault("Soften.label", "Size: [value size]")

    # keyer

    # merge
    nuke.knobDefault("Switch.label", "Which: [value which]")
    nuke.knobDefault("Dissolve.label", "Which: [value which]")
    nuke.knobDefault("Merge.label", "Bbox: [value bbox]")

    # transform
    nuke.knobDefault(
        "Crop.label",
        "Box: x:[value box.x]  y:[value box.y] r:[value box.r] t:[value box.t]",
    )
    nuke.knobDefault("IDistort.label", "Scale: [value uv_scale]")
    nuke.knobDefault("SplineWarp3.label", "Out: [string toupper [value output_enum]]")
    nuke.knobDefault("STMap.label", "UV: [value uv]")
    nuke.knobDefault("VectorDistort.label", "[value referenceFrame]")
    nuke.knobDefault("Transform.shutteroffset", "centred")

    # 3D
    nuke.knobDefault("Camera2.label", "File: [file tail [value file]]")
    nuke.knobDefault(
        "ReadGeo2.label",
        "File: [file tail [value file]]\n[string toupper [value display]]\nRender: [string toupper [value render_mode]]",
    )
    nuke.knobDefault(
        "Card2.label",
        "Display: [string toupper [value display]]\nRender: [string toupper [value render_mode]]",
    )
    nuke.knobDefault(
        "Cube.label",
        "Display: [string toupper [value display]]\nRender: [string toupper [value render_mode]]",
    )
    nuke.knobDefault(
        "Cylinder.label",
        "Display: [string toupper [value display]]\nRender: [string toupper [value render_mode]]",
    )
    nuke.knobDefault(
        "Sphere.label",
        "Display: [string toupper [value display]]\nRender: [string toupper [value render_mode]]",
    )
    nuke.knobDefault(
        "Scene.label",
        "Display: [string toupper [value display]]\nRender: [string toupper [value render_mode]]",
    )

    # other
    nuke.knobDefault(
        "nuke_dispatch.label",
        """Range: [value framestart] - [value frameend]\nBatch: [value batch]\nLic. Rem.: [if {[value removelicense]==true} {return "On"} {return "Off"}]""",
    )

    ##############################################################################
    ####################-------------DEFAULTS VALUES-------#######################
    ##############################################################################

    # image

    nuke.knobDefault("Read.on_error", "checkerboard")

    # draw
    nuke.knobDefault("Text2.xjustify", "center")
    nuke.knobDefault("Text2.yjustify", "center")
    nuke.knobDefault("RotoPaint.cliptype", "no clip")

    # time
    nuke.knobDefault("Tracker4.label", "[value reference_frame]")

    # channel
    nuke.knobDefault("Remove.operation", "1")
    nuke.knobDefault("Remove.channels", "rgba")

    # color

    # filter
    nuke.knobDefault("Blur.size", "2")
    nuke.knobDefault("EdgeBlur.channels", "alpha")
    nuke.knobDefault("DirBlurWrapper.BlurTye", "linear")
    nuke.knobDefault("DirBlurWrapper.BlurLayer", "rgba")
    nuke.knobDefault("Dilate.channels", "alpha")
    nuke.knobDefault("Erode.channels", "alpha")
    nuke.knobDefault("FilterErode.channels", "alpha")

    # grade
    nuke.knobDefault("Invert.channels", "alpha")

    # keyer

    # merge
    nuke.knobDefault("Merge.bbox", "B")
    nuke.knobDefault("Merge.also_merge", "none")
    nuke.knobDefault("ContactSheet.roworder", "TopBottom")
    nuke.knobDefault("ContactSheet.width", "input.width*columns")
    nuke.knobDefault("ContactSheet.height", "input.height*rows")

    # transform

    # 3D
    nuke.knobDefault("Project3D.crop", "false")
    nuke.knobDefault("ScanlineRender.shutteroffset", "centred")
    nuke.knobDefault("ScanlineRender.motion_vectors_type", "0")
    nuke.knobDefault("ScanlineRender.ztest_enabled", "false")
    nuke.knobDefault("ScanlineRender.MB_channel", "none")
    nuke.knobDefault("Wireframe.operation", "see through")
    nuke.knobDefault("Wireframe.line_width", "1")

    # other
    nuke.knobDefault("nuke_dispatch.batch", "1")
    nuke.knobDefault("Dot.note_font_size", "50")
    nuke.knobDefault("BackdropNode.note_font_size", "50")
    nuke.knobDefault("BackdropNode.appearance", "Border")
    nuke.knobDefault("StickyNote.note_font_size", "22")