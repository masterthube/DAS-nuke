import nuke
import sys
import os

nuke.pluginAddPath("NukeSurvivalToolkit")
nuke.pluginAddPath("pixelfudger3")
nuke.pluginAddPath("stamps")
nuke.pluginAddPath("DAS")
nuke.pluginAddPath("C:/Users/dario/AppData/Local/Packages/PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0/LocalCache/local-packages/Python313/site-packages")

try:
    import NukeFaceTrack.bridge as mp_bridge
    mp_bridge.init_bridge()
    print("NukeFaceTrack: Bridge Initialized")
except ImportError as e:
    nuke.tprint(f"NukeFaceTrack: Import Failed: {e}")

print(f"Welcome to hell, Dario")