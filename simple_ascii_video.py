#!/usr/bin/env python3
"""
Simplified ASCII Video Converter - More reliable version
"""

import cv2
import numpy as np
import argparse
import os
import sys

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

class SimpleVideoToASCII:
    def __init__(self, width=60):
        self.ascii_chars = "@%#*+=-:. "
        self.width = width
        self.char_width = 8
        self.char_height = 16
        
    def frame_to_ascii(self, frame):
        """Convert frame to simple ASCII"""
        # Convert to grayscale and resize
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        height, original_width = gray.shape
        aspect_ratio = height / original_width
        new_height = int(self.width * aspect_ratio * 0.5)
        
        resized = cv2.resize(gray, (self.width, new_height))
        
        # Convert to ASCII
        ascii_frame = ""
        for row in resized:
            for pixel in row:
                # Clamp pixel value and calculate index safely
                pixel = max(0, min(255, int(pixel)))
                char_index = int(pixel * (len(self.ascii_chars) - 1) / 255)
                char_index = max(0, min(len(self.ascii_chars) - 1, char_index))
                ascii_frame += self.ascii_chars[char_index]
            ascii_frame += "\n"
        
        return ascii_frame
    
    def ascii_to_simple_image(self, ascii_text, bg_color=(0, 0, 0)):
        """Convert ASCII to image using simple rectangle drawing"""
        if not PIL_AVAILABLE:
            return None
            
        lines = ascii_text.strip().split('\n')
        if not lines:
            return None
        
        # Calculate dimensions
        img_width = len(lines[0]) * self.char_width
        img_height = len(lines) * self.char_height
        
        # Create image
        img = Image.new('RGB', (img_width, img_height), bg_color)
        draw = ImageDraw.Draw(img)
        
        # Draw each character as a filled rectangle with brightness-based color
        for y, line in enumerate(lines):
            for x, char in enumerate(line):
                if char in self.ascii_chars:
                    # Map character to brightness (darker chars = darker color)
                    brightness = int((self.ascii_chars.index(char) / (len(self.ascii_chars) - 1)) * 255)
                    color = (brightness, brightness, brightness)
                    
                    # Draw filled rectangle for this character
                    x1 = x * self.char_width
                    y1 = y * self.char_height
                    x2 = x1 + self.char_width - 1
                    y2 = y1 + self.char_height - 1
                    
                    draw.rectangle([x1, y1, x2, y2], fill=color)
        
        return img
    
    def create_video(self, video_path, output_path, max_frames=100):
        """Create ASCII video with simple, reliable method"""
        print(f"Processing: {video_path}")
        
        # Open video
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print("Error: Could not open video")
            return False
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        print(f"Original FPS: {fps}")
        
        # Process frames
        ascii_frames = []
        frame_count = 0
        
        while len(ascii_frames) < max_frames:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Skip frames for speed (process every 3rd frame)
            if frame_count % 3 == 0:
                ascii_frame = self.frame_to_ascii(frame)
                ascii_frames.append(ascii_frame)
                
                if len(ascii_frames) % 10 == 0:
                    print(f"Processed {len(ascii_frames)} frames")
            
            frame_count += 1
        
        cap.release()
        print(f"Total ASCII frames: {len(ascii_frames)}")
        
        if not ascii_frames:
            print("No frames processed")
            return False
        
        # Create video from ASCII frames
        print("Creating video...")
        first_img = self.ascii_to_simple_image(ascii_frames[0])
        if not first_img:
            print("Could not create image from ASCII")
            return False
        
        width, height = first_img.size
        
        # Use a more compatible codec
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(output_path.replace('.mp4', '.avi'), fourcc, fps/3, (width, height))
        
        if not out.isOpened():
            print("Error: Could not create video writer")
            return False
        
        # Write frames
        for i, ascii_frame in enumerate(ascii_frames):
            img = self.ascii_to_simple_image(ascii_frame)
            if img:
                img_array = np.array(img)
                img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                out.write(img_bgr)
            
            if (i + 1) % 10 == 0:
                print(f"Writing frame {i + 1}/{len(ascii_frames)}")
        
        out.release()
        final_output = output_path.replace('.mp4', '.avi')
        print(f"Video saved as: {final_output}")
        return True

def main():
    parser = argparse.ArgumentParser(description="Simple ASCII Video Converter")
    parser.add_argument("video_file", help="Input video file")
    parser.add_argument("--output", "-o", default="simple_ascii.avi", help="Output file")
    parser.add_argument("--width", "-w", type=int, default=60, help="ASCII width")
    parser.add_argument("--frames", "-f", type=int, default=100, help="Max frames to process")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.video_file):
        print(f"Error: Video file not found: {args.video_file}")
        return
    
    converter = SimpleVideoToASCII(width=args.width)
    success = converter.create_video(args.video_file, args.output, args.frames)
    
    if success:
        print("✅ Conversion completed successfully!")
    else:
        print("❌ Conversion failed")

if __name__ == "__main__":
    main()