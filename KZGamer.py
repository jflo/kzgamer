import cv2
# from picamera2 import Picamera2, Preview
from dice import get_blobs, get_dice_from_blobs
from vid_markup import overlay_info
from entropy import Entropy

desktop = True

if desktop:
    cap = cv2.VideoCapture(0)
else:
    # picam2 = Picamera2()
    picam2 = {};
    picam2.preview_configuration.main.size = (1280, 720)
    picam2.preview_configuration.main.format = "RGB888"
    picam2.preview_configuration.align()
    picam2.configure("preview")
    picam2.start()

entropy = Entropy()
loopState = "waiting"
seenSince = 0
currentDice = 0
while not entropy.entropy_full():
    if desktop:
        ret, frame = cap.read()
        cv2.imshow('frame', frame)
    else:
        ret, frame = picam2.capture_array()

    # check for dice
    blobs = get_blobs(frame)
    dice = get_dice_from_blobs(blobs)

    # are these the same dice from the last N frames?
    if currentDice == dice:
      seenSince+=1
      loopState = "dice stabilizing"
    if seenSince > 20:
      # parse dice and append to entropy
      loopState = "dice stable"
      entropy.entropy_add(dice)
      # open trapdoor for 2 sec, close it back up
      seenSince = 0
    else:
        loopState = "watching"

    out_frame = overlay_info(frame, dice, blobs, loopState)
    cv2.imshow('frame', frame)
    currentDice = dice
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
# call java client with contribution file
