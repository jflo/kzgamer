import cv2

# Open the video file
cap = cv2.VideoCapture('video_file.mp4')

# Check if the video file was successfully opened
if not cap.isOpened():
    print("Error opening video file")

    # Loop through the video frames
    while cap.isOpened():
        # Read a frame from the video
	    ret, frame = cap.read()
	        if ret:
		        # Convert the frame to grayscale
			        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
				        
					        # Apply histogram equalization to the grayscale frame
						        equalized = cv2.equalizeHist(gray)
							        
								        # Display the original and equalized frames
									        cv2.imshow('Original', gray)
										        cv2.imshow('Equalized', equalized)
											        
												        # Exit the loop if the user presses the 'q' key
													        if cv2.waitKey(25) & 0xFF == ord('q'):
														            break
															        else:
																        break

																	# Release the video capture and close all windows
																	cap.release()
																	cv2.destroyAllWindows()

