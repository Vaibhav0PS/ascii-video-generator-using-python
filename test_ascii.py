#!/usr/bin/env python3
"""
Simple test script for ASCII video conversion
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from video_to_ascii import VideoToASCII

def test_simple_conversion(video_file):
    """Test basic ASCII conversion without video export"""
    print("Testing basic ASCII conversion...")
    
    converter = VideoToASCII(width=40, use_color=False, quality='low')
    
    try:
        # Convert just a few frames for testing
        ascii_frames = converter.convert_video(
            video_file,
            play_realtime=False,
            duration=2,  # Only 2 seconds
            skip_frames=5  # Every 5th frame for speed
        )
        
        if ascii_frames:
            print(f"✅ Successfully converted {len(ascii_frames)} frames")
            print("Sample frame:")
            print(ascii_frames[0][:200] + "..." if len(ascii_frames[0]) > 200 else ascii_frames[0])
            return True
        else:
            print("❌ No frames converted")
            return False
            
    except Exception as e:
        print(f"❌ Error during conversion: {e}")
        return False

def test_video_export(video_file):
    """Test video export with minimal settings"""
    print("\nTesting video export...")
    
    converter = VideoToASCII(width=30, use_color=False, quality='low')
    
    try:
        # Convert and save a very short video
        converter.convert_video(
            video_file,
            play_realtime=False,
            duration=1,  # Only 1 second
            skip_frames=10,  # Every 10th frame
            save_video="test_output.mp4"
        )
        
        if os.path.exists("test_output.mp4"):
            file_size = os.path.getsize("test_output.mp4")
            print(f"✅ Video created successfully: test_output.mp4 ({file_size} bytes)")
            return True
        else:
            print("❌ Video file was not created")
            return False
            
    except Exception as e:
        print(f"❌ Error during video export: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python test_ascii.py <video_file>")
        sys.exit(1)
    
    video_file = sys.argv[1]
    
    if not os.path.exists(video_file):
        print(f"Error: Video file '{video_file}' not found")
        sys.exit(1)
    
    print(f"Testing with video: {video_file}")
    
    # Test basic conversion first
    basic_success = test_simple_conversion(video_file)
    
    if basic_success:
        # Test video export
        video_success = test_video_export(video_file)
        
        if video_success:
            print("\n🎉 All tests passed! The converter is working correctly.")
        else:
            print("\n⚠️  Basic conversion works, but video export has issues.")
    else:
        print("\n❌ Basic conversion failed. Check your video file and dependencies.")