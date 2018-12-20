
from distutils.version import StrictVersion
import numpy as np
import os
import six.moves.urllib as urllib
import sys
import tarfile
import tensorflow as tf
import zipfile
import cv2
import math
import CentroidTracker
import Draw as draw
import CheckMoto
from collections import OrderedDict
import glob
import imutils
import socket
from scipy.spatial import distance as dist

from collections import defaultdict
from io import StringIO
from matplotlib import pyplot as plt
from PIL import Image

from object_detection.utils import ops as utils_ops
from object_detection.utils import label_map_util
import visualization_utils as vis_util
# from utils import label_map_util
# from utils import visualization_utils as vis_util

	  
CWD_PATH = os.getcwd()
MODEL_NAME = 'inference_graph'

#VIDEO_NAME = 'FCAM_34.avi'
# Path to frozen detection graph. This is the actual model that is used for the object detection.

PATH_TO_CKPT = os.path.join(CWD_PATH, MODEL_NAME,'frozen_inference_graph.pb')

# Path to label map file
PATH_TO_LABELS = os.path.join(CWD_PATH,'training','labelmap.pbtxt')

NUM_CLASSES = 5
message = 'STOPPING'
# Path to video
video = os.path.join(CWD_PATH,'video_stop')
for folder in glob.glob(video + '/*.avi'):
    PATH_TO_VIDEO = folder

detection_graph = tf.Graph()
with detection_graph.as_default():
    od_graph_def = tf.GraphDef()
    with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
        serialized_graph = fid.read()
        od_graph_def.ParseFromString(serialized_graph)
        tf.import_graph_def(od_graph_def, name='')

    sess = tf.Session(graph=detection_graph)
	
label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES, use_display_name=True)
category_index = label_map_util.create_category_index(categories)

def load_image_into_numpy_array(image):
  return np.nsarray(image).astype(np.uint8)

cap = cv2.VideoCapture(PATH_TO_VIDEO)
pixelsPerMetric = None

def calculateDistance(location_array):
    total_distance_ver = 0
    total_distance_hor = 0
    for i in range(len(location_array) - 1):
        total_distance_ver += abs(location_array[i][1] - location_array[i + 1][1])
        total_distance_hor += abs(location_array[i][0] - location_array[i + 1][0])

    # check 2 trường hợp, chạy ngang và chạy dọc
    return max(total_distance_ver/(len(location_array) - 1), total_distance_hor/(len(location_array) - 1))

	 
ret = True
count = 0
ct = CentroidTracker.CentroidTracker()
counted_object_id = []

location_object = OrderedDict()

with detection_graph.as_default():
    with tf.Session(graph=detection_graph) as sess:
      # Definite input and output Tensors for detection_graph
      image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
      # Each box represents a part of the image where a particular object was detected.
      detection_boxes = detection_graph.get_tensor_by_name('detection_boxes:0')
      # Each score represent how level of confidence for each of the objects.
      # Score is shown on the result image, together with the class label.
      detection_scores = detection_graph.get_tensor_by_name(
          'detection_scores:0')
      detection_classes = detection_graph.get_tensor_by_name(
          'detection_classes:0')
      num_detections = detection_graph.get_tensor_by_name('num_detections:0')
      ret = True
      while ret:
        ret, image_np = cap.read()
        image_np_expanded = np.expand_dims(image_np, axis=0)
        image_np = imutils.resize(image_np, width=600)
        # Actual detection.
        (boxes, scores, classes, num) = sess.run(
              [detection_boxes, detection_scores,
               detection_classes, num_detections],
              feed_dict={image_tensor: image_np_expanded})
        # Visualization of the results of a detection.
        imageclone = image_np.copy()
        image, box_to_color_map = vis_util.visualize_boxes_and_labels_on_image_array(
              imageclone,
              np.squeeze(boxes),
              np.squeeze(classes).astype(np.int32),
              np.squeeze(scores),
              category_index,
              use_normalized_coordinates=True,
              line_thickness=1,
              skip_labels=True)

        rects = []
        for box, color in box_to_color_map.items():
          ymin, xmin, ymax, xmax = box
          im_height, im_width = image_np.shape[:2]
          (startX, endX, startY, endY) = (int(xmin * im_width), int(xmax * im_width), int(ymin * im_height), int(ymax * im_height))

          rect = (startX, startY, endX, endY)
          rects.append(rect)
          cv2.rectangle(image_np, (startX, startY), (endX, endY), [0, 255, 0], 2)
		 
          #calculate size of vehicles
          size_v = endX - startX
          size_v = (size_v * 37) / 1000
          
          cal_size = "{}".format(size_v)
          cv2.putText(image_np, cal_size, (startX, startY), 
              cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255.0), 2)
                   					
        cv2.imshow("image", image_np)
        
        # Press 'q' to quit
        if cv2.waitKey(1) == ord('q'):
            break
cap.release()
cv2.destroyAllWindows()