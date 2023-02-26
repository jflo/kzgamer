import cv2


def movement(frame):
    # Define a background subtractor object
    bg_subtractor = cv2.createBackgroundSubtractorMOG2()

# Loop through the frames of the video
    while True:
        # Apply the background subtraction algorithm to the frame
        fg_mask = bg_subtractor.apply(frame)

        # Threshold the foreground mask to reduce noise
        threshold = 128
        ret, fg_mask = cv2.threshold(fg_mask, threshold, 255, cv2.THRESH_BINARY)

        # Count the number of white pixels in the foreground mask
        num_white_pixels = cv2.countNonZero(fg_mask)

        # If the number of white pixels is above a threshold, motion is detected
        motion_detected = num_white_pixels > 1000

        # Display the frame and foreground mask
        cv2.imshow('frame', frame)
        cv2.imshow('foreground mask', fg_mask)

        # Check for keyboard input to exit the loop
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the video capture object and close all windows
    cap.release()
    cv2.destroyAllWindows()