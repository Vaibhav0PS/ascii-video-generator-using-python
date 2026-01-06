#!/usr/bin/env python3
"""
Enhanced Video to ASCII Art Converter with Color Support

This script converts a video file into ASCII art animation with optional color support.
Requires: opencv-python, numpy, colorama

Usage: python video_to_ascii.py <video_file> [--width WIDTH] [--color] [--output OUTPUT]
"""

import cv2
import numpy as np
import argparse
import time
import os
import sys
import threading
from collections import deque
try:
    from colorama import init, Fore, Back, Style
    init(autoreset=True)
    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False
    print("Warning: colorama not installed. Color mode will be disabled.")
    print("Install with: pip install colorama")

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("Warning: Pillow not installed. Video saving will be disabled.")
    print("Install with: pip install Pillow")

try:
    from moviepy.editor import VideoFileClip, AudioFileClip
    MOVIEPY_AVAILABLE = True
    print("✅ MoviePy loaded successfully - Audio support enabled")
except ImportError as e:
    MOVIEPY_AVAILABLE = False
    print("Warning: moviepy not installed. Audio support will be disabled.")
    print("Install with: pip install moviepy")
    print(f"Import error: {e}")

class VideoToASCII:
    def __init__(self, width=80, use_color=False, quality='medium'):
        # Different ASCII character sets for different quality levels
        self.ascii_sets = {
            'low': "@#*+=-:. ",
            'medium': "@%#*+=-:. ",
            'high': "█▉▊▋▌▍▎▏ ",
            'ultra': "██▓▒░▒▓██"
        }
        
        self.ascii_chars = self.ascii_sets.get(quality, self.ascii_sets['medium'])
        self.width = width
        self.use_color = use_color and COLORAMA_AVAILABLE
        self.quality = quality
        
        # Color mapping for 8-bit colors (256 color mode)
        self.color_codes = [
            16, 17, 18, 19, 20, 21,  # Blues
            22, 28, 34, 40, 46, 82,  # Greens  
            124, 160, 196, 202, 208, 214,  # Reds
            220, 226, 227, 228, 229, 230,  # Yellows
            231, 255  # Whites
        ]
        
        # Video export settings
        self.font_size = 8 if quality == 'high' else 10
        self.char_width = 6 if quality == 'high' else 8
        self.char_height = 12 if quality == 'high' else 14
        
    def resize_frame(self, frame, width):
        """Resize frame while maintaining aspect ratio"""
        height, original_width = frame.shape[:2]
        aspect_ratio = height / original_width
        # Adjust for character aspect ratio (characters are taller than wide)
        char_aspect_ratio = 0.45 if self.quality == 'high' else 0.55
        new_height = int(width * aspect_ratio * char_aspect_ratio)
        return cv2.resize(frame, (width, new_height), interpolation=cv2.INTER_AREA)
    
    def get_color_code(self, r, g, b):
        """Convert RGB to ANSI 256-color code"""
        if not self.use_color:
            return ""
        
        # Convert RGB to closest 256-color palette
        if r == g == b:  # Grayscale
            if r < 8:
                return f"\033[38;5;16m"  # Black
            elif r > 248:
                return f"\033[38;5;231m"  # White
            else:
                gray = 232 + int((r / 255) * 23)
                return f"\033[38;5;{gray}m"
        else:
            # Color mapping
            r_idx = int(r / 255 * 5)
            g_idx = int(g / 255 * 5) 
            b_idx = int(b / 255 * 5)
            color_code = 16 + (36 * r_idx) + (6 * g_idx) + b_idx
            return f"\033[38;5;{color_code}m"
    
    def apply_filters(self, frame):
        """Apply image enhancement filters"""
        # Increase contrast and brightness
        alpha = 1.2  # Contrast control (1.0-3.0)
        beta = 10    # Brightness control (0-100)
        enhanced = cv2.convertScaleAbs(frame, alpha=alpha, beta=beta)
        
        # Apply slight blur to reduce noise
        blurred = cv2.GaussianBlur(enhanced, (3, 3), 0)
        return blurred
    
    def get_rgb_from_ansi(self, ansi_code):
        """Convert ANSI color code back to RGB for video export"""
        if not ansi_code or not ansi_code.startswith('\033[38;5;'):
            return (255, 255, 255)  # Default white
        
        try:
            color_num = int(ansi_code.split(';')[2].rstrip('m'))
            
            # Handle grayscale colors (232-255)
            if 232 <= color_num <= 255:
                gray_val = int((color_num - 232) * 255 / 23)
                return (gray_val, gray_val, gray_val)
            
            # Handle standard colors (16-231)
            if 16 <= color_num <= 231:
                color_num -= 16
                r = (color_num // 36) * 51
                g = ((color_num % 36) // 6) * 51
                b = (color_num % 6) * 51
                return (r, g, b)
            
            # Handle basic colors (0-15)
            basic_colors = [
                (0, 0, 0), (128, 0, 0), (0, 128, 0), (128, 128, 0),
                (0, 0, 128), (128, 0, 128), (0, 128, 128), (192, 192, 192),
                (128, 128, 128), (255, 0, 0), (0, 255, 0), (255, 255, 0),
                (0, 0, 255), (255, 0, 255), (0, 255, 255), (255, 255, 255)
            ]
            if 0 <= color_num < len(basic_colors):
                return basic_colors[color_num]
                
        except (ValueError, IndexError):
            pass
        
        return (255, 255, 255)  # Default white
    
    def ascii_to_image(self, ascii_text, bg_color=(0, 0, 0)):
        """Convert ASCII text to PIL Image for video export"""
        if not PIL_AVAILABLE:
            return None
        
        lines = ascii_text.strip().split('\n')
        if not lines:
            return None
        
        # Calculate image dimensions more accurately
        # Remove ANSI color codes to get actual character count
        clean_lines = []
        for line in lines:
            clean_line = line
            # Remove ANSI color codes
            import re
            clean_line = re.sub(r'\033\[[0-9;]*m', '', clean_line)
            clean_lines.append(clean_line)
        
        max_width = max(len(line) for line in clean_lines) if clean_lines else self.width
        img_width = max_width * self.char_width
        img_height = len(clean_lines) * self.char_height
        
        # Create image
        img = Image.new('RGB', (img_width, img_height), bg_color)
        draw = ImageDraw.Draw(img)
        
        # Try to load a monospace font with better error handling
        font = None
        try:
            if os.name == 'nt':  # Windows
                font_paths = [
                    "C:/Windows/Fonts/consola.ttf",
                    "C:/Windows/Fonts/cour.ttf", 
                    "C:/Windows/Fonts/lucon.ttf"
                ]
                for font_path in font_paths:
                    if os.path.exists(font_path):
                        font = ImageFont.truetype(font_path, self.font_size)
                        break
            else:  # Unix/Linux/MacOS
                font_paths = [
                    "/System/Library/Fonts/Monaco.ttf",  # macOS
                    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",  # Linux
                    "/usr/share/fonts/TTF/DejaVuSansMono.ttf",  # Linux alt
                ]
                for font_path in font_paths:
                    if os.path.exists(font_path):
                        font = ImageFont.truetype(font_path, self.font_size)
                        break
        except Exception as e:
            print(f"Warning: Could not load TrueType font: {e}")
        
        # Fallback to default font if no TrueType font found
        if font is None:
            try:
                font = ImageFont.load_default()
            except:
                # Create a minimal font fallback
                font = None
        
        # Draw text line by line
        y_pos = 0
        for line in lines:
            x_pos = 0
            i = 0
            current_color = (255, 255, 255)  # Default white
            
            while i < len(line):
                if line[i:i+7] == '\033[38;5;':
                    # Extract color code
                    end_pos = line.find('m', i)
                    if end_pos != -1:
                        color_code = line[i:end_pos+1]
                        current_color = self.get_rgb_from_ansi(color_code)
                        i = end_pos + 1
                        continue
                elif line[i:i+4] == '\033[0m':
                    # Reset color
                    current_color = (255, 255, 255)
                    i += 4
                    continue
                
                # Draw character
                if i < len(line):
                    char = line[i]
                    if char != '\n' and char.isprintable():
                        try:
                            if font:
                                draw.text((x_pos, y_pos), char, fill=current_color, font=font)
                            else:
                                # Fallback: draw a simple rectangle for each character
                                draw.rectangle([x_pos, y_pos, x_pos + self.char_width - 1, y_pos + self.char_height - 1], 
                                             fill=current_color)
                        except Exception as e:
                            # Skip problematic characters
                            pass
                        x_pos += self.char_width
                i += 1
            
            y_pos += self.char_height
        
        return img
    
    def frame_to_ascii(self, frame):
        """Convert a frame to ASCII art with optional color"""
        # Apply image enhancements
        enhanced_frame = self.apply_filters(frame)
        
        # Resize frame first (for both color and grayscale)
        resized_color = self.resize_frame(enhanced_frame, self.width)
        
        if self.use_color:
            # Keep color information
            resized_frame = resized_color
            # Also create grayscale for character selection
            gray_resized = cv2.cvtColor(resized_color, cv2.COLOR_BGR2GRAY)
        else:
            # Convert to grayscale
            gray_resized = cv2.cvtColor(resized_color, cv2.COLOR_BGR2GRAY)
            resized_frame = gray_resized
        
        # Convert pixels to ASCII
        ascii_frame = ""
        height, width = gray_resized.shape
        
        for y in range(height):
            line = ""
            for x in range(width):
                # Get brightness for character selection
                brightness = gray_resized[y, x]
                
                # Map brightness to ASCII character (with overflow protection)
                brightness = max(0, min(255, int(brightness)))  # Clamp to 0-255 range
                char_index = int(brightness * (len(self.ascii_chars) - 1) / 255)
                char_index = max(0, min(len(self.ascii_chars) - 1, char_index))  # Clamp to valid index
                char = self.ascii_chars[char_index]
                
                if self.use_color and len(resized_frame.shape) == 3:
                    # Get color information
                    b, g, r = resized_frame[y, x]
                    color_code = self.get_color_code(r, g, b)
                    line += f"{color_code}{char}"
                else:
                    line += char
            
            ascii_frame += line + "\n"
        
        # Reset color at the end if using color
        if self.use_color:
            ascii_frame += "\033[0m"
        
        return ascii_frame
    
    def extract_audio(self, video_path, start_time=0, duration=None):
        """Extract audio from the original video"""
        if not MOVIEPY_AVAILABLE:
            return None
        
        try:
            video_clip = VideoFileClip(video_path)
            
            # Extract audio segment if specified
            if start_time > 0 or duration:
                end_time = start_time + duration if duration else video_clip.duration
                audio_clip = video_clip.subclip(start_time, end_time).audio
            else:
                audio_clip = video_clip.audio
            
            if audio_clip is None:
                print("Warning: No audio track found in the video")
                video_clip.close()
                return None
            
            # Save temporary audio file
            temp_audio_path = "temp_audio.wav"
            audio_clip.write_audiofile(temp_audio_path, verbose=False, logger=None)
            
            audio_clip.close()
            video_clip.close()
            
            return temp_audio_path
            
        except Exception as e:
            print(f"Warning: Could not extract audio: {e}")
            return None
    
    def combine_video_audio(self, video_path, audio_path, output_path):
        """Combine ASCII video with original audio"""
        if not MOVIEPY_AVAILABLE:
            print("Warning: moviepy not available, saving video without audio")
            return False
        
        try:
            # Load video and audio
            video_clip = VideoFileClip(video_path)
            audio_clip = AudioFileClip(audio_path)
            
            # Combine video and audio
            final_clip = video_clip.set_audio(audio_clip)
            
            # Write final video with audio
            final_clip.write_videofile(
                output_path, 
                codec='libx264',
                audio_codec='aac',
                verbose=False,
                logger=None
            )
            
            # Clean up
            final_clip.close()
            video_clip.close()
            audio_clip.close()
            
            return True
            
        except Exception as e:
            print(f"Error combining video and audio: {e}")
            return False
    
    def save_ascii_video(self, ascii_frames, output_path, fps, bg_color=(0, 0, 0), original_video_path=None, start_time=0, duration=None, preserve_audio=True):
        """Save ASCII frames as a video file with optional audio"""
        if not PIL_AVAILABLE:
            print("Error: Pillow not installed. Cannot save video.")
            return False
        
        if not ascii_frames:
            print("Error: No ASCII frames to save")
            return False
        
        print(f"Creating ASCII video: {output_path}")
        
        # Convert first frame to get dimensions
        first_img = self.ascii_to_image(ascii_frames[0], bg_color)
        if not first_img:
            print("Error: Could not create image from ASCII")
            return False
        
        width, height = first_img.size
        print(f"Video dimensions: {width}x{height}")
        
        # Create temporary video file (without audio)
        temp_video_path = "temp_ascii_video.mp4"
        
        # Initialize video writer with reliable codec
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        temp_video_path = temp_video_path.replace('.mp4', '.avi')  # Use AVI for reliability
        out = cv2.VideoWriter(temp_video_path, fourcc, fps, (width, height))
        
        if not out.isOpened():
            print("Error: Could not open video writer")
            return False
        
        # Convert each ASCII frame to image and write to video
        print("Rendering ASCII frames...")
        successful_frames = 0
        
        for i, ascii_frame in enumerate(ascii_frames):
            try:
                img = self.ascii_to_image(ascii_frame, bg_color)
                if img:
                    # Convert PIL image to OpenCV format (BGR)
                    img_array = np.array(img)
                    img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                    
                    # Ensure the frame has the correct dimensions
                    actual_height, actual_width = img_bgr.shape[:2]
                    if actual_height != height or actual_width != width:
                        # Resize the frame to match expected dimensions
                        img_bgr = cv2.resize(img_bgr, (width, height))
                    
                    success = out.write(img_bgr)
                    if success:
                        successful_frames += 1
                    else:
                        print(f"Warning: Failed to write frame {i+1}")
                
                if (i + 1) % 10 == 0:
                    progress = ((i + 1) / len(ascii_frames)) * 100
                    print(f"Video rendering progress: {progress:.1f}% ({successful_frames}/{i+1} frames written)")
                    
            except Exception as e:
                print(f"Warning: Failed to process frame {i+1}: {e}")
                continue
        
        out.release()
        
        print(f"Successfully wrote {successful_frames}/{len(ascii_frames)} frames to video")
        
        # Check if video was created successfully
        if successful_frames == 0:
            print("Error: No frames were successfully written to video")
            return False
        
        # Handle audio if requested and available
        if preserve_audio and original_video_path and MOVIEPY_AVAILABLE:
            print("Extracting audio from original video...")
            audio_path = self.extract_audio(original_video_path, start_time, duration)
            
            if audio_path:
                print("Combining video with audio...")
                success = self.combine_video_audio(temp_video_path, audio_path, output_path)
                
                # Clean up temporary files
                if os.path.exists(temp_video_path):
                    os.remove(temp_video_path)
                if os.path.exists(audio_path):
                    os.remove(audio_path)
                
                if success:
                    print(f"ASCII video with audio saved: {output_path}")
                    return True
                else:
                    print("Failed to combine audio, saving video without audio...")
        
        # If no audio processing or audio failed, just rename temp video
        if os.path.exists(temp_video_path):
            if os.path.exists(output_path):
                os.remove(output_path)
            os.rename(temp_video_path, output_path)
            print(f"ASCII video saved (no audio): {output_path}")
            return True
        
        return False
    
    def convert_video(self, video_path, output_file=None, play_realtime=True, start_time=0, duration=None, skip_frames=1, save_video=None):
        """Convert video to ASCII art with enhanced features"""
        # Open video file
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            print(f"Error: Could not open video file {video_path}")
            return
        
        # Get video properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Set start position if specified
        if start_time > 0:
            start_frame = int(start_time * fps)
            cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
        
        # Calculate end frame if duration is specified
        end_frame = total_frames
        if duration:
            end_frame = min(total_frames, int((start_time + duration) * fps))
        
        print(f"Processing video: {video_path}")
        print(f"FPS: {fps:.2f}, Total frames: {total_frames}")
        print(f"ASCII width: {self.width} characters")
        print(f"Quality: {self.quality}, Color: {'Yes' if self.use_color else 'No'}")
        if skip_frames > 1:
            print(f"Frame skip: {skip_frames} (processing every {skip_frames} frames)")
        
        ascii_frames = []
        frame_count = 0
        processed_count = 0
        
        # Use threading for better performance
        frame_queue = deque(maxlen=100)  # Buffer for smoother playback
        
        # Process frames
        while True:
            ret, frame = cap.read()
            if not ret or (duration and cap.get(cv2.CAP_PROP_POS_FRAMES) >= end_frame):
                break
            
            frame_count += 1
            
            # Skip frames if specified
            if frame_count % skip_frames != 0:
                continue
            
            # Convert frame to ASCII
            ascii_frame = self.frame_to_ascii(frame)
            ascii_frames.append(ascii_frame)
            processed_count += 1
            
            if processed_count % 10 == 0:  # Progress update
                progress = (frame_count / (end_frame - (start_time * fps if start_time > 0 else 0))) * 100
                print(f"Processed {processed_count} frames ({progress:.1f}%)")
        
        cap.release()
        
        # Save to file if specified
        if output_file:
            print(f"Saving ASCII art to {output_file}")
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"Video: {video_path}\n")
                f.write(f"Dimensions: {self.width} chars wide\n")
                f.write(f"Quality: {self.quality}\n")
                f.write(f"Color: {'Yes' if self.use_color else 'No'}\n")
                f.write("="*50 + "\n\n")
                
                for i, ascii_frame in enumerate(ascii_frames):
                    f.write(f"Frame {i+1}:\n")
                    f.write(ascii_frame)
                    f.write("\n" + "="*self.width + "\n\n")
        
        # Save as video if requested
        if save_video:
            video_fps = fps / skip_frames
            self.save_ascii_video(
                ascii_frames, 
                save_video, 
                video_fps, 
                getattr(self, 'bg_color', (0, 0, 0)),
                video_path,
                start_time,
                duration,
                getattr(self, 'preserve_audio', True)
            )
        
        # Play in real-time if requested
        if play_realtime:
            self.play_ascii_animation(ascii_frames, fps / skip_frames)
        
        return ascii_frames
    
    def play_ascii_animation(self, ascii_frames, fps):
        """Play ASCII animation with better performance"""
        print(f"\nPlaying ASCII animation at {fps:.1f} FPS")
        print("Controls: Ctrl+C to stop, Space to pause (if supported)")
        time.sleep(2)
        
        try:
            frame_delay = 1.0 / fps
            for i, ascii_frame in enumerate(ascii_frames):
                start_time = time.time()
                
                # Clear screen
                if os.name == 'nt':  # Windows
                    os.system('cls')
                else:  # Unix/Linux/MacOS
                    print('\033[2J\033[H', end='')
                
                # Display frame with info
                print(f"Frame {i+1}/{len(ascii_frames)} | FPS: {fps:.1f}")
                print(ascii_frame, end='')
                
                # Maintain frame rate
                elapsed = time.time() - start_time
                sleep_time = max(0, frame_delay - elapsed)
                if sleep_time > 0:
                    time.sleep(sleep_time)
                    
        except KeyboardInterrupt:
            print("\n\nPlayback stopped by user")
        except Exception as e:
            print(f"\nPlayback error: {e}")

def main():
    parser = argparse.ArgumentParser(
        description="Enhanced Video to ASCII Art Converter with Color Support",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python video_to_ascii.py video.mp4                    # Basic conversion
  python video_to_ascii.py video.mp4 --color            # With colors
  python video_to_ascii.py video.mp4 -w 120 --quality high  # High quality
  python video_to_ascii.py video.mp4 --start 30 --duration 10  # 10 seconds from 30s mark
  python video_to_ascii.py video.mp4 --skip 2           # Process every 2nd frame
        """
    )
    
    parser.add_argument("video_file", help="Path to the video file")
    parser.add_argument("--width", "-w", type=int, default=80, 
                       help="Width of ASCII output in characters (default: 80)")
    parser.add_argument("--color", "-c", action="store_true",
                       help="Enable color output (requires colorama)")
    parser.add_argument("--quality", "-q", choices=['low', 'medium', 'high', 'ultra'], 
                       default='medium', help="ASCII quality level (default: medium)")
    parser.add_argument("--output", "-o", type=str, 
                       help="Output file to save ASCII art as text")
    parser.add_argument("--save-video", type=str,
                       help="Save ASCII art as video file (e.g., output.mp4)")
    parser.add_argument("--no-play", action="store_true", 
                       help="Don't play the ASCII animation in real-time")
    parser.add_argument("--start", "-s", type=float, default=0,
                       help="Start time in seconds (default: 0)")
    parser.add_argument("--duration", "-d", type=float,
                       help="Duration to process in seconds (default: entire video)")
    parser.add_argument("--skip", type=int, default=1,
                       help="Process every Nth frame (default: 1, process all frames)")
    parser.add_argument("--bg-color", type=str, default="black",
                       choices=['black', 'white', 'dark-gray', 'light-gray'],
                       help="Background color for video export (default: black)")
    parser.add_argument("--no-audio", action="store_true",
                       help="Don't preserve audio when saving video")
    parser.add_argument("--audio-only", action="store_true",
                       help="Extract and save only the audio track")
    
    args = parser.parse_args()
    
    # Validate arguments
    if not os.path.exists(args.video_file):
        print(f"Error: Video file '{args.video_file}' not found")
        sys.exit(1)
    
    if args.color and not COLORAMA_AVAILABLE:
        print("Warning: colorama not available, disabling color mode")
        args.color = False
    
    if args.width < 10 or args.width > 300:
        print("Warning: Width should be between 10 and 300 characters")
        args.width = max(10, min(300, args.width))
    
    if args.skip < 1:
        print("Error: Skip value must be at least 1")
        sys.exit(1)
    
    if args.save_video and not PIL_AVAILABLE:
        print("Error: Pillow not installed. Cannot save video.")
        print("Install with: pip install Pillow")
        sys.exit(1)
    
    if (args.save_video and not args.no_audio) and not MOVIEPY_AVAILABLE:
        print("Warning: moviepy not installed. Video will be saved without audio.")
        print("Install with: pip install moviepy")
    
    if args.audio_only and not MOVIEPY_AVAILABLE:
        print("Error: moviepy not installed. Cannot extract audio.")
        print("Install with: pip install moviepy")
        sys.exit(1)
    
    # Convert background color
    bg_colors = {
        'black': (0, 0, 0),
        'white': (255, 255, 255),
        'dark-gray': (64, 64, 64),
        'light-gray': (192, 192, 192)
    }
    bg_color = bg_colors.get(args.bg_color, (0, 0, 0))
    
    # Handle audio-only extraction
    if args.audio_only:
        print("Extracting audio only...")
        try:
            converter = VideoToASCII()  # Minimal initialization
            audio_output = args.video_file.rsplit('.', 1)[0] + '_audio.wav'
            audio_path = converter.extract_audio(args.video_file, args.start, args.duration)
            if audio_path:
                if os.path.exists(audio_output):
                    os.remove(audio_output)
                os.rename(audio_path, audio_output)
                print(f"Audio extracted to: {audio_output}")
            else:
                print("Failed to extract audio")
                sys.exit(1)
        except Exception as e:
            print(f"Error extracting audio: {e}")
            sys.exit(1)
        return
    
    # Create converter and process video
    print("Initializing Enhanced Video to ASCII Converter...")
    converter = VideoToASCII(
        width=args.width, 
        use_color=args.color,
        quality=args.quality
    )
    
    # Set audio preservation preference
    converter.preserve_audio = not args.no_audio
    converter.bg_color = bg_color
    
    try:
        converter.convert_video(
            args.video_file, 
            output_file=args.output,
            play_realtime=not args.no_play,
            start_time=args.start,
            duration=args.duration,
            skip_frames=args.skip,
            save_video=args.save_video
        )
        print("\nConversion completed successfully!")
        
        if args.save_video:
            audio_status = "with audio" if (not args.no_audio and MOVIEPY_AVAILABLE) else "without audio"
            print(f"ASCII video saved to: {args.save_video} ({audio_status})")
        
    except Exception as e:
        print(f"Error during conversion: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()