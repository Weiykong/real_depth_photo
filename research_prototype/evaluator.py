
import cv2
import numpy as np

def get_sharpness_score(image):
    """Calculates the Laplacian variance to estimate sharpness."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return cv2.Laplacian(gray, cv2.CV_64F).var()

def get_exposure_score(image):
    """
    Calculates an exposure score based on how many pixels are in a good range (not clipped).
    Higher is better.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Prefer images where the mean brightness is around 128
    mean_brightness = np.mean(gray)
    exposure_balance = 1.0 - abs(mean_brightness - 128) / 128.0

    # Penalize extreme clipping (pure black or pure white)
    black_pixels = np.sum(gray < 5) / gray.size
    white_pixels = np.sum(gray > 250) / gray.size
    clipping_penalty = (black_pixels + white_pixels)

    return exposure_balance * (1.0 - clipping_penalty)

def pick_hero_frame(image_list):
    """Returns the index of the best frame considering sharpness and exposure."""
    if not image_list:
        return -1

    sharpness_scores = [get_sharpness_score(img) for img in image_list]
    exposure_scores = [get_exposure_score(img) for img in image_list]

    # Normalize scores
    s_max = max(sharpness_scores) if max(sharpness_scores) > 0 else 1
    sharpness_scores = [s / s_max for s in sharpness_scores]

    # Combine scores: 70% sharpness, 30% exposure
    combined_scores = [
        0.7 * s + 0.3 * e for s, e in zip(sharpness_scores, exposure_scores)
    ]

    return np.argmax(combined_scores)