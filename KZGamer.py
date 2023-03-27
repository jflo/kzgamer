import cv2
import os

import sys
import time
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot

try:
    from picamera2 import Picamera2, Preview
    picam_available = True
    from libcamera import controls
except:
    picam_available = False
    print("exception during picam setup")

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
            self.capture_config = self.camera.create_still_configuration() 
            self.camera.configure(self.capture_config)
            focal_length = 1/.182
            self.camera.set_controls({"AfMode": controls.AfModeEnum.Manual,
                                      "LensPosition": focal_length,
                                      "AeConstraintMode": controls.AeConstraintModeEnum.Highlight,
                                      "AeMeteringMode": controls.AeMeteringModeEnum.Spot,
                                      "ExposureValue": -1,
                                      "Contrast": 8 })
            self.camera.start()
            time.sleep(1)
            # if picam is available, we're on the pi and io is available
            self.trap_door = TrapDoor()
        else:
            self.camera = cv2.VideoCapture(0)

        self.entropy = Entropy()
        self.settle_frames = 2
        self.hitting_on = 4
        self.vid_display = VideoFrameProvider()
        self.frame_capture_delay = 0.1

    @pyqtSlot(object)
    def target_selected(self, target_number):
        self.hitting_on = target_number

    def run(self):
        loop_state = "waiting"
        self.running = True
        consistent_frames = 1
        stabilizing_dice = []
        last_stable_dice = []
        while self.running:
            time.sleep(self.frame_capture_delay)
            if picam_available:
                frame = self.camera.capture_array()
            else:
                ret, frame = self.camera.read()
            # check for dice
            #self.vid_display.show_frame(frame)
            #time.sleep(1)
            processed = preprocess(frame)
            #self.vid_display.show_frame(processed)
            #time.sleep(1)
            blobs = get_blobs(processed)
            dice = get_dice_from_blobs(blobs)
            
            stabilizing_dice = simplify_dice(dice)
            #self.vid_display.overlay_info(processed, dice, blobs, loop_state)
            if len(blobs) > 0 :
                print(f"found {len(blobs)} blobs which seems like {len(dice)} dice")
                print(stabilizing_dice)
                print(last_stable_dice)
            # are these the same dice from the last N frames?
            if stabilizing_dice == last_stable_dice and len(stabilizing_dice) > 0:
                consistent_frames += 1
                loop_state = "dice stabilizing"
                self.vid_display.overlay_info(processed, dice, blobs, loop_state)
                if consistent_frames >= self.settle_frames:
                # parse dice and append to entropy
                    loop_state = "dice stable"
                    self.vid_display.overlay_info(processed, dice, blobs, loop_state)
                    self.entropy.entropy_add(last_stable_dice)
                    num_hits = len([num for num in last_stable_dice if num >= self.hitting_on])
                    num_sixes = len([num for num in last_stable_dice if num == 6])
                    num_bits_collected = self.entropy.bits_collected()
                    roll_message = f"{num_hits} hits({self.hitting_on}) on {len(last_stable_dice)} dice, {num_sixes} exploded - {num_bits_collected}" \
                               f" total bits of entropy collected"
                    self.new_roll.emit(roll_message)
                    if picam_available:
                        self.trap_door.spring_and_reset()
                        seen_since = 0
                        last_stable_dice = []
                        stabilizing_dice = []
            else:
                loop_state = "watching"
                last_stable_dice = stabilizing_dice

            #self.vid_display.overlay_info(processed, dice, blobs, loop_state)

            if self.entropy.entropy_full():
                hex = self.entropy.to_hex_string()
                subprocess.run(["ls -l"], capture_output=True)
                print(f"DANKSHARD BE PRAISED THE KZGENING IS UPON US")
                command = f"kzgcli offline contribute ceremony-state.json kzgamer-contribution.json --entropy-hex {hex}"
                subprocess.run([command], capture_output=True)

    def stop(self):
        self.running = False
