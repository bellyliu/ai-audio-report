# Whisper Audio Transcription App

A Python command-line application that leverages OpenAI's Whisper model to transcribe audio files to text with high accuracy.

## Features

- 🎵 **Multiple Audio Formats**: Supports MP3, WAV, FLAC, M4A, AAC, OGG, WMA, MP4, AVI, MOV, WebM
- 🧠 **Multiple Whisper Models**: tiny, base, small, medium, large (trade-off between speed and accuracy)
- 🌍 **Language Support**: Auto-detection or specify language codes (en, es, fr, etc.)
- 📝 **Multiple Output Formats**: TXT, SRT, VTT, JSON, TSV
- 🔄 **Translation**: Can translate to English from any supported language
- 💻 **Command-line Interface**: Simple and powerful command-line tool
- 🚀 **Easy Installation**: Simple pip install process

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Install Python Dependencies

```bash
# Navigate to the project directory
cd whisper-ai

# Install required packages
pip install -r requirements.txt
```

### Optional: Install FFmpeg (for additional audio format support)

**macOS (using Homebrew):**

```bash
brew install ffmpeg
```

**Ubuntu/Debian:**

```bash
sudo apt update
sudo apt install ffmpeg
```

**Windows:**
Download from [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)

_Note: FFmpeg is optional. Whisper can handle most common audio formats without it._

## Usage

### Command Line Interface

```bash
# Basic usage - transcribe with default settings
python transcribe.py audio_file.mp3

# Specify model size for better accuracy (but slower)
python transcribe.py audio_file.mp3 --model large

# Specify language for better performance
python transcribe.py audio_file.mp3 --language en

# Choose specific output formats
python transcribe.py audio_file.mp3 --formats txt srt json

# Translate to English from any language
python transcribe.py audio_file.mp3 --task translate

# Specify output directory
python transcribe.py audio_file.mp3 --output /path/to/output

# Enable verbose output for debugging
python transcribe.py audio_file.mp3 --verbose

# Test with the included sample file
python transcribe.py eng-opem.flac --model tiny
```

### Command Line Options

- `audio_file`: Path to the audio file (required)
- `--model, -m`: Whisper model size (tiny, base, small, medium, large) - default: base
- `--language, -l`: Language code (e.g., en, es, fr) - optional, auto-detect if not specified
- `--task, -t`: Task type (transcribe, translate) - default: transcribe
- `--output, -o`: Output directory - default: same as input file
- `--formats, -f`: Output formats (txt, srt, vtt, json, tsv) - default: all formats
- `--verbose, -v`: Enable verbose output

### Quick Test

To quickly test the installation, you can use the included sample audio file:

```bash
# Run a quick test with the sample file
python example_test.py

# Or test directly with the transcribe script
python transcribe.py eng-opem.flac --model tiny --formats txt
```

## Whisper Models

| Model  | Size     | Speed   | Accuracy | Use Case                 |
| ------ | -------- | ------- | -------- | ------------------------ |
| tiny   | ~39 MB   | Fastest | Lowest   | Quick testing, real-time |
| base   | ~74 MB   | Fast    | Good     | General purpose          |
| small  | ~244 MB  | Medium  | Better   | Better accuracy needed   |
| medium | ~769 MB  | Slow    | High     | High accuracy required   |
| large  | ~1550 MB | Slowest | Best     | Maximum accuracy         |

## Output Formats

- **TXT**: Plain text transcription
- **SRT**: Subtitle format with timestamps
- **VTT**: WebVTT subtitle format
- **JSON**: Complete transcription data with segments and metadata
- **TSV**: Tab-separated values with timestamps

## Examples

### Example 1: Basic Transcription

```bash
python transcribe.py sample_audio.mp3
```

Output files:

- `sample_audio.txt`
- `sample_audio.srt`
- `sample_audio.vtt`
- `sample_audio.json`
- `sample_audio.tsv`

### Example 2: Spanish to English Translation

```bash
python transcribe.py spanish_audio.mp3 --language es --task translate --formats txt json
```

### Example 3: High Accuracy Transcription

```bash
python transcribe.py important_meeting.wav --model large --formats txt srt json
```

### Example 4: Quick Test with Sample File

```bash
python transcribe.py eng-opem.flac --model tiny --verbose
```

## Integration with Your Flask App

You can easily integrate the transcriber into your existing Flask application:

```python
from whisper_ai.transcribe import WhisperTranscriber

# Initialize transcriber
transcriber = WhisperTranscriber(model_size="base")

# Transcribe audio
result = transcriber.transcribe_audio("path/to/audio.mp3")

# Save in different formats
transcriber.save_txt(result, "output.txt")
transcriber.save_srt(result, "output.srt")
transcriber.save_json(result, "output.json")
```

## Performance Tips

1. **Choose the right model**: Use `tiny` or `base` for real-time applications, `large` for maximum accuracy
2. **Specify language**: If you know the language, specify it to improve accuracy and speed
3. **Use appropriate hardware**: Whisper runs faster on GPUs if available
4. **Start small**: Test with the `tiny` model first, then upgrade to larger models as needed

## Troubleshooting

### Common Issues

1. **Import Error**: Make sure all dependencies are installed:

   ```bash
   pip install -r requirements.txt
   ```

2. **Memory Issues**: Use smaller models (tiny, base) for large files or limited memory

3. **Slow Performance**:
   - Use smaller models for faster processing
   - Ensure you have adequate RAM
   - Consider using GPU acceleration

### Error Messages

- **"Import whisper could not be resolved"**: Install openai-whisper with pip
- **"File too large"**: Use smaller audio files or split large files
- **"CUDA out of memory"**: Use a smaller model or CPU processing

## Testing Installation

Run the test script to verify everything is working:

```bash
python test_installation.py
```

This will test:

- Package imports
- Whisper model loading
- Basic transcription functionality

## Dependencies

- **openai-whisper**: Core Whisper model
- **torch**: PyTorch for deep learning
- **torchaudio**: Audio processing
- **numpy**: Numerical operations

## License

This project uses OpenAI's Whisper model. Please refer to OpenAI's usage policies and the Whisper license for commercial use.

## Support

For support and questions, please check the troubleshooting section above or review the error messages for guidance.
