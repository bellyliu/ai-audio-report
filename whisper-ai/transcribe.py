#!/usr/bin/env python3
"""
Audio Transcription App using OpenAI Whisper
Supports multiple audio formats and output formats including SRT, VTT, TXT, JSON, and TSV
"""

import whisper
import os
import argparse
import json
import sys
from pathlib import Path
from datetime import timedelta
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WhisperTranscriber:
    """A class to handle audio transcription using OpenAI Whisper"""
    
    def __init__(self, model_size="base"):
        """
        Initialize the transcriber
        
        Args:
            model_size (str): Whisper model size ('tiny', 'base', 'small', 'medium', 'large')
        """
        self.model_size = model_size
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load the Whisper model"""
        try:
            logger.info(f"Loading Whisper model: {self.model_size}")
            self.model = whisper.load_model(self.model_size)
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            sys.exit(1)
    
    def transcribe_audio(self, audio_path, language=None, task="transcribe"):
        """
        Transcribe audio file
        
        Args:
            audio_path (str): Path to audio file
            language (str): Language code (e.g., 'en', 'es', 'fr')
            task (str): 'transcribe' or 'translate'
        
        Returns:
            dict: Whisper transcription result
        """
        try:
            logger.info(f"Transcribing: {audio_path}")
            
            options = {"task": task}
            if language:
                options["language"] = language
            
            result = self.model.transcribe(audio_path, **options)
            logger.info("Transcription completed successfully")
            return result
        
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return None
    
    def save_txt(self, result, output_path):
        """Save transcription as plain text"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(result['text'].strip())
            logger.info(f"TXT saved: {output_path}")
        except Exception as e:
            logger.error(f"Failed to save TXT: {e}")
    
    def save_srt(self, result, output_path):
        """Save transcription as SRT subtitle file"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                for i, segment in enumerate(result['segments'], 1):
                    start_time = self._format_timestamp(segment['start'])
                    end_time = self._format_timestamp(segment['end'])
                    text = segment['text'].strip()
                    
                    f.write(f"{i}\n")
                    f.write(f"{start_time} --> {end_time}\n")
                    f.write(f"{text}\n\n")
            logger.info(f"SRT saved: {output_path}")
        except Exception as e:
            logger.error(f"Failed to save SRT: {e}")
    
    def save_vtt(self, result, output_path):
        """Save transcription as VTT subtitle file"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("WEBVTT\n\n")
                for segment in result['segments']:
                    start_time = self._format_timestamp_vtt(segment['start'])
                    end_time = self._format_timestamp_vtt(segment['end'])
                    text = segment['text'].strip()
                    
                    f.write(f"{start_time} --> {end_time}\n")
                    f.write(f"{text}\n\n")
            logger.info(f"VTT saved: {output_path}")
        except Exception as e:
            logger.error(f"Failed to save VTT: {e}")
    
    def save_json(self, result, output_path):
        """Save transcription as JSON with detailed information"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            logger.info(f"JSON saved: {output_path}")
        except Exception as e:
            logger.error(f"Failed to save JSON: {e}")
    
    def save_tsv(self, result, output_path):
        """Save transcription as TSV (Tab-Separated Values)"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("start\tend\ttext\n")
                for segment in result['segments']:
                    start = f"{segment['start']:.2f}"
                    end = f"{segment['end']:.2f}"
                    text = segment['text'].strip().replace('\t', ' ')
                    f.write(f"{start}\t{end}\t{text}\n")
            logger.info(f"TSV saved: {output_path}")
        except Exception as e:
            logger.error(f"Failed to save TSV: {e}")
    
    def _format_timestamp(self, seconds):
        """Format timestamp for SRT format"""
        td = timedelta(seconds=seconds)
        hours, remainder = divmod(td.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)
        milliseconds = int((seconds % 1) * 1000)
        return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d},{milliseconds:03d}"
    
    def _format_timestamp_vtt(self, seconds):
        """Format timestamp for VTT format"""
        td = timedelta(seconds=seconds)
        hours, remainder = divmod(td.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)
        milliseconds = int((seconds % 1) * 1000)
        return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}.{milliseconds:03d}"

def main():
    """Main function to handle command line arguments and run transcription"""
    parser = argparse.ArgumentParser(description="Transcribe audio using OpenAI Whisper")
    parser.add_argument("audio_file", help="Path to audio file")
    parser.add_argument("--model", "-m", default="base", 
                       choices=["tiny", "base", "small", "medium", "large"],
                       help="Whisper model size (default: base)")
    parser.add_argument("--language", "-l", help="Language code (e.g., en, es, fr)")
    parser.add_argument("--task", "-t", default="transcribe", 
                       choices=["transcribe", "translate"],
                       help="Task: transcribe or translate to English (default: transcribe)")
    parser.add_argument("--output", "-o", help="Output directory (default: same as input file)")
    parser.add_argument("--formats", "-f", nargs="+", 
                       choices=["txt", "srt", "vtt", "json", "tsv"],
                       default=["txt", "srt", "vtt", "json", "tsv"],
                       help="Output formats (default: all formats)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Validate input file
    audio_path = Path(args.audio_file)
    if not audio_path.exists():
        logger.error(f"Audio file not found: {audio_path}")
        sys.exit(1)
    
    # Set output directory
    if args.output:
        output_dir = Path(args.output)
        output_dir.mkdir(parents=True, exist_ok=True)
    else:
        output_dir = audio_path.parent
    
    # Initialize transcriber
    transcriber = WhisperTranscriber(args.model)
    
    # Transcribe audio
    result = transcriber.transcribe_audio(str(audio_path), args.language, args.task)
    
    if result is None:
        logger.error("Transcription failed")
        sys.exit(1)
    
    # Generate output filename base
    base_name = audio_path.stem
    
    # Save in requested formats
    format_methods = {
        'txt': transcriber.save_txt,
        'srt': transcriber.save_srt,
        'vtt': transcriber.save_vtt,
        'json': transcriber.save_json,
        'tsv': transcriber.save_tsv
    }
    
    for format_name in args.formats:
        output_path = output_dir / f"{base_name}.{format_name}"
        format_methods[format_name](result, str(output_path))
    
    # Print summary
    print(f"\n=== Transcription Summary ===")
    print(f"Audio file: {audio_path}")
    print(f"Model: {args.model}")
    print(f"Language: {result.get('language', 'auto-detected')}")
    print(f"Task: {args.task}")
    print(f"Duration: {result.get('duration', 'unknown')} seconds")
    print(f"Output formats: {', '.join(args.formats)}")
    print(f"Output directory: {output_dir}")
    print("\nTranscription completed successfully!")

if __name__ == "__main__":
    main()