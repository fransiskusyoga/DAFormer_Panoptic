
from mmseg.core import anchor, build_anchor_generator,build_assigner
import mmseg
import mmcv
import numpy as np
import time
import cv2 as cv
import torch
def show_anchor(input_shape_hw, stride, anchor_generator_cfg, random_n, select_n):
    img = np.zeros(input_shape_hw, np.uint8)
    feature_map = []
    for s in stride:
        feature_map.append([input_shape_hw[0] // s, input_shape_hw[1] // s])
    anchor_generator = build_anchor_generator(anchor_generator_cfg)
    anchors = anchor_generator.grid_anchors(feature_map)  # 输出原图尺度上anchor坐标 xyxy格式 左上角格式
    base_anchors = anchor_generator.base_anchors
    assigner=dict(type='ATSSAssigner', topk=9)
    assigner = build_assigner(assigner)
    
    #print(anchors[0].shape,anchors[1].shape)
    nums_per_level = [len(each) for each in anchors]
    #for each in anchors:
    #    nums_per_level.append(len(each))
    anchors = torch.cat([each for each in anchors],dim=0)
    gt_bboxes = torch.tensor([[100,100,300,300],[400,400,600,600]]).to(anchors.device)
    gt_labels = torch.tensor([1,2]).to(anchors.device)
    #print(anchors.device,gt_bboxes.device)
    #print(nums_per_level)
    assign_result = assigner.assign(anchors, nums_per_level, gt_bboxes, None, gt_labels)
    print((assign_result.gt_inds!=0).nonzero().shape)
    anchors = anchors[(assign_result.gt_inds!=0).nonzero().squeeze(1)]
    print(anchors)
    values,indices = anchors.min(-1)
    anchors = anchors[(values>0).nonzero().squeeze(1)].cpu().numpy()
    print(anchors)
    img_ = mmcv.imshow_bboxes(img, anchors, thickness=1, show=False)
    img_ = mmcv.imshow_bboxes(img_,gt_bboxes.cpu().numpy() , thickness=1, colors='red', show=False)
    cv.imshow('img',img_)
    if cv.waitKey(0) & 0xFF== ord('q'):
        exit(0)
    '''
    for i,each in enumerate(base_anchors):
        each[:,0:4:2] += input_shape_hw[0]//2
        each[:,1:4:2] += input_shape_hw[1]//2
    for _ in range(random_n):
        disp_img = []
        for i,anchor in enumerate(anchors):
            img = np.zeros(input_shape_hw, np.uint8)
            anchor = anchor.cpu().numpy()
            print(anchor.shape)
            index = (anchor[:, 0] > 0) & (anchor[:, 1] > 0) & (anchor[:, 2] < input_shape_hw[1]) & \
                    (anchor[:, 3] < input_shape_hw[0])
            anchor = anchor[index]
            
            anchor = np.random.permutation(anchor)
            img_ = mmcv.imshow_bboxes(img, anchor[:select_n], thickness=1, show=False)
            img_ = mmcv.imshow_bboxes(img_, base_anchors[i].cpu().numpy(), thickness=1, colors='red', show=False)
            #disp_img.append(img_)
            
            #time.sleep(0.3)
    '''
def demo_atss(input_shape_hw):
    stride = [8, 16, 32, 64, 128]
    anchor_generator_cfg = dict(
        type='AnchorGenerator',
        octave_base_scale=8,  # 每层特征图的base anchor scale,如果变大，则整体anchor都会放大
        scales_per_octave=1,  # 每层有3个尺度 2**0 2**(1/3) 2**(2/3)
        ratios=[1.0],  # 每层的anchor有3种长宽比 故每一层每个位置有9个anchor
        strides=stride)  # 每个特征图层输出stride,故anchor范围是4x8=32,4x128x2**(2/3)=812.7
    random_n = 10
    select_n = 100
    show_anchor(input_shape_hw, stride, anchor_generator_cfg, random_n, select_n)





if __name__ == '__main__':
    input_shape_hw = (640, 640, 3)
    demo_atss(input_shape_hw)
    #demo_yolov3(input_shape_hw)