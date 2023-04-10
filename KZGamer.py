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
from entropy import Entropy

if picam_available:
    from trapdoor import TrapDoor
from preprocess import preprocess
import subprocess


class KZGamerThread(QThread):
    ui_update = pyqtSignal(object)
    new_roll = pyqtSignal(object)
    log = pyqtSignal(object)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.running = False
        if picam_available:
            self.camera = Picamera2()
            self.capture_config = self.camera.create_still_configuration(main={"size": (2304,1296)})
            self.camera.configure(self.capture_config)
            focal_length = 1/.231
            self.camera.set_controls({"AfMode": controls.AfModeEnum.Manual,
                                      "LensPosition": focal_length,
                                      "AeEnable": False,
                                      "ExposureTime": int((1000000)*1/15),
                                      "ExposureValue": -2,
                                      "Contrast": 8 })
            self.camera.start()
            time.sleep(1)
            # if picam is available, we're on the pi and io is available
            self.trap_door = TrapDoor()
        else:
            self.camera = cv2.VideoCapture(0)

        self.entropy_goal = 128
        self.entropy = Entropy(self.entropy_goal)
        self.settle_frames = 2
        self.hitting_on = 4
        self.mode = "Morale"
        self.frame_capture_delay = 0.1

    @pyqtSlot(object)
    def target_selected(self, target_number):
        self.hitting_on = target_number

    @pyqtSlot(object)
    def mode_selected(self, mode_name):
        self.mode = mode_name

    def run(self):
        self.status_check()
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
            processed = preprocess(frame)
            blobs = get_blobs(processed)
            dice = get_dice_from_blobs(blobs)
            
            stabilizing_dice = simplify_dice(dice)
            # are these the same dice from the last N frames?
            if stabilizing_dice == last_stable_dice and len(stabilizing_dice) > 0:
                consistent_frames += 1
                if consistent_frames >= self.settle_frames:
                # parse dice and append to entropy
                    for num in last_stable_dice:
                        if num > 6:
                            self.log.emit("error detected, dice ignored, reroll")
                    self.entropy.entropy_add(last_stable_dice)
                    num_hits = len([num for num in last_stable_dice if num >= self.hitting_on])
                    num_sixes = len([num for num in last_stable_dice if num == 6])
                    if self.mode == "Hit/Damage":
                        roll_result = f"{num_hits} hits({self.hitting_on}) on {len(last_stable_dice)} dice, {num_sixes} exploded"
                    elif self.mode == "Morale":
                        total_value = sum(last_stable_dice)
                        if total_value == 11:
                            roll_result = "Morale check failed"
                        elif total_value == 12:
                            roll_result = "FUBAR, roll D6 chart pg. 41"
                        elif total_value <= self.hitting_on:
                            roll_result = "Morale check succeeded"
                        else:
                            roll_result = "Morale check failed"
                    num_bits_collected = self.entropy.bits_collected()
                    bits_message = f"{num_bits_collected}" \
                                   f" total bits of entropy collected"
                    self.log.emit(bits_message)
                    self.new_roll.emit(roll_result)

                    if picam_available:
                        self.trap_door.spring_and_reset()
                        seen_since = 0
                        last_stable_dice = []
                        stabilizing_dice = []
            else:
                loop_state = "watching"
                last_stable_dice = stabilizing_dice


            if self.entropy.entropy_full():
                hex = self.entropy.to_hex_string()
                subprocess.run(["ls", "-l"], capture_output=True)
                victory_message = "DANKSHARD BE PRAISED THE KZGENING IS UPON US"
                self.new_roll.emit(victory_message)
                command = ["/usr/local/bin/kzgcli", "offline", "contribute", "/media/jflo/KOBRA/ceremony-state.json", "/media/jflo/KOBRA/kzgamer-contribution.json", f"--entropy-hex {hex}"]
                contrib_result = subprocess.run([command], capture_output=True)
                self.log.emit(contrib_result.stdout.decode())
                self.log.emit(contrib_result.stderr.decode())
                print(contrib_result.stdout.decode())
                print(contrib_result.stderr.decode())

    def status_check(self):
        git_command = ["git", "log", "--pretty=format:'%h %ad %s'", "-1"]
        git_log = subprocess.run(git_command, capture_output=True)
        self.log.emit(git_log.stdout.decode())
        self.log.emit(git_log.stderr.decode())
        state_check_command = ["ls", "-lh", "/media/jflo/KOBRA/ceremony-state.json"]
        state_check_result = subprocess.run(state_check_command, capture_output=True)
        self.log.emit(state_check_result.stdout.decode())
        self.log.emit(state_check_result.stderr.decode())
        self.log.emit(f"attempting to collect {self.entropy_goal} bits of entropy")

    def stop(self):
        self.running = False
