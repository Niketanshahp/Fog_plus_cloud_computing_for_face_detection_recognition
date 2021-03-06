# USAGE
# python pi_face_recognition.py --cascade haarcascade_frontalface_default.xml --encodings encodings.pickle

# import the necessary packages
from imutils.video import VideoStream
from imutils.video import FPS
# import face_recognition
# import argparse
import imutils
# import pickle
import time
import cv2
import paho.mqtt.client as mqtt
import numpy as np
import json
import datetime

# construct the argument parser and parse the arguments
# ap = argparse.ArgumentParser()
# ap.add_argument("-c", "--cascade", required=True,
#                 help="path to where the face cascade resides")
# ap.add_argument("-e", "--encodings", required=True,
#                 help="path to serialized db of facial encodings")
# args = vars(ap.parse_args())

# load the known faces and embeddings along with OpenCV's Haar
# cascade for face detection
# print("[INFO] loading encodings + face detector...")
# data = pickle.loads(open(args["encodings"], "rb").read())
# detector = cv2.CascadeClassifier(args["cascade"])

# initialize the video stream and allow the camera sensor to warm up
print("[INFO] starting video stream...")
vs = VideoStream(src=0).start()
# vs = VideoStream(usePiCamera=False).start()
time.sleep(2.0)

# start the FPS counter
fps = FPS().start()


# loop over frames from the video file stream

init = datetime.datetime.now()

def recog():
    # grab the frame from the threaded video stream and resize it
    # to 500px (to speedup processing)
	global init
	frame = vs.read()
    # cv2.imshow("Client", frame)
    # recog()
    # print(frame.dtype)
	print(frame.shape)
	frame = imutils.resize(frame, width=500)
	init = datetime.datetime.now()
	client.publish("topic/up", frame.tostring())
	print("Sent")

    # # convert the input frame from (1) BGR to grayscale (for face
    # # detection) and (2) from BGR to RGB (for face recognition)
    # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # # detect faces in the grayscale frame
    # rects = detector.detectMultiScale(gray, scaleFactor=1.1,
    # 	minNeighbors=5, minSize=(30, 30),
    # 	flags=cv2.CASCADE_SCALE_IMAGE)

    # # OpenCV returns bounding box coordinates in (x, y, w, h) order
    # # but we need them in (top, right, bottom, left) order, so we
    # # need to do a bit of reordering
    # boxes = [(y, x + w, y + h, x) for (x, y, w, h) in rects]

    # # compute the facial embeddings for each face bounding box
    # encodings = face_recognition.face_encodings(rgb, boxes)
    # names = []

    # # loop over the facial embeddings
    # for encoding in encodings:
    # 	# attempt to match each face in the input image to our known
    # 	# encodings
    # 	matches = face_recognition.compare_faces(data["encodings"],
    # 		encoding)
    # 	name = "Unknown"

    # 	# check to see if we have found a match
    # 	if True in matches:
    # 		# find the indexes of all matched faces then initialize a
    # 		# dictionary to count the total number of times each face
    # 		# was matched
    # 		matchedIdxs = [i for (i, b) in enumerate(matches) if b]
    # 		counts = {}

    # 		# loop over the matched indexes and maintain a count for
    # 		# each recognized face face
    # 		for i in matchedIdxs:
    # 			name = data["names"][i]
    # 			counts[name] = counts.get(name, 0) + 1

    # 		# determine the recognized face with the largest number
    # 		# of votes (note: in the event of an unlikely tie Python
    # 		# will select first entry in the dictionary)
    # 		name = max(counts, key=counts.get)

    # 	# update the list of names
    # 	names.append(name)

    # # loop over the recognized faces
    # for ((top, right, bottom, left), name) in zip(boxes, names):
    # 	# draw the predicted face name on the image
    # 	cv2.rectangle(frame, (left, top), (right, bottom),
    # 		(0, 255, 0), 2)
    # 	y = top - 15 if top - 15 > 15 else top + 15
    # 	cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX,
    # 		0.75, (0, 255, 0), 2)

    # # display the image to our screen
    # cv2.imshow("Frame", frame)
    # key = cv2.waitKey(1) & 0xFF

    # if the `q` key was pressed, break from the loop
    # if key == ord("q"):
    #     break

    # update the FPS counter
    # fps.update()


# stop the timer and display FPS information
# fps.stop()
# print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
# print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

# do a bit of cleanup
# cv2.destroyAllWindows()
# vs.stop()

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("topic/down")
    recog()


def on_message(client, userdata, msg):
	print("received")
	print ((datetime.datetime.now()-init).total_seconds() * 1000)
	str = msg.payload
	frame = np.fromstring(str, np.uint8)
	frame = frame.reshape((375, 500, 3))
    # print(frame)
	cv2.imshow("Frame", frame)
	key = cv2.waitKey(1) & 0xFF

	# if the `q` key was pressed, break from the loop
	# print ("Condition")
	if key == ord("q"):
		fps.stop()
		print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
		print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
		cv2.destroyAllWindows()
		vs.stop()
		exit()
	fps.update()
	recog()


client = mqtt.Client()
client.connect("127.0.0.1", 1883, 60)
client.on_connect = on_connect
# time.sleep(1)

# client.publish("topic/test", "Hello world!");
# print("Client published")

client.on_message = on_message


client.loop_forever()
