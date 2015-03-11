from __future__ import division

import sys
import yaml

import numpy
import cv2
import scipy.misc

import constants


def mkmat(rows, cols, L):
    mat = numpy.matrix(L, dtype='float64')
    mat.resize((rows,cols))
    return mat

class PinholeCameraModel(object):
    def rectifyPoint(self, uv_raw):
        src = mkmat(1, 2, list(uv_raw))
        src.resize((1, 1, 2))
        dst = src.copy()
        res = cv2.undistortPoints(src, self.K, self.D, dst, self.R, self.P)
        return [float(res[0,0,0]), float(res[0,0,1])]
    
    def project3dToPixel(self, point):
        src = mkmat(4, 1, [point[0], point[1], point[2], 1.0])
        dst = self.P * src
        x = dst[0,0]
        y = dst[1,0]
        w = dst[2,0]
        return x / w, y / w

with open(sys.argv[2], 'rb') as f:
    calibration = yaml.load(f)

model = PinholeCameraModel()
model.K = mkmat(3, 3, calibration['camera_matrix']['data'])
model.D = mkmat(5, 1, calibration['distortion_coefficients']['data'])
model.R = mkmat(3, 3, calibration['rectification_matrix']['data'])
model.P = mkmat(3, 4, calibration['projection_matrix']['data'])

c2 = lambda (x, y): model.project3dToPixel((y, -x, 1))
c = lambda (x, y): model.rectifyPoint(c2((x, y)))

d = {}
image_array = numpy.zeros((constants.H_DISPLAY_END, constants.V_DISPLAY_END, 3), dtype=numpy.uint8)
with open(sys.argv[1], 'rb') as f:
    for line in f:
        x, y, Rx, Ry, Gx, Gy, Bx, By = map(float, line.split(','))
        x = int(x)
        y = int(y)
        #if x < constants.V_DISPLAY_END*3//16 or x > constants.V_DISPLAY_END*5//16 or y < constants.H_DISPLAY_END*3//8 or y > constants.H_DISPLAY_END*5//8:
        #    continue
        #print x, y, Gx, Gy,
        
        tRx, tRy = c2((Rx, Ry))
        tGx, tGy = c2((Gx, Gy))
        tBx, tBy = c2((Bx, By))
        
        CROP = 20
        red_bad   = tRx < -CROP or tRx >= constants.CAMERA_COLUMNS+CROP or tRy < -CROP or tRy >= constants.CAMERA_ROWS+CROP
        green_bad = tGx < -CROP or tGx >= constants.CAMERA_COLUMNS+CROP or tGy < -CROP or tGy >= constants.CAMERA_ROWS+CROP
        blue_bad  = tBx < -CROP or tBx >= constants.CAMERA_COLUMNS+CROP or tBy < -CROP or tBy >= constants.CAMERA_ROWS+CROP
        
        #print Gx, Gy,
        
        Rx, Ry = c((Rx, Ry))
        Gx, Gy = c((Gx, Gy))
        Bx, By = c((Bx, By))
        
        #print Gx, Gy,
        
        Rx = int(round(Rx))
        Ry = int(round(Ry))
        Gx = int(round(Gx))
        Gy = int(round(Gy))
        Bx = int(round(Bx))
        By = int(round(By))
        #print Gx, Gy
        
        if not (0 <= Rx < constants.CAMERA_COLUMNS and 0 <= Ry < constants.CAMERA_ROWS): red_bad = True
        if not (0 <= Gx < constants.CAMERA_COLUMNS and 0 <= Gy < constants.CAMERA_ROWS): green_bad = True
        if not (0 <= Bx < constants.CAMERA_COLUMNS and 0 <= By < constants.CAMERA_ROWS): blue_bad = True
        
        if not red_bad: image_array[y, x, 0] = 255
        if not green_bad: image_array[y, x, 1] = 255
        if not blue_bad: image_array[y, x, 2] = 255
        
        d[x, y] = [(Rx, Ry), (Gx, Gy), (Bx, By)]
        if red_bad:   d[x, y][0] = -1, -1
        if green_bad: d[x, y][1] = -1, -1
        if blue_bad:  d[x, y][2] = -1, -1
d = numpy.array([[d[x, y] for y in xrange(constants.H_DISPLAY_END)] for x in xrange(constants.V_DISPLAY_END)])


with open(sys.argv[3], 'wb') as f:
    numpy.save(f, d)
scipy.misc.imsave('outfile.png', image_array)
