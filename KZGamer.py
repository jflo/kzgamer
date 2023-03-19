import cv2
import sys
import time
from picamera2 import Picamera2, Preview
from dice import get_blobs, get_dice_from_blobs, simplify_dice
from vid_markup import overlay_info
from entropy import Entropy
from trapdoor import TrapDoor
from preprocess import preprocess
import subprocess
from PyQt5.QtWidgets import QApplication
from PyQt5 import QtCore
from MainWindow import MainWindow

picam2 = Picamera2()
picam2.preview_configuration.main.size = (800, 480)
picam2.preview_configuration.main.format = "RGB888"
picam2.preview_configuration.align()
picam2.configure("preview")
picam2.set_controls({"AnalogueGain" : 16.0, "Contrast": 1.0})
time.sleep(2)
picam2.start()

entropy = Entropy()
trap_door = TrapDoor()
trap_door.re_home()

loop_state = "waiting"
settle_frames = 10
seen_since = 0
current_dice = 0

app = QApplication(sys.argv)
ui = MainWindow()
ui.setWindowState(QtCore.Qt.WindowMaximized)
ui.show()

while True:
    frame = picam2.capture_array()
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
      trap_door.spring_and_reset()
      seen_since = 0
    else:
        loop_state = "watching"

    overlay_info(processed, dice, blobs, loop_state)
    cv2.imshow('frame', processed)
    current_dice = simple_dice
    num_hits = len([num for num in current_dice if num >= ui.hitting_on])
    num_sixes = len([ num for num in current_dice if num == 6])
    num_bits_collected = entropy.bits_collected()
    ui.log_roll(num_hits, len(current_dice), num_sixes, num_bits_collected)
    if entropy.entropy_full():
        hex = entropy.to_hex_string()
        subprocess.run(["ls -l"], capture_output=True)
        subprocess.run(["kzgcli offline contribute ceremony-state.json kzgamer-contribution.json --entropy-hex {hex}"],capture_output=True)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        sys.exit(app.exec_())
        break

