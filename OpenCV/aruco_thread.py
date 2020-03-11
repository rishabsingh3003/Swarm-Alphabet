import numpy as np
import cv2
import cv2.aruco as aruco
import glob
import math
import threading
import csv
import pandas as pd

#cap = cv2.VideoCapture(1)
class VideoCaptureAsync:
    def __init__(self, src=0, width=640, height=480):
        self.src = src
        self.cap = cv2.VideoCapture(self.src)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.grabbed, self.frame = self.cap.read()
        self.started = False
        self.read_lock = threading.Lock()

    def set(self, var1, var2):
        self.cap.set(var1, var2)

    def start(self):
        if self.started:
            print('[!] Asynchroneous video capturing has already been started.')
            return None
        self.started = True
        self.thread = threading.Thread(target=self.update, args=())
        self.thread.start()
        return self

    def update(self):
        while self.started:
            grabbed, frame = self.cap.read()
            with self.read_lock:
                self.grabbed = grabbed
                self.frame = frame

    def read(self):
        with self.read_lock:
            frame = self.frame.copy()
            grabbed = self.grabbed
        return grabbed, frame

    def stop(self):
        self.started = False
        self.thread.join()

    def __exit__(self, exec_type, exc_value, traceback):
        self.cap.release()


cap = VideoCaptureAsync(1)
####---------------------- CALIBRATION ---------------------------
# termination criteria for the iterative algorithm
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.1)

# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
# checkerboard of size (7 x 6) is used
objp = np.zeros((6*9,3), np.float32)
objp[:,:2] = np.mgrid[0:9,0:6].T.reshape(-1,2)
objp *= 3.5

# arrays to store object points and image points from all the images.
objpoints = [] # 3d point in real world space
imgpoints = [] # 2d points in image plane.

# iterating through all calibration images
# in the folder
images = glob.glob('./calib_images/*.png')

for fname in images:
	img = cv2.imread(fname)
	gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)


	# find the chess board (calibration pattern) corners
	ret, corners = cv2.findChessboardCorners(gray, (9,6),None)

	# if calibration pattern is found, add object points,
	# image points (after refining them)
	if ret == True:
		objpoints.append(objp)

		# Refine the corners of the detected corners
		corners2 = cv2.cornerSubPix(gray,corners,(5,5),(-1,-1),criteria)
		imgpoints.append(corners2)

		# Draw and display the corners
		img = cv2.drawChessboardCorners(img, (9,6), corners2,ret)


ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1],None,None)
print("\nRMS:", ret)
print("camera matrix:\n", mtx)
print("distortion coefficients: ", dist.ravel())

def detect_angle(x1,y1,x2,y2):
			try:
				val = (y2-y1)/(x2-x1)
				val = math.atan(abs(val))
				val = ((int)(val* 180/3.1416))%360
				if(x2-x1 ==0):
					val = 90 
				val = 360 - val
				if(x2<x1 and y2>y1):
					val = (180 - val)%360 
				elif(x2<x1 and y1>y2):
					val = (180 + val)%360
				elif(x2>x1 and y2>y1):
					pass
				elif(x2>x1 and y2<y1):
					val = (360 - val)%360
				return val
			except:
				pass
###------------------ ARUCO TRACKER ---------------------------
cap.start()
while (True):
	ret, frame = cap.read()
	

	# operations on the frame
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

	# set dictionary size depending on the aruco marker selected
	aruco_dict = aruco.Dictionary_get(aruco.DICT_5X5_50)

	# detector parameters can be set here (List of detection parameters[3])
	parameters = aruco.DetectorParameters_create()
	parameters.adaptiveThreshConstant = 10

	# lists of ids and the corners belonging to each id
	corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)
	# frame = cv2.circle(frame,(300,400),10,(0,0,200),-1)
	# font for displaying text (below)
	font = cv2.FONT_HERSHEY_SIMPLEX

	# check if the ids list is not empty
	# if no check is added the code will crash
	if np.all(ids != None):

		# estimate pose of each marker and return the values
		# rvet and tvec-different from camera coefficients
		rvec, tvec ,_ = aruco.estimatePoseSingleMarkers(corners, 0.05, mtx, dist)
		(rvec-tvec).any() # get rid of that nasty numpy value array error

		# for i in range(0, ids.size):
		#     # draw axis for the aruco markers
		#     aruco.drawAxis(frame, mtx, dist, rvec[i], tvec[i], 0.1)

		# draw a square around the markers
		aruco.drawDetectedMarkers(frame, corners)


		# code to show ids of the marker found
		strg = ''
		for i in range(0, ids.size):
			strg += str(ids[i][0])+', '

			x = np.round(((corners[i-1][0][0][0] + corners[i-1][0][1][0] + corners[i-1][0][2][0] + corners[i-1][0][3][0]) / 4),0)
			y = np.round(((corners[i-1][0][0][1] + corners[i-1][0][1][1] + corners[i-1][0][2][1] + corners[i-1][0][3][1]) / 4),0)
			
			# x1 = np.round((0.5*abs(corners[i-1][0][2][0]+corners[i-1][0][0][0])),0)
			# y1 = np.round((0.5*abs(corners[i-1][0][2][1]+corners[i-1][0][0][1])),0)

			x2 = np.round((0.5*abs(corners[i-1][0][1][0]+corners[i-1][0][0][0])),0)
			y2 = np.round((0.5*abs(corners[i-1][0][1][1]+corners[i-1][0][0][1])),0)

			cv2.putText(frame, "ID:" + str(ids[i-1][0]), (int(x-30),int(y-65)), font, 0.8, (255,0,0),2,cv2.LINE_AA)
			cv2.putText(frame, "," + str(y), (int(x),int(y-40)), font, 0.8, (0,0,255),2,cv2.LINE_AA)
			cv2.putText(frame, str(x), (int(x-80),int(y-40)), font, 0.8, (0,0,255),2,cv2.LINE_AA)

			# rotM = np.zeros(shape=(3,3))
			# dst, jacobian = cv2.Rodrigues(rvec[i-1], rotM, jacobian = 0)

			# ypr = cv2.RQDecomp3x3(rotM)
			# yaw = np.round((ypr[0][0]),0)
			# cv2.putText(frame, "deg: " + str(angle), (0,250), font, 1, (0,255,0),2,cv2.LINE_AA)
			val = (str(ids[i-1][0]), str(x),str(y), str(x2), str(y2))
					
			df = pd.DataFrame(data = val).T
			df.to_csv('bot_' +str(ids[i-1][0])+ '.csv', mode='a', header=False)

	else:
		# code to show 'No Ids' when no markers are found
		cv2.putText(frame, "No Ids", (0,64), font, 1, (0,255,0),2,cv2.LINE_AA)

	# display the resulting frame
	cv2.imshow('frame',frame)
	if cv2.waitKey(1) & 0xFF == ord('q'):
		break

# When everything done, release the capture
cap.release()
cap.stop()
cv2.destroyAllWindows()



