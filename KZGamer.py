import cv2
import time
from picamera2 import Picamera2, Preview
from libcamera import controls
from dice import get_blobs, get_dice_from_blobs, simplify_dice
from vid_markup import overlay_info
from entropy import Entropy
from trapdoor import TrapDoor
from gpiozero import LED
from preprocess import preprocess
import subprocess

picam2 = Picamera2()
picam2.preview_configuration.main.size = (800, 480)
picam2.preview_configuration.main.format = "RGB888"
picam2.preview_configuration.align()
picam2.configure("preview")
picam2.set_controls({"AnalogueGain" : 16.0, "Contrast": 1.0})
time.sleep(2)
picam2.start()

entropy = Entropy()
trapDoor = TrapDoor()
trapDoor.reHome()

loopState = "waiting"
settleFrames = 10
seenSince = 0
currentDice = 0

while not entropy.entropy_full():
    frame = picam2.capture_array()
    # check for dice
    processed = preprocess(frame)
    blobs = get_blobs(processed)
    dice = get_dice_from_blobs(blobs)
    simple_dice = simplify_dice(dice)

    # are these the same dice from the last N frames?
    if currentDice == simple_dice and len(simple_dice) > 0:
      seenSince+=1
      loopState = "dice stabilizing"
    if seenSince > settleFrames:
      # parse dice and append to entropy
      loopState = "dice stable"
      entropy.entropy_add(simple_dice)
      # open trapDoor for 2 sec, close it back up
      trapDoor.springAndReset()
      seenSince = 0
    else:
        loopState = "watching"

    out_frame = overlay_info(processed, dice, blobs, loopState)
    cv2.imshow('frame', processed)
    currentDice = simple_dice
    if entropy.entropy_full():
        hex = entropy.runningEntropy.toHexString()
        subprocess.run(["ls -l"], capture_output=True)
        subprocess.run(["kzgcli offline contribute ceremony-state.json kzgamer-contribution.json --entropy-hex {hex}"],capture_output=True)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
