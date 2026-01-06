# Enhanced Video to ASCII Art Converter 🎬➡️🎨

A powerful Python script that converts video files into ASCII art animations with **full color support** and advanced features.

## ✨ Features

- 🌈 **Full Color Support** - RGB colors mapped to 256-color ANSI codes
- 🎯 **Multiple Quality Levels** - From basic ASCII to Unicode block characters
- ⚡ **Performance Optimized** - Frame skipping and buffering for smooth playback
- 🎬 **Video Segment Processing** - Convert specific time ranges
- 📁 **File Export** - Save ASCII art with metadata
- 🎥 **Video Export** - Save ASCII art as MP4 video files with audio
- 🎵 **Audio Support** - Preserve original audio tracks in exported videos
- 🖥️ **Cross-Platform** - Works on Windows, macOS, and Linux
- 🎮 **Real-time Playback** - Watch ASCII animations at original FPS

## 🚀 Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Or install manually
pip install opencv-python numpy colorama Pillow moviepy
```

## 📖 Usage Examples

### Basic conversion:
```bash
python video_to_ascii.py video.mp4
```

### With colors (recommended):
```bash
python video_to_ascii.py video.mp4 --color
```

### High quality with colors:
```bash
python video_to_ascii.py video.mp4 --color --quality high --width 120
```

### Process specific segment:
```bash
python video_to_ascii.py video.mp4 --start 30 --duration 10 --color
```

### Fast processing (every 3rd frame):
```bash
python video_to_ascii.py video.mp4 --skip 3 --color
```

### Save to text file:
```bash
python video_to_ascii.py video.mp4 --color --output my_ascii_art.txt --no-play
```

### Save as video with audio:
```bash
python video_to_ascii.py video.mp4 --color --save-video ascii_video.mp4 --no-play
```

### Create high-quality ASCII video:
```bash
python video_to_ascii.py video.mp4 --color --quality high --save-video output.mp4 --width 120
```

### Extract audio only:
```bash
python video_to_ascii.py video.mp4 --audio-only --start 30 --duration 10
```

### Create silent ASCII video:
```bash
python video_to_ascii.py video.mp4 --color --save-video silent.mp4 --no-audio --no-play
```

## 🎛️ Command Line Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--color` | `-c` | Enable full RGB color output | False |
| `--width` | `-w` | ASCII art width in characters | 80 |
| `--quality` | `-q` | Quality: low/medium/high/ultra | medium |
| `--output` | `-o` | Save to text file | None |
| `--save-video` | | Save as MP4 video file with audio | None |
| `--bg-color` | | Background color for video export | black |
| `--no-audio` | | Don't preserve audio in video export | False |
| `--audio-only` | | Extract and save only the audio track | False |
| `--no-play` | | Skip real-time playback | False |
| `--start` | `-s` | Start time in seconds | 0 |
| `--duration` | `-d` | Duration to process (seconds) | Full video |
| `--skip` | | Process every Nth frame | 1 |

## 🎨 Quality Levels

| Level | Characters | Best For |
|-------|------------|----------|
| **low** | `@#*+=-:. ` | Fast processing, simple output |
| **medium** | `@%#*+=-:. ` | Balanced quality and speed |
| **high** | `█▉▊▋▌▍▎▏ ` | Detailed output, Unicode blocks |
| **ultra** | `██▓▒░▒▓██` | Maximum detail, special effects |

## 🌈 Color Features

The color mode uses ANSI 256-color codes to display:
- **RGB mapping** - Full color spectrum support
- **Grayscale optimization** - Smart black/white handling  
- **Terminal compatibility** - Works with most modern terminals
- **Performance optimized** - Efficient color code generation

## 🎵 Audio Features

Preserve and manipulate audio from original videos:
- **Audio Preservation** - Automatically extracts and combines original audio
- **Audio Synchronization** - Maintains perfect sync with ASCII video
- **Audio-Only Export** - Extract just the audio track as WAV file
- **Segment Audio** - Extract audio from specific time ranges
- **No Audio Option** - Create silent ASCII videos when desired

## 🔧 How It Works

1. **Video Processing** - OpenCV extracts and enhances frames
2. **Image Enhancement** - Contrast/brightness adjustment and noise reduction
3. **Intelligent Resizing** - Maintains aspect ratio with character compensation
4. **Color Analysis** - RGB values mapped to ANSI color codes
5. **ASCII Mapping** - Brightness levels converted to character density
6. **Real-time Display** - Smooth playback with frame rate control

## 📋 Supported Formats

Works with any format OpenCV supports:
- **Video**: MP4, AVI, MOV, MKV, WMV, FLV, WebM
- **Codecs**: H.264, H.265, VP9, AV1, and more

## 💡 Pro Tips

### Performance
- Use `--skip 2` or `--skip 3` for faster processing of long videos
- Lower width (40-60) for real-time playback on slower systems
- Use `--no-play` for batch processing multiple videos

### Visual Quality  
- Enable `--color` for dramatically better results
- Use `--quality high` for detailed scenes
- Try `--width 100-150` for larger displays
- Dark terminal themes work best with ASCII art

### Specific Use Cases
```bash
# Movie trailer preview (first 30 seconds)
python video_to_ascii.py trailer.mp4 --duration 30 --color --quality high

# Quick preview (every 5th frame)
python video_to_ascii.py long_video.mp4 --skip 5 --color --width 60

# High quality export
python video_to_ascii.py video.mp4 --color --quality ultra --width 150 --output masterpiece.txt --no-play
```

## 🎯 Advanced Examples

### Create ASCII art from webcam:
```bash
# First record a short clip, then convert
python video_to_ascii.py webcam_clip.mp4 --color --quality high
```

### Batch process multiple videos:
```bash
# Create text versions of all MP4 files
for file in *.mp4; do
    python video_to_ascii.py "$file" --color --output "${file%.mp4}_ascii.txt" --no-play
done

# Create ASCII video versions with audio
for file in *.mp4; do
    python video_to_ascii.py "$file" --color --save-video "${file%.mp4}_ascii.mp4" --no-play
done
```

### Audio processing examples:
```bash
# Extract audio from specific segment
python video_to_ascii.py movie.mp4 --audio-only --start 120 --duration 30

# Create ASCII video with white background and no audio
python video_to_ascii.py video.mp4 --color --save-video clean.mp4 --bg-color white --no-audio

# High quality ASCII with preserved audio
python video_to_ascii.py video.mp4 --color --quality ultra --save-video hq_with_audio.mp4 --width 150
```

## 🐛 Troubleshooting

- **No color output**: Install colorama with `pip install colorama`
- **No audio in exported video**: Install moviepy with `pip install moviepy`
- **Audio sync issues**: Ensure original video has valid audio track
- **Slow playback**: Reduce width or increase skip value
- **Garbled output**: Ensure terminal supports UTF-8 and 256 colors
- **Memory issues**: Process shorter segments using `--duration`
- **Audio extraction fails**: Check if video has audio track, try different format

## 🎪 Fun Examples

Try these for impressive results:
- Animated movies (great contrast and colors)
- Music videos (dynamic scenes)
- Nature documentaries (rich colors)
- Classic black & white films (perfect for ASCII)

---

**Made with ❤️ for terminal art enthusiasts**