import torch
import cv2
import numpy as np
from transformers import pipeline
from PIL import Image

class DepthEngine:
    def __init__(self):
        # Using Depth-Anything-V2-Small for speed on Mac/Mobile
        # It provides incredible edge-accuracy for 4K frames
        self.pipe = pipeline(task="depth-estimation", model="depth-anything/Depth-Anything-V2-Small-hf", device="mps")

    def generate_map(self, image, preprocess=True):
        """
        Generates a normalized depth map (0-255) from a 4K image.
        """
        if preprocess:
            processed_img = self.preprocess_image(image)
        else:
            processed_img = image

        # Convert OpenCV BGR to PIL RGB for the transformer
        image_rgb = cv2.cvtColor(processed_img, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(image_rgb)

        # Run inference
        print("Analyzing scene depth...")
        depth = self.pipe(pil_img)["depth"]

        # Convert back to NumPy and resize to match original 4K dimensions
        depth_np = np.array(depth)
        depth_rescaled = cv2.resize(depth_np, (image.shape[1], image.shape[0]), interpolation=cv2.INTER_CUBIC)

        # Normalize to 0-255 for visualization and processing
        depth_normalized = cv2.normalize(depth_rescaled, None, 0, 255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U)

        return depth_normalized

    def preprocess_image(self, image):
        """
        Enhances contrast and reduces noise for better depth estimation in low light.
        """
        # 1. Convert to LAB color space for luminance-based CLAHE
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)

        # 2. Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        cl = clahe.apply(l)

        # 3. Merge back and convert to BGR
        limg = cv2.merge((cl, a, b))
        enhanced = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)

        # 4. Subtle denoising to prevent AI from mistaking noise for texture
        denoised = cv2.fastNlMeansDenoisingColored(enhanced, None, 3, 3, 7, 21)

        return denoised