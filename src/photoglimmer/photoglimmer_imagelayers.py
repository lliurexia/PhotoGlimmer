
import numpy as np
import cv2


def  createBlackMask(fg_image_bgr, blurred_mask_graybgr ):
    msk_bgr= blurred_mask_graybgr/255
    bright_masked_bgr= np.uint8(fg_image_bgr * msk_bgr)
    bright_masked_bgr= np.clip(bright_masked_bgr, 0, 255)
    return bright_masked_bgr


def  createWhiteMask(fg_image_bgr, blurred_mask_graybgr ):
    inv_img_bgr= cv2.bitwise_not(fg_image_bgr)
    bright_masked_bgr=   np.uint8(inv_img_bgr * (blurred_mask_graybgr/255))
    bright_masked_bgr= np.clip(bright_masked_bgr, 0, 255)
    return cv2.bitwise_not(bright_masked_bgr)


def  addPreservingBlack( img, n:int):
    img_copy= img.copy()
    mask = img_copy != 0 
    img_copy[mask] += np.int8(n)    
    return np.clip(img_copy, 0, 255)


def  stackBGFGLayers( fg_image_bgr, bg_image_bgr, fgbrightnes, bgbrightness , blurred_mask_graybgr ):
    resultimage=None
    if fgbrightnes <  bgbrightness :     
        whitemasked_fg_layer= createWhiteMask(fg_image_bgr, blurred_mask_graybgr )
        resultimage = cv2.min( whitemasked_fg_layer, bg_image_bgr)
    else :   
        fg_modified= fg_image_bgr.copy() 
        blackmasked_fg_layer= createBlackMask(fg_modified, blurred_mask_graybgr )
        resultimage = cv2.max( blackmasked_fg_layer, bg_image_bgr)
    return resultimage   


def  stackBGFGLayersHSV( fg_image_bgr, bg_image_bgr, fgbrightnes, bgbrightness , blurred_mask_graybgr ):
    resultimage=None
    if fgbrightnes <  bgbrightness :     
        whitemasked_fg_layer= createWhiteMask(fg_image_bgr, blurred_mask_graybgr )
        resultimage = cv2.min( whitemasked_fg_layer, bg_image_bgr)
    else :   
        fg_modified= fg_image_bgr.copy() 
        blackmasked_fg_layer= createBlackMask(fg_modified, blurred_mask_graybgr )
        resultimage = cv2.max( blackmasked_fg_layer, bg_image_bgr)
    return resultimage   


def  blendImages( img1_bgr ,img2_bgr , blendweight_img1=0.5 ):
    addWted_bgr = cv2.addWeighted(img1_bgr,
                              blendweight_img1,
                              img2_bgr, (1.0 -blendweight_img1),
                              gamma=0)
    return addWted_bgr


def  createTrasnparentImage(imgbgr, blurredmaskbgr):
    bgra = cv2.cvtColor(imgbgr, cv2.COLOR_BGR2BGRA)
    # Make sure the mask is a single channel (grayscale)
    if len(blurredmaskbgr.shape) > 2 and blurredmaskbgr.shape[2] == 3:
        # If the mask is BGR, convert it to grayscale
        mask_gray = cv2.cvtColor(blurredmaskbgr, cv2.COLOR_BGR2GRAY)
    else:
        # If it's already single channel, use it directly
        mask_gray = blurredmaskbgr if len(blurredmaskbgr.shape) == 2 else blurredmaskbgr[:,:,0]
    
    # Assign the mask to the alpha channel
    bgra[:, :, 3] = mask_gray
    return bgra