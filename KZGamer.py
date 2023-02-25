{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 1,
   "id": "dc8bee7c-4679-4ff8-b063-0b3331bde62f",
   "metadata": {
    "tags": []
   },
   "outputs": [],
   "source": [
    "import cv2\n",
    "import numpy as np\n",
    "import sklearn\n",
    "from sklearn import cluster"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 2,
   "id": "963e5132-63fb-460c-9775-ce2df2a979c0",
   "metadata": {
    "tags": []
   },
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "4.7.0\n",
      "1.2.1\n"
     ]
    }
   ],
   "source": [
    "print(cv2.__version__)\n",
    "print(sklearn.__version__)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 3,
   "id": "616df10c-554b-40cb-8ca2-cac46c7eebc0",
   "metadata": {
    "tags": []
   },
   "outputs": [],
   "source": [
    "vid = cv2.VideoCapture(0)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 4,
   "id": "e71ec655-49bc-4c90-b371-11a69f468403",
   "metadata": {
    "tags": []
   },
   "outputs": [],
   "source": [
    "def get_blobs(frame):\n",
    "    frame_blurred = cv2.medianBlur(frame, 7)\n",
    "    frame_gray = cv2.cvtColor(frame_blurred, cv2.COLOR_BGR2GRAY)\n",
    "    blobs = detector.detect(frame_gray)\n",
    "    return blobs"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 5,
   "id": "b4d38478-3bb6-423b-99b4-7428d23db729",
   "metadata": {
    "tags": []
   },
   "outputs": [],
   "source": [
    "def get_dice_from_blobs(blobs):\n",
    "    # Get centroids of all blobs\n",
    "    X = []\n",
    "    for b in blobs:\n",
    "        pos = b.pt\n",
    "\n",
    "        if pos != None:\n",
    "            X.append(pos)\n",
    "\n",
    "    X = np.asarray(X)\n",
    "\n",
    "    if len(X) > 0:\n",
    "        clustering = cluster.DBSCAN(eps=50, min_samples=1).fit(X)\n",
    "        #clustering = cluster.OPTICS(eps=40, max_eps=50, min_samples=1).fit(X)\n",
    "\n",
    "        # Find the largest label assigned + 1, that's the number of dice found\n",
    "        num_dice = max(clustering.labels_) + 1\n",
    "\n",
    "        dice = []\n",
    "\n",
    "        # Calculate centroid of each dice, the average between all a dice's dots\n",
    "        for i in range(num_dice):\n",
    "            X_dice = X[clustering.labels_ == i]\n",
    "\n",
    "            centroid_dice = np.mean(X_dice, axis=0)\n",
    "\n",
    "            dice.append([len(X_dice), *centroid_dice])\n",
    "\n",
    "        return dice\n",
    "\n",
    "    else:\n",
    "        return []"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 6,
   "id": "cae46943-f0bb-47b7-ad63-2f6f6d0f52b6",
   "metadata": {
    "tags": []
   },
   "outputs": [],
   "source": [
    "def overlay_info(frame, dice, blobs):\n",
    "    # Overlay blobs\n",
    "    for b in blobs:\n",
    "        pos = b.pt\n",
    "        r = b.size / 2\n",
    "\n",
    "        cv2.circle(frame, (int(pos[0]), int(pos[1])),\n",
    "                   int(r), (255, 0, 0), 2)\n",
    "\n",
    "    # Overlay dice number\n",
    "    for d in dice:\n",
    "        # Get textsize for text centering\n",
    "        textsize = cv2.getTextSize(\n",
    "            str(d[0]), cv2.FONT_HERSHEY_PLAIN, 3, 2)[0]\n",
    "\n",
    "        cv2.putText(frame, str(d[0]),\n",
    "                    (int(d[1] - textsize[0] / 2),\n",
    "                     int(d[2] + textsize[1] / 2)),\n",
    "                    cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 2)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 8,
   "id": "e6402323-38ab-4894-acc9-3ef293363425",
   "metadata": {
    "tags": []
   },
   "outputs": [
    {
     "ename": "error",
     "evalue": "OpenCV(4.7.0) /io/opencv/modules/highgui/src/window.cpp:971: error: (-215:Assertion failed) size.width>0 && size.height>0 in function 'imshow'\n",
     "output_type": "error",
     "traceback": [
      "\u001b[0;31m---------------------------------------------------------------------------\u001b[0m",
      "\u001b[0;31merror\u001b[0m                                     Traceback (most recent call last)",
      "Cell \u001b[0;32mIn[8], line 13\u001b[0m\n\u001b[1;32m      8\u001b[0m ret, frame \u001b[38;5;241m=\u001b[39m vid\u001b[38;5;241m.\u001b[39mread()\n\u001b[1;32m      9\u001b[0m \u001b[38;5;66;03m#blobs = get_blobs(frame)\u001b[39;00m\n\u001b[1;32m     10\u001b[0m \u001b[38;5;66;03m#dice = get_dice_from_blobs(blobs)\u001b[39;00m\n\u001b[1;32m     11\u001b[0m \u001b[38;5;66;03m#out_frame = overlay_info(frame, dice, blobs)\u001b[39;00m\n\u001b[0;32m---> 13\u001b[0m \u001b[43mcv2\u001b[49m\u001b[38;5;241;43m.\u001b[39;49m\u001b[43mimshow\u001b[49m\u001b[43m(\u001b[49m\u001b[38;5;124;43m'\u001b[39;49m\u001b[38;5;124;43mframe\u001b[39;49m\u001b[38;5;124;43m'\u001b[39;49m\u001b[43m,\u001b[49m\u001b[43mframe\u001b[49m\u001b[43m)\u001b[49m\n\u001b[1;32m     14\u001b[0m \u001b[38;5;28;01mif\u001b[39;00m cv2\u001b[38;5;241m.\u001b[39mwaitKey(\u001b[38;5;241m1\u001b[39m) \u001b[38;5;241m&\u001b[39m \u001b[38;5;241m0xFF\u001b[39m \u001b[38;5;241m==\u001b[39m \u001b[38;5;28mord\u001b[39m(\u001b[38;5;124m'\u001b[39m\u001b[38;5;124mq\u001b[39m\u001b[38;5;124m'\u001b[39m):\n\u001b[1;32m     15\u001b[0m     \u001b[38;5;28;01mbreak\u001b[39;00m\n",
      "\u001b[0;31merror\u001b[0m: OpenCV(4.7.0) /io/opencv/modules/highgui/src/window.cpp:971: error: (-215:Assertion failed) size.width>0 && size.height>0 in function 'imshow'\n"
     ]
    }
   ],
   "source": [
    "params = cv2.SimpleBlobDetector_Params()\n",
    "params.filterByInertia\n",
    "params.minInertiaRatio = 0.6\n",
    "\n",
    "detector = cv2.SimpleBlobDetector_create(params)\n",
    "\n",
    "while(True):\n",
    "    ret, frame = vid.read()\n",
    "    #blobs = get_blobs(frame)\n",
    "    #dice = get_dice_from_blobs(blobs)\n",
    "    #out_frame = overlay_info(frame, dice, blobs)\n",
    "    \n",
    "    cv2.imshow('frame',frame)\n",
    "    if cv2.waitKey(1) & 0xFF == ord('q'):\n",
    "        break\n",
    "        \n",
    "vid.release()\n",
    "cv2.destroyAllWindows()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 10,
   "id": "5012a5fc-2525-44e6-a798-237565e80266",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "< cv2.VideoCapture 0x7f4eb39f70>\n",
      "False\n",
      "None\n"
     ]
    }
   ],
   "source": [
    "vid = cv2.VideoCapture(0)\n",
    "ret, frame = vid.read()\n",
    "print(vid)\n",
    "print(ret)\n",
    "print(frame)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 10,
   "id": "e65a4304-3dd3-4b42-8fbe-795981437911",
   "metadata": {},
   "outputs": [
    {
     "ename": "error",
     "evalue": "OpenCV(4.7.0) /io/opencv/modules/highgui/src/window.cpp:971: error: (-215:Assertion failed) size.width>0 && size.height>0 in function 'imshow'\n",
     "output_type": "error",
     "traceback": [
      "\u001b[0;31m---------------------------------------------------------------------------\u001b[0m",
      "\u001b[0;31merror\u001b[0m                                     Traceback (most recent call last)",
      "Cell \u001b[0;32mIn[10], line 1\u001b[0m\n\u001b[0;32m----> 1\u001b[0m \u001b[43mcv2\u001b[49m\u001b[38;5;241;43m.\u001b[39;49m\u001b[43mimshow\u001b[49m\u001b[43m(\u001b[49m\u001b[38;5;124;43m'\u001b[39;49m\u001b[38;5;124;43mframe\u001b[39;49m\u001b[38;5;124;43m'\u001b[39;49m\u001b[43m,\u001b[49m\u001b[43mframe\u001b[49m\u001b[43m)\u001b[49m\n",
      "\u001b[0;31merror\u001b[0m: OpenCV(4.7.0) /io/opencv/modules/highgui/src/window.cpp:971: error: (-215:Assertion failed) size.width>0 && size.height>0 in function 'imshow'\n"
     ]
    }
   ],
   "source": [
    " cv2.imshow('frame',frame)"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3 (ipykernel)",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.9.2"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
