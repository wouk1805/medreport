# audio_chunks_manager.py
# ============================================================================
# Audio Chunks Management - WAV file saving
# ============================================================================

import os
from scipy.io.wavfile import write
from datetime import datetime
import io
import base64
from config import SAMPLE_RATE

class AudioChunksManager:
    """Simple manager for saving audio chunks as WAV files"""
    
    def __init__(self, audio_dir="audio"):
        self.audio_dir = audio_dir
        self.session_id = None
        self.chunk_counter = 0
        self.session_started = False
        self.ensure_audio_directory()
    
    def ensure_audio_directory(self):
        """Create audio directory if it doesn't exist"""
        if not os.path.exists(self.audio_dir):
            os.makedirs(self.audio_dir)
            print(f"📁 Created audio directory: {self.audio_dir}")
    
    def start_new_session(self):
        """Start a new recording session"""
        if self.session_started:
            print(f"⚠️ Session already started: {self.session_id}")
            return self.session_id
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_id = f"session_{timestamp}"
        self.chunk_counter = 0
        self.session_started = True
        
        # Create session subdirectory
        session_dir = os.path.join(self.audio_dir, self.session_id)
        if not os.path.exists(session_dir):
            os.makedirs(session_dir)
            print(f"📁 Created session directory: {session_dir}")
        
        print(f"🎬 Started new audio session: {self.session_id}")
        return self.session_id
    
    def save_chunk_as_wav(self, chunk_array, sample_rate=SAMPLE_RATE):
        """
        Save audio chunk as WAV file and return base64
        
        Returns:
            tuple: (base64_data, wav_file_path)
        """
        # Create base64 for debugging
        bio = io.BytesIO()
        write(bio, sample_rate, chunk_array)
        bio.seek(0)
        audio_bytes = bio.read()
        audio_b64_raw = base64.b64encode(audio_bytes).decode('utf-8')
        base64_data = f"data:audio/wav;base64,{audio_b64_raw}"
        
        # Only save WAV file if session is properly started
        if not self.session_started or self.session_id is None:
            print("⚠️ No active session - chunk not saved to WAV")
            return base64_data, None
        
        # Increment chunk counter
        self.chunk_counter += 1
        
        # Generate filename and path
        chunk_filename = f"chunk_{self.chunk_counter:04d}.wav"
        session_dir = os.path.join(self.audio_dir, self.session_id)
        wav_file_path = os.path.join(session_dir, chunk_filename)
        
        try:
            # Save as WAV file
            write(wav_file_path, sample_rate, chunk_array)
            
            # Log chunk info
            chunk_duration = len(chunk_array) / sample_rate
            print(f"💾 Saved chunk {self.chunk_counter}: {chunk_duration:.1f}s → {wav_file_path}")
            
            return base64_data, wav_file_path
            
        except Exception as e:
            print(f"❌ Error saving chunk {self.chunk_counter}: {e}")
            return base64_data, None
    
    def end_session(self):
        """End current recording session"""
        if self.session_started and self.session_id:
            print(f"🏁 Ended audio session: {self.session_id} ({self.chunk_counter} chunks saved)")
        
        # Reset all session state
        self.session_id = None
        self.chunk_counter = 0
        self.session_started = False
    
    def get_session_info(self):
        """Get current session information for debugging"""
        return {
            'session_id': self.session_id,
            'chunk_counter': self.chunk_counter,
            'is_active': self.session_started,
            'session_dir': os.path.join(self.audio_dir, self.session_id) if self.session_id else None
        }