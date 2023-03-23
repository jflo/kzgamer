import cv2
import os

import sys
import time
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot

try :
    from picamera2 import Picamera2, Preview
    picam_available = True
    # avoids using the QT bundled with opencv
    os.environ.pop("QT_QPA_PLATFORM_PLUGIN_PATH")
    os.environ.update({"QT_QPA_PLATFORM_PLUGIN_PATH":"/usr/lib/aarch64-linux-gnu/qt5/plugins/xcbglintegrations/libqxcb-glx-integration.so"})

except:
    picam_available = False

from dice import get_blobs, get_dice_from_blobs, simplify_dice
from VideoFrameProvider import VideoFrameProvider
from entropy import Entropy
if picam_available:
    from trapdoor import TrapDoor
from preprocess import preprocess
import subprocess


class KZGamerThread(QThread):
    ui_update = pyqtSignal(object)
    new_roll = pyqtSignal(object)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.running = False
        if picam_available:
            self.camera = Picamera2()
            time.sleep(1)
            self.camera.start()
            #if picam is available, we're on the pi and io is available
            self.trap_door = TrapDoor()
            self.trap_door.re_home()
        else:
            self.camera = cv2.VideoCapture(0)


        self.entropy = Entropy()
        self.loop_state = "waiting"
        self.settle_frames = 10
        self.hitting_on = 4
        self.vid_display = VideoFrameProvider()

    @pyqtSlot(object)
    def target_selected(self, target_number):
        self.hitting_on = target_number

    def run(self):
        self.running = True
        seen_since = 0
        current_dice = 0
        simple_dice = []
        while self.running:
            if picam_available:
                frame = self.camera.capture_array()
            else:
                ret, frame = self.camera.read()
            # check for dice
            processed = preprocess(frame)
            blobs = get_blobs(processed)
            dice = get_dice_from_blobs(blobs)
            simple_dice = simplify_dice(dice)

            # are these the same dice from the last N frames?
            if current_dice == simple_dice and len(simple_dice) > 0:
                seen_since+=1
                loop_state = "dice stabilizing"
            if seen_since > self.settle_frames:
                # parse dice and append to entropy
                loop_state = "dice stable"
                self.entropy.entropy_add(simple_dice)
                current_dice = simple_dice
                num_hits = len([num for num in current_dice if num >= self.hitting_on])
                num_sixes = len([ num for num in current_dice if num == 6])
                num_bits_collected = self.entropy.bits_collected()
                roll_message = f"{num_hits} on {len(current_dice)} dice, {num_sixes} exploded - {num_bits_collected} total bits of entropy collected"
                self.new_roll.emit(roll_message)

                if picam_available:
                    self.trap_door.spring_and_reset()
                    seen_since = 0
            else:
                loop_state = "watching"

            self.vid_display.overlay_info(processed, dice, blobs, loop_state)

            if self.entropy.entropy_full():
                hex = self.entropy.to_hex_string()
                subprocess.run(["ls -l"], capture_output=True)
                subprocess.run(["kzgcli offline contribute ceremony-state.json kzgamer-contribution.json --entropy-hex {hex}"],capture_output=True)

    def stop(self):
        self.running = False