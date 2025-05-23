#!python3
#-*- coding: utf-8 -*-
"""
yolo v3 detection model

@author: RyuManSAng
@date: 20180920
"""
from ctypes import *
import os
import cv2
import numpy as np
import time
import re

# 객체 검출 결과 중 박스 정보
class BOX(Structure):
    _fields_ = [("x", c_float),
                ("y", c_float),
                ("w", c_float),
                ("h", c_float)]

# 객체 검출 결과
class DETECTION(Structure):
    _fields_ = [("bbox", BOX),
                ("classes", c_int),
                ("prob", POINTER(c_float)),
                ("mask", POINTER(c_float)),
                ("objectness", c_float),
                ("sort_class", c_int),
                ("uc", POINTER(c_float)),
                ("points", c_int),
                ("embeddings", POINTER(c_float)),
                ("embedding_size", c_int),
                ("sim", c_float),
                ("track_id", c_int)]

# 객체 검출 결과 배열
class DETNUMPAIR(Structure):
    _fields_ = [("num", c_int),
                ("dets", POINTER(DETECTION))]

# 이미지 정보
class IMAGE(Structure):
    _fields_ = [("w", c_int),
                ("h", c_int),
                ("c", c_int),
                ("data", POINTER(c_float))]

# 메타 데이터
class METADATA(Structure):
    _fields_ = [("classes", c_int),
                ("names", POINTER(c_char_p))]

# GPU 사용 여부
hasGPU = True

# 라이브러리 로드
lib = CDLL("/home/fourind/programming/DetectionModel/darknet/alexy/darknet/libdarknet.so", RTLD_GLOBAL)

# 네트워크 너비 조회
lib.network_width.argtypes = [c_void_p]
lib.network_width.restype = c_int

# 네트워크 높이 조회
lib.network_height.argtypes = [c_void_p]
lib.network_height.restype = c_int

# 이미지 복사
copy_image_from_bytes = lib.copy_image_from_bytes
copy_image_from_bytes.argtypes = [IMAGE,c_char_p]

# 네트워크 너비 조회
def network_width(net):
    return lib.network_width(net)

# 네트워크 높이 조회
def network_height(net):
    return lib.network_height(net)

# 네트워크 예측
predict = lib.network_predict_ptr
predict.argtypes = [c_void_p, POINTER(c_float)]
predict.restype = POINTER(c_float)

# GPU 설정
if hasGPU:
    set_gpu = lib.cuda_set_device
    set_gpu.argtypes = [c_int]

init_cpu = lib.init_cpu
init_cpu.argtypes = [c_int]

make_image = lib.make_image
make_image.argtypes = [c_int, c_int, c_int]
make_image.restype = IMAGE

get_network_boxes = lib.get_network_boxes
get_network_boxes.argtypes = [c_void_p, c_int, c_int, c_float, c_float, POINTER(c_int), c_int, POINTER(c_int), c_int]
get_network_boxes.restype = POINTER(DETECTION)

make_network_boxes = lib.make_network_boxes
make_network_boxes.argtypes = [c_void_p]
make_network_boxes.restype = POINTER(DETECTION)

free_detections = lib.free_detections
free_detections.argtypes = [POINTER(DETECTION), c_int]

free_batch_detections = lib.free_batch_detections
free_batch_detections.argtypes = [POINTER(DETNUMPAIR), c_int]

free_ptrs = lib.free_ptrs
free_ptrs.argtypes = [POINTER(c_void_p), c_int]

network_predict = lib.network_predict_ptr
network_predict.argtypes = [c_void_p, POINTER(c_float)]

reset_rnn = lib.reset_rnn
reset_rnn.argtypes = [c_void_p]

load_net = lib.load_network
load_net.argtypes = [c_char_p, c_char_p, c_int]
load_net.restype = c_void_p

load_net_custom = lib.load_network_custom
load_net_custom.argtypes = [c_char_p, c_char_p, c_int, c_int]
load_net_custom.restype = c_void_p

do_nms_obj = lib.do_nms_obj
do_nms_obj.argtypes = [POINTER(DETECTION), c_int, c_int, c_float]

do_nms_sort = lib.do_nms_sort
do_nms_sort.argtypes = [POINTER(DETECTION), c_int, c_int, c_float]

free_image = lib.free_image
free_image.argtypes = [IMAGE]

letterbox_image = lib.letterbox_image
letterbox_image.argtypes = [IMAGE, c_int, c_int]
letterbox_image.restype = IMAGE

load_meta = lib.get_metadata
lib.get_metadata.argtypes = [c_char_p]
lib.get_metadata.restype = METADATA

load_image = lib.load_image_color
load_image.argtypes = [c_char_p, c_int, c_int]
load_image.restype = IMAGE

rgbgr_image = lib.rgbgr_image
rgbgr_image.argtypes = [IMAGE]

predict_image = lib.network_predict_image
predict_image.argtypes = [c_void_p, IMAGE]
predict_image.restype = POINTER(c_float)

predict_image_letterbox = lib.network_predict_image_letterbox
predict_image_letterbox.argtypes = [c_void_p, IMAGE]
predict_image_letterbox.restype = POINTER(c_float)

network_predict_batch = lib.network_predict_batch
network_predict_batch.argtypes = [c_void_p, IMAGE, c_int, c_int, c_int,
                                   c_float, c_float, POINTER(c_int), c_int, c_int]
network_predict_batch.restype = POINTER(DETNUMPAIR)

# 배열 생성
def c_array(ctype, values):
    arr = (ctype*len(values))()
    arr[:] = values
    return arr

# 네트워크 래핑
class DarknetWrapper:
    net = None
    meta = None

    def __init__(self, configPath, weightPath, namesPath, batch_size=1, gpus=0):
        p = 0
        set_gpu(gpus)

        self.net = load_net_custom(configPath.encode("ascii"), weightPath.encode("ascii"), 0, batch_size)
        self.net_width = network_width(self.net)
        self.net_height = network_height(self.net)
        self.darknet_image = make_image(self.net_width, self.net_height, 3)

        self.meta_names = []
        with open(namesPath) as f:
            try:
                label_list = f.read().strip().splitlines()
                self.meta_names = [x.strip() for x in label_list]
            except TypeError:
                pass
        self.meta_classes = len(self.meta_names)

    # 객체 검출
    def detect(self, frame, thresh=.5, hier_thresh=.5, nms=.45):
        bf_size = frame.shape[:2]
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        if bf_size != (self.net_width, self.net_height):
            frame = cv2.resize(frame, (self.net_width, self.net_height), interpolation=cv2.INTER_LINEAR)
        af_size = frame.shape[:2]
        copy_image_from_bytes(self.darknet_image, frame.tobytes())

        num = c_int(0)
        pnum = pointer(num)
        predict_image(self.net, self.darknet_image)

        letter_box = 0
        dets = get_network_boxes(self.net, self.darknet_image.w, self.darknet_image.h, thresh, hier_thresh, None, 0, pnum, letter_box)
        num = pnum[0]
        if nms:
            do_nms_sort(dets, num, self.meta_classes, nms)

        res = []
        for j in range(num):
            for i in range(self.meta_classes):
                if dets[j].prob[i] > 0:
                    b = dets[j].bbox
                    x = bf_size[1] * (b.x / af_size[1])
                    y = bf_size[0] * (b.y / af_size[0])
                    w = bf_size[1] * (b.w / af_size[1])
                    h = bf_size[0] * (b.h / af_size[0])

                    res.append((self.meta_names[i], dets[j].prob[i], (x, y, w, h)))
        res = sorted(res, key=lambda x: -x[1])
        free_detections(dets, num)
        return res
