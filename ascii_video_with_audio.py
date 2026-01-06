#!/usr/bin/env python3
"""
ASCII Video Converter with Audio Support - Reliable Version
"""

import cv2
import numpy as np
import argparse
import os
import sys

try:
    from PIL import Image, ImageDraw
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    from moviepy.editor import VideoFileClip, AudioFileClip
    MOVIEPY_AVAILABLE = True
    print("✅ MoviePy loaded - Audio support enabled")
except ImportError:
    MOVIEPY_AVAILABLE = False
    print("⚠️  MoviePy not available - Audio support disabled")

class ReliableVideoToASCII:
    def __init__(self, width=60, use_color=False):
        self.ascii_chars = "@%#*+=-:. "
        self.width = width
        self.use_color = use_color
        self.char_width = 8
        self.char_height = 16
        
    def frame_to_ascii(self, frame):
        """Convert frame to ASCII with color support"""
        # Resize frame first
        height, original_width = frame.shape[:2]
        aspect_ratio = height / original_width
        new_height = int(self.width * aspect_ratio * 0.5)
        
        resized = cv2.resize(frame, (self.width, new_height))
        
        if self.use_color:
            # Keep color information
            resized_color = resized
            gray_resized = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
        else:
            # Convert to grayscale
            gray_resized = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
            resized_color = None
        
        # Convert to ASCII
        ascii_frame = ""
        for y in range(new_height):
            for x in range(self.width):
                # Get brightness for character selection
                brightness = gray_resized[y, x]
                brightness = max(0, min(255, int(brightness)))
                
                char_index = int(brightness * (len(self.ascii_chars) - 1) / 255)
                char_index = max(0, min(len(self.ascii_chars) - 1, char_index))
                char = self.ascii_chars[char_index]
                
                if self.use_color and resized_color is not None:
                    # Get color information
                    b, g, r = resized_color[y, x]
                    color_code = self.get_color_code(r, g, b)
                    ascii_frame += f"{color_code}{char}"
                else:
                    ascii_frame += char
            ascii_frame += "\n"
        
        if self.use_color:
            ascii_frame += "\033[0m"  # Reset color
        
        return ascii_frame
    
    def get_color_code(self, r, g, b):
        """Convert RGB to ANSI color code"""
        # Simple color mapping
        if r == g == b:  # Grayscale
            if r < 64:
                return "\033[30m"  # Black
            elif r < 128:
                return "\033[90m"  # Dark gray
            elif r < 192:
                return "\033[37m"  # Light gray
            else:
                return "\033[97m"  # White
        else:
            # Basic color mapping
            if r > g and r > b:
                return "\033[91m"  # Red
            elif g > r and g > b:
                return "\033[92m"  # Green
            elif b > r and b > g:
                return "\033[94m"  # Blue
            elif r > 128 and g > 128:
                return "\033[93m"  # Yellow
            elif r > 128 and b > 128:
                return "\033[95m"  # Magenta
            elif g > 128 and b > 128:
                return "\033[96m"  # Cyan
            else:
                return "\033[37m"  # Default
    
    def ascii_to_image(self, ascii_text, bg_color=(0, 0, 0)):
        """Convert ASCII to image"""
        if not PIL_AVAILABLE:
            return None
            
        lines = ascii_text.strip().split('\n')
        if not lines:
            return None
        
        # Remove ANSI codes for dimension calculation
        import re
        clean_lines = [re.sub(r'\033\[[0-9;]*m', '', line) for line in lines]
        max_width = max(len(line) for line in clean_lines) if clean_lines else self.width
        
        img_width = max_width * self.char_width
        img_height = len(clean_lines) * self.char_height
        
        # Create image
        img = Image.new('RGB', (img_width, img_height), bg_color)
        draw = ImageDraw.Draw(img)
        
        # Draw characters as rectangles with brightness-based colors
        for y, line in enumerate(lines):
            x_pos = 0
            i = 0
            current_color = (255, 255, 255)  # Default white
            
            while i < len(line):
                if line[i:i+4] == '\033[':
                    # Skip ANSI color codes
                    end_pos = line.find('m', i)
                    if end_pos != -1:
                        color_code = line[i:end_pos+1]
                        current_color = self.ansi_to_rgb(color_code)
                        i = end_pos + 1
                        continue
                
                if i < len(line) and line[i] != '\n':
                    char = line[i]
                    if char in self.ascii_chars:
                        # Map character to brightness
                        brightness = int((self.ascii_chars.index(char) / (len(self.ascii_chars) - 1)) * 255)
                        if self.use_color:
                            color = current_color
                        else:
                            color = (brightness, brightness, brightness)
                        
                        # Draw rectangle
                        x1 = x_pos
                        y1 = y * self.char_height
                        x2 = x1 + self.char_width - 1
                        y2 = y1 + self.char_height - 1
                        
                        draw.rectangle([x1, y1, x2, y2], fill=color)
                    
                    x_pos += self.char_width
                i += 1
        
        return img
    
    def ansi_to_rgb(self, ansi_code):
        """Convert ANSI color code to RGB"""
        color_map = {
            '\033[30m': (0, 0, 0),      # Black
            '\033[90m': (128, 128, 128), # Dark gray
            '\033[37m': (192, 192, 192), # Light gray
            '\033[97m': (255, 255, 255), # White
            '\033[91m': (255, 0, 0),     # Red
            '\033[92m': (0, 255, 0),     # Green
            '\033[94m': (0, 0, 255),     # Blue
            '\033[93m': (255, 255, 0),   # Yellow
            '\033[95m': (255, 0, 255),   # Magenta
            '\033[96m': (0, 255, 255),   # Cyan
        }
        return color_map.get(ansi_code, (255, 255, 255))
    
    def extract_audio(self, video_path, start_time=0, duration=None):
        """Extract audio from video"""
        if not MOVIEPY_AVAILABLE:
            return None
        
        try:
            video_clip = VideoFileClip(video_path)
            
            if start_time > 0 or duration:
                end_time = start_time + duration if duration else video_clip.duration
                audio_clip = video_clip.subclip(start_time, end_time).audio
            else:
                audio_clip = video_clip.audio
            
            if audio_clip is None:
                print("⚠️  No audio track found")
                video_clip.close()
                return None
            
            temp_audio = "temp_audio.wav"
            audio_clip.write_audiofile(temp_audio, verbose=False, logger=None)
            
            audio_clip.close()
            video_clip.close()
            
            return temp_audio
            
        except Exception as e:
            print(f"⚠️  Audio extraction failed: {e}")
            return None
    
    def combine_video_audio(self, video_path, audio_path, output_path):
        """Combine video with audio"""
        if not MOVIEPY_AVAILABLE:
            return False
        
        try:
            video_clip = VideoFileClip(video_path)
            audio_clip = AudioFileClip(audio_path)
            
            final_clip = video_clip.set_audio(audio_clip)
            final_clip.write_videofile(output_path, codec='libx264', audio_codec='aac', verbose=False, logger=None)
            
            final_clip.close()
            video_clip.close()
            audio_clip.close()
            
            return True
            
        except Exception as e:
            print(f"⚠️  Audio combination failed: {e}")
            return False
    
    def create_video(self, video_path, output_path, max_frames=100, preserve_audio=True):
        """Create ASCII video with optional audio"""
        print(f"🎬 Processing: {video_path}")
        
        # Open video
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print("❌ Could not open video")
            return False
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        print(f"📊 FPS: {fps}, Max frames: {max_frames}")
        print(f"🎨 Width: {self.width}, Color: {self.use_color}")
        
        # Process frames
        ascii_frames = []
        frame_count = 0
        
        while len(ascii_frames) < max_frames:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Process every 2nd frame for speed
            if frame_count % 2 == 0:
                ascii_frame = self.frame_to_ascii(frame)
                ascii_frames.append(ascii_frame)
                
                if len(ascii_frames) % 20 == 0:
                    print(f"📝 Processed {len(ascii_frames)} frames")
            
            frame_count += 1
        
        cap.release()
        print(f"✅ Created {len(ascii_frames)} ASCII frames")
        
        if not ascii_frames:
            print("❌ No frames processed")
            return False
        
        # Create video
        print("🎥 Creating video...")
        first_img = self.ascii_to_image(ascii_frames[0])
        if not first_img:
            print("❌ Could not create image")
            return False
        
        width, height = first_img.size
        temp_video = "temp_ascii.avi"
        
        # Use reliable codec
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(temp_video, fourcc, fps/2, (width, height))
        
        if not out.isOpened():
            print("❌ Could not create video writer")
            return False
        
        # Write frames
        for i, ascii_frame in enumerate(ascii_frames):
            img = self.ascii_to_image(ascii_frame)
            if img:
                img_array = np.array(img)
                img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                out.write(img_bgr)
            
            if (i + 1) % 20 == 0:
                print(f"🎬 Writing frame {i + 1}/{len(ascii_frames)}")
        
        out.release()
        
        # Handle audio
        if preserve_audio and MOVIEPY_AVAILABLE:
            print("🎵 Extracting audio...")
            audio_path = self.extract_audio(video_path, duration=len(ascii_frames)/fps*2)
            
            if audio_path:
                print("🔗 Combining video with audio...")
                success = self.combine_video_audio(temp_video, audio_path, output_path)
                
                # Cleanup
                if os.path.exists(temp_video):
                    os.remove(temp_video)
                if os.path.exists(audio_path):
                    os.remove(audio_path)
                
                if success:
                    print(f"🎉 ASCII video with audio saved: {output_path}")
                    return True
        
        # No audio or audio failed
        if os.path.exists(temp_video):
            if os.path.exists(output_path):
                os.remove(output_path)
            os.rename(temp_video, output_path)
            print(f"🎬 ASCII video saved (no audio): {output_path}")
            return True
        
        return False

def main():
    parser = argparse.ArgumentParser(description="Reliable ASCII Video Converter with Audio")
    parser.add_argument("video_file", help="Input video file")
    parser.add_argument("--output", "-o", default="ascii_output.mp4", help="Output file")
    parser.add_argument("--width", "-w", type=int, default=60, help="ASCII width")
    parser.add_argument("--frames", "-f", type=int, default=150, help="Max frames")
    parser.add_argument("--color", "-c", action="store_true", help="Enable colors")
    parser.add_argument("--no-audio", action="store_true", help="Disable audio")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.video_file):
        print(f"❌ Video file not found: {args.video_file}")
        return
    
    converter = ReliableVideoToASCII(width=args.width, use_color=args.color)
    success = converter.create_video(
        args.video_file, 
        args.output, 
        args.frames, 
        preserve_audio=not args.no_audio
    )
    
    if success:
        print("🎉 Conversion completed successfully!")
    else:
        print("❌ Conversion failed")

if __name__ == "__main__":
    main()