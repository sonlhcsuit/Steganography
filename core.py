import numpy as np
import cv2

origin = 'originial_img.jpeg'
to_be_encoded = 'to_be_encoded_img.jpeg'
img = cv2.imread(origin,0)
cv2.imshow('image',img)
cv2.waitKey(0)
cv2.destroyAllWindows()