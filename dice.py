import cv2
import numpy as np
import sklearn
from sklearn import cluster

params = cv2.SimpleBlobDetector_Params()
params.filterByInertia
#filter out things too elongated, likely not on top face
params.minInertiaRatio = 0.75
params.maxInertiaRatio = 1
params.minCircularity = 0.95
params.maxCircularity = 1
params.blobColor = 0
params.minThreshold = 50
params.maxThreshold = 150


detector = cv2.SimpleBlobDetector_create(params)

def get_blobs(frame):
    blobs = detector.detect(frame)
    return blobs

def simplify_dice(complex_dice) :
    simple_dice = [sub_array[0] for sub_array in complex_dice]
    simple_dice.sort()
    return simple_dice

def get_dice_from_blobs(blobs):
    # Get centroids of all blobs
    X = []
    for b in blobs:
        pos = b.pt
        if pos != None:
            X.append(pos)

    X = np.asarray(X)

    if len(X) > 0:
        clustering = cluster.DBSCAN(eps=50, min_samples=1).fit(X)
        #clustering = cluster.OPTICS(eps=40, max_eps=50, min_samples=1).fit(X)

        # Find the largest label assigned + 1, that's the number of dice found
        num_dice = max(clustering.labels_) + 1

        dice = []

        # Calculate centroid of each dice, the average between all a dice's dots
        for i in range(num_dice):
            X_dice = X[clustering.labels_ == i]

            centroid_dice = np.mean(X_dice, axis=0)

            dice.append([len(X_dice), *centroid_dice])

        return dice

    else:
        return []
