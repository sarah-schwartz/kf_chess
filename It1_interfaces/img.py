from __future__ import annotations

import pathlib

import cv2
import numpy as np

class Img:
    def __init__(self):
        self.img = None

    # Read an image from a file and optionally resize it
    def read(self, path: str | pathlib.Path,   
             size: tuple[int, int] | None = None,
             keep_aspect: bool = False,
             interpolation: int = cv2.INTER_AREA) -> "Img":
        path = str(path)
        self.img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        if self.img is None:
            raise FileNotFoundError(f"Cannot load image: {path}")

        if size is not None:  # Resize if size is specified
            target_w, target_h = size
            h, w = self.img.shape[:2]

            if keep_aspect:
                scale = min(target_w / w, target_h / h)
                new_w, new_h = int(w * scale), int(h * scale)
            else:
                new_w, new_h = target_w, target_h

            self.img = cv2.resize(self.img, (new_w, new_h), interpolation=interpolation)

        return self
    
    def set(self, img_array: np.ndarray) -> "Img":
        """Set the image from a numpy array"""
        self.img = img_array.copy()  # Create a copy to avoid reference issues
        return self
        
    def clone(self) -> "Img":
        """Create a deep copy of this image"""
        new_img = Img()
        if self.img is not None:
            new_img.img = self.img.copy()
        else:
            new_img.img = None
        return new_img

    def draw_on(self, other_img, x, y): # Draw this image on another image at position (x, y)
        if self.img is None or other_img.img is None:
            raise ValueError("Both images must be loaded before drawing.")

        if self.img.shape[2] != other_img.img.shape[2]: # Check if channel count matches
            if self.img.shape[2] == 3 and other_img.img.shape[2] == 4:
                self.img = cv2.cvtColor(self.img, cv2.COLOR_BGR2BGRA)
            elif self.img.shape[2] == 4 and other_img.img.shape[2] == 3:
                self.img = cv2.cvtColor(self.img, cv2.COLOR_BGRA2BGR)

        h, w = self.img.shape[:2]
        H, W = other_img.img.shape[:2]

        if y + h > H or x + w > W: # Check if the logo fits in the target image
            raise ValueError("Logo does not fit at the specified position.")

        roi = other_img.img[y:y + h, x:x + w]

        if self.img.shape[2] == 4:
            b, g, r, a = cv2.split(self.img)
            mask = a / 255.0
            for c in range(3):
                roi[..., c] = (1 - mask) * roi[..., c] + mask * self.img[..., c]
        else:
            other_img.img[y:y + h, x:x + w] = self.img

    def put_text(self, txt, x, y, font_size, color=(255, 255, 255, 255), thickness=1): # Add text to the image
        if self.img is None:
            raise ValueError("Image not loaded.")
        cv2.putText(self.img, txt, (x, y),
                    cv2.FONT_HERSHEY_SIMPLEX, font_size,
                    color, thickness, cv2.LINE_AA)

    def show(self):
        if self.img is None:
            raise ValueError("Image not loaded.")
        cv2.imshow("Image", self.img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
