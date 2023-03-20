import cv2
import os
# avoids using the QT bundled with opencv
import sys
import time
try :
    from picamera2 import Picamera2, Preview
    picam_available = True
    os.environ.pop("QT_QPA_PLATFORM_PLUGIN_PATH")
    os.environ.update({"QT_QPA_PLATFORM_PLUGIN_PATH":"/usr/lib/aarch64-linux-gnu/qt5/plugins/xcbglintegrations/libqxcb-glx-integration.so"})

except:
    picam_available = False

from dice import get_blobs, get_dice_from_blobs, simplify_dice
from vid_markup import overlay_info
from entropy import Entropy
if picam_available:
    from trapdoor import TrapDoor
from preprocess import preprocess
import subprocess
from PyQt5.QtWidgets import QApplication
from PyQt5 import QtCore
from MainWindow import MainWindow

if picam_available:
    camera = Picamera2()
    camera.preview_configuration.main.size = (800, 480)
    camera.preview_configuration.main.format = "RGB888"
    camera.preview_configuration.align()
    camera.configure("preview")
    camera.set_controls({"AnalogueGain" : 16.0, "Contrast": 1.0})
    time.sleep(1)
    camera.start()
else:
    camera = cv2.VideoCapture()


entropy = Entropy()
if picam_available:
    trap_door = TrapDoor()
    trap_door.re_home()

loop_state = "waiting"
settle_frames = 10
seen_since = 0
current_dice = 0

app = QApplication(sys.argv)
ui = MainWindow()
#ui.setWindowState(QtCore.Qt.WindowMaximized)
ui.show()
ui.setWindowTitle("KZGamer")
sys.exit(app.exec_())


while True:
    if picam_available:
        frame = camera.capture_array()
    else:
        ret, frame = camera.read()
    # check for dice
    processed = preprocess(frame)

    blobs = get_blobs(processed)
    dice = get_dice_from_blobs(blobs)
    simple_dice = simplify_dice(dice)

    # are these the same dice from the last N frames?
    if current_dice == simple_dice and len(simple_dice) > 0:
      seen_since+=1
      loop_state = "dice stabilizing"
    if seen_since > settle_frames:
      # parse dice and append to entropy
      loop_state = "dice stable"
      entropy.entropy_add(simple_dice)
      # open trapDoor for 2 sec, close it back up
      if picam_available:
        trap_door.spring_and_reset()
      seen_since = 0
    else:
        loop_state = "watching"

    overlay_info(processed, dice, blobs, loop_state)
    current_dice = simple_dice
    num_hits = len([num for num in current_dice if num >= ui.hitting_on])
    num_sixes = len([ num for num in current_dice if num == 6])
    num_bits_collected = entropy.bits_collected()
    ui.log_roll(num_hits, len(current_dice), num_sixes, num_bits_collected)
    if entropy.entropy_full():
        hex = entropy.to_hex_string()
        subprocess.run(["ls -l"], capture_output=True)
        subprocess.run(["kzgcli offline contribute ceremony-state.json kzgamer-contribution.json --entropy-hex {hex}"],capture_output=True)