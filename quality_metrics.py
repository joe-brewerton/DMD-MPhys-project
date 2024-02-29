#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 30 12:04:46 2024

@author: tabithajohn
"""
from skimage.metrics import structural_similarity as ssim
import cv2
import numpy as np

# Assess Image Quality
class quality:
    def __init__(self, ground_image, reconstruction_image):
        self.ground_image = ground_image
        self.reconstruction_image = reconstruction_image
    def rescale(arr):
        min_val = arr.min()
        max_val = arr.max()
        normalized_arr = (arr - min_val) / (max_val - min_val)
        rescaled_arr = (normalized_arr * 255)
        return rescaled_arr
    def PSNR(self):
        mse = self.mse()
        if mse == 0:
            return float('inf') 
        psnr = 10 * np.log10((np.max(self.ground_image) ** 2) / mse)
        return psnr
    def mse(self):
        assert self.ground_image.shape == self.reconstruction_image.shape
        err = np.sum(abs(self.ground_image - self.reconstruction_image) ** 2)
        err = err / float(self.ground_image.shape[0]* self.reconstruction_image.shape[1])
        return err
    def SSIM(self):
        return ssim(self.ground_image, self.reconstruction_image)
    def ncc(self):
        ncc = np.sum((self.ground_image - np.mean(self.ground_image)) * (self.reconstruction_image - np.mean(self.reconstruction_image))) / (np.std(self.ground_image) * np.std(self.reconstruction_image) * self.ground_image.size)
        return ncc
    def dynamic_range(self):
        min_intensity = self.reconstruction_image.min()
        print(min_intensity)
        max_intensity = self.reconstruction_image.max()
        print(max_intensity)
        ground_range = self.ground_image.max() - self.ground_image.min()
        dyn_range = (max_intensity - min_intensity) 
        return dyn_range 
    def std_dev(self):
        mean_intensity = np.mean(self.reconstruction_image)
        variance = np.mean((self.reconstruction_image - mean_intensity)**2)
        std_dev = np.sqrt(variance)
        return std_dev
    def mae(self):
        mae = np.mean(np.abs(self.ground_image - self.reconstruction_image))
        return mae
    def execute(self):
        mse = self.mse()
        psnr = self.PSNR()
        SSIM = self.SSIM()
        ncc = self.ncc()
        dyn_range = self.dynamic_range()
        std_dev = self.std_dev()
        mae = self.mae()
        
        print(f" MSE: {mse}, PSNR: {psnr}, SSIM: {SSIM}, NCC: {ncc}, Dynamic Range:{dyn_range}, Standard Deviation: {std_dev}, MAE: {mae}")
        return
    
    
    
    
    
    