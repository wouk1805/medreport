# audio.py
# ============================================================================
# Audio Engine and Processing
# ============================================================================

import sounddevice as sd
import numpy as np
import threading
import time
import math
import queue
import asyncio
from config import *
from audio_chunks_manager import AudioChunksManager
from local_model_manager import LocalModelManager

class AudioEngine:
    def __init__(self, ui_callbacks):
        self.ui_callbacks = ui_callbacks
        self.is_recording = False
        self.audio_buffer = np.empty((0, CHANNELS), dtype='int16')
        self.lock = threading.Lock()
        self.last_sent_time = 0
        self.recording_start_time = 0
        self.chunks_sent = 0
        self.audio_levels = [0.0] * TOTAL_WAVE_BARS
        self.sender_thread = None
        
        # Chunking tracking
        self.last_sent_sample_count = 0
        
        # Transcript management
        self.chunk_transcripts = []
        
        # Processing queue for local models
        self.processing_queue = queue.Queue()
        
        # Initialize audio chunks manager
        self.chunks_manager = AudioChunksManager()
        
        # Initialize local model manager with proper UI callbacks
        print("🤖 Initializing local Gemma 3n models...")
        model_ui_callbacks = {
            'update_status': ui_callbacks.get('update_status'),
            'on_models_ready': ui_callbacks.get('on_models_ready'),
            'schedule_ui_update': ui_callbacks.get('schedule_ui_update')
        }
        self.model_manager = LocalModelManager(model_ui_callbacks)
        
        # Start loading models in background
        threading.Thread(target=self._load_models_background, daemon=True).start()
        
        # Setup audio stream
        self.stream = sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype='int16',
            callback=self.audio_callback,
        )
        
        # Start background worker
        self.start_background_worker()
    
    def _load_models_background(self):
        """Load models in background thread"""
        try:
            print("🔄 Starting background model loading...")
            self.model_manager.load_models()
            print("✅ Background model loading completed")
        except Exception as e:
            print(f"❌ Background model loading failed: {e}")
            # Notify UI of loading failure
            if 'schedule_ui_update' in self.ui_callbacks:
                def update_error():
                    if 'update_status' in self.ui_callbacks:
                        self.ui_callbacks['update_status']("Model loading failed", COLORS.get('accent_danger', '#DC2626'), "static")
                
                self.ui_callbacks['schedule_ui_update'](update_error)
    
    def start_background_worker(self):
        """Start background worker thread for model processing"""
        self.processing_worker = threading.Thread(target=self._processing_worker, daemon=True)
        self.processing_worker.start()
    
    def _processing_worker(self):
        """Background worker for local model processing"""
        while True:
            try:
                task = self.processing_queue.get(timeout=1)
                if task is None:
                    break
                
                if task['type'] == 'transcription':
                    self._process_chunk_async(task['chunk'], task['wav_path'])
                elif task['type'] == 'final_chunk':
                    self._process_final_chunk_async(task['chunk'], task['wav_path'])
                elif task['type'] == 'cleanup':
                    self._perform_cleanup_async()
                    
            except queue.Empty:
                continue
            except Exception as e:
                print(f"❌ Processing worker error: {e}")
    
    def audio_callback(self, indata, frames, time_info, status):
        """Audio callback for recording"""
        if self.is_recording:
            with self.lock:
                self.audio_buffer = np.vstack((self.audio_buffer, indata.copy()))
                
                # Audio visualization
                mono_audio = np.mean(indata, axis=1) if len(indata.shape) > 1 else indata.flatten()
                
                if len(mono_audio) > 0:
                    rms = np.sqrt(np.mean(mono_audio ** 2))
                    normalized_volume = min(rms / VOLUME_SENSITIVITY, 1.0)
                    
                    new_levels = []
                    for i in range(TOTAL_WAVE_BARS):
                        time_offset = time.time() * 12 + i * 1.2
                        frequency_factor = 0.5 + 0.8 * (math.sin(time_offset) * 0.5 + 0.5)
                        bar_level = normalized_volume * frequency_factor
                        
                        current_val = self.audio_levels[i] if i < len(self.audio_levels) else 0
                        smoothed = current_val * (1 - LEVEL_SMOOTHING) + bar_level * LEVEL_SMOOTHING
                        new_levels.append(min(smoothed, 1.0))
                    
                    self.audio_levels = new_levels
                else:
                    self.audio_levels = [val * AUDIO_DECAY_RATE for val in self.audio_levels]
    
    def _process_chunk_async(self, chunk_array, wav_file_path):
        """Process chunk with local transcription model"""
        try:
            chunk_duration = len(chunk_array) / SAMPLE_RATE
            print(f"🎙️ Processing chunk locally: {chunk_duration:.1f}s")
            
            # Check if model manager is available and models are loaded
            if not hasattr(self, 'model_manager') or self.model_manager is None:
                print("❌ Model manager not available")
                return
            
            # Run async transcription in new event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                transcription = loop.run_until_complete(
                    self.model_manager.transcribe_audio_chunk(wav_file_path)
                )
            finally:
                loop.close()
            
            self.chunks_sent += 1
            elapsed = int(time.time() - self.recording_start_time)
            
            # Store chunk transcript
            if transcription.strip() and not transcription.startswith('[Transcription Error'):
                self.chunk_transcripts.append(transcription.strip())
                print(f"📝 Chunk {self.chunks_sent}: {len(transcription)} chars • {elapsed}s")
                print(f"📋 Content: {transcription[:50]}..." if len(transcription) > 50 else f"📋 Content: {transcription}")
                
                # Update UI with chunk transcript
                def update_ui():
                    if 'update_status' in self.ui_callbacks:
                        self.ui_callbacks['update_status']("Processing", COLORS.get('accent_orange', '#F59E0B'), "animate")
                    if 'append_transcription' in self.ui_callbacks:
                        self.ui_callbacks['append_transcription'](transcription)
                
                if 'schedule_ui_update' in self.ui_callbacks:
                    self.ui_callbacks['schedule_ui_update'](update_ui)
            else:
                print(f"⚠️ Chunk {self.chunks_sent}: transcription failed or empty")
                
        except Exception as e:
            print(f"❌ Chunk processing exception: {e}")
            def update_error():
                if 'update_status' in self.ui_callbacks:
                    self.ui_callbacks['update_status']("❌ Processing error", COLORS.get('accent_danger', '#DC2626'), "error")
                if 'append_transcription' in self.ui_callbacks:
                    self.ui_callbacks['append_transcription'](f"[Processing Error]: {str(e)}")
            
            if 'schedule_ui_update' in self.ui_callbacks:
                self.ui_callbacks['schedule_ui_update'](update_error)
    
    def _process_final_chunk_async(self, chunk_array, wav_file_path):
        """Process final chunk with local transcription"""
        try:
            print(f"📤 Final chunk: {len(chunk_array)} samples")
            self._process_chunk_async(chunk_array, wav_file_path)
            
            # End the session after the final chunk is processed
            self.chunks_manager.end_session()
            
            def signal_complete():
                if 'update_status' in self.ui_callbacks:
                    self.ui_callbacks['update_status']("Complete", COLORS.get('accent_success', '#059669'), "animate")
            
            if 'schedule_ui_update' in self.ui_callbacks:
                self.ui_callbacks['schedule_ui_update'](signal_complete)
            
        except Exception as e:
            print(f"❌ Final chunk error: {e}")
            self.chunks_manager.end_session()
    
    def periodic_send(self):
        """Send chunks periodically for real-time transcription"""
        chunk_samples = int(CHUNK_SECONDS * SAMPLE_RATE)
        
        while self.is_recording:
            current_time = time.time()
            if current_time - self.last_sent_time >= SEND_INTERVAL:
                with self.lock:
                    total_samples = self.audio_buffer.shape[0]
                    
                    if total_samples > self.last_sent_sample_count:
                        new_samples_available = total_samples - self.last_sent_sample_count
                        
                        if new_samples_available >= chunk_samples:
                            start_idx = total_samples - chunk_samples
                            chunk = self.audio_buffer[start_idx:total_samples].copy()
                            self.last_sent_sample_count = total_samples
                            
                            print(f"📤 Sending chunk for local processing: samples {start_idx}-{total_samples}")
                            
                        elif new_samples_available > 0 and (current_time - self.recording_start_time) >= 2.0:
                            start_idx = self.last_sent_sample_count
                            chunk = self.audio_buffer[start_idx:total_samples].copy()
                            self.last_sent_sample_count = total_samples
                            
                            print(f"📤 Sending partial chunk: samples {start_idx}-{total_samples}")
                        else:
                            chunk = None
                    else:
                        chunk = None
                
                if chunk is not None:
                    # Save chunk as WAV file
                    audio_b64, wav_file_path = self.chunks_manager.save_chunk_as_wav(chunk, SAMPLE_RATE)
                    
                    if wav_file_path:
                        self.processing_queue.put({
                            'type': 'transcription',
                            'chunk': chunk,
                            'wav_path': wav_file_path
                        })
                        self.last_sent_time = current_time
                    
            time.sleep(0.1)
    
    def start_recording(self):
        """Start recording with proper session management"""
        if self.is_recording:
            return False
            
        print("🎙️ Starting recording...")
        
        # Start new audio chunks session
        session_id = self.chunks_manager.start_new_session()
        print(f"🎬 Audio session started: {session_id}")
        
        self.is_recording = True
        self.chunks_sent = 0
        self.audio_levels = [0.0] * TOTAL_WAVE_BARS
        self.recording_start_time = time.time()
        
        # Reset transcripts
        self.last_sent_sample_count = 0
        self.chunk_transcripts = []
        
        with self.lock:
            self.audio_buffer = np.empty((0, CHANNELS), dtype='int16')
        self.last_sent_time = time.time() - SEND_INTERVAL
        
        try:
            self.stream.start()
            self.sender_thread = threading.Thread(target=self.periodic_send, daemon=True)
            self.sender_thread.start()
            
            print("✅ Recording started with local transcription")
            return True
        except Exception as e:
            print(f"❌ Failed to start: {e}")
            self.is_recording = False
            self.chunks_manager.end_session()
            return False
    
    def stop_recording(self):
        """Stop recording and end session"""
        if not self.is_recording:
            return False
            
        print("🛑 Stopping recording...")
        self.is_recording = False
        self.audio_levels = [0.0] * TOTAL_WAVE_BARS
        
        if 'update_status' in self.ui_callbacks:
            self.ui_callbacks['update_status']("Finalizing...", COLORS.get('accent_warning', '#F59E0B'), "animate")
        
        self.processing_queue.put({'type': 'cleanup'})
        
        return True
    
    def _perform_cleanup_async(self):
        """Cleanup and process final chunk if needed"""
        try:
            # Process final chunk if any remaining audio
            with self.lock:
                total_samples = self.audio_buffer.shape[0]
                remaining_samples = total_samples - self.last_sent_sample_count
                
                print(f"🔍 Cleanup: {remaining_samples} remaining samples")
                
                if remaining_samples > int(0.3 * SAMPLE_RATE):
                    remaining_chunk = self.audio_buffer[self.last_sent_sample_count:total_samples].copy()
                    
                    # Save final chunk as WAV
                    audio_b64, wav_file_path = self.chunks_manager.save_chunk_as_wav(remaining_chunk, SAMPLE_RATE)
                    
                    if wav_file_path:
                        self.processing_queue.put({
                            'type': 'final_chunk',
                            'chunk': remaining_chunk,
                            'wav_path': wav_file_path
                        })
                else:
                    # No final chunk, end session now
                    self.chunks_manager.end_session()
                    def signal_complete():
                        if 'update_status' in self.ui_callbacks:
                            self.ui_callbacks['update_status']("Complete", COLORS.get('accent_success', '#059669'), "animate")
                    
                    if 'schedule_ui_update' in self.ui_callbacks:
                        self.ui_callbacks['schedule_ui_update'](signal_complete)
            
            # Stop audio stream
            try:
                self.stream.stop()
                print("🔇 Audio stream stopped")
            except Exception as e:
                print(f"❌ Error stopping stream: {e}")
            
            # Wait for sender thread
            if self.sender_thread and self.sender_thread.is_alive():
                self.sender_thread.join(timeout=2)
            
        except Exception as e:
            print(f"❌ Cleanup error: {e}")
            self.chunks_manager.end_session()
    
    def get_recording_elapsed_time(self):
        """Get elapsed time"""
        if self.is_recording and self.recording_start_time > 0:
            return int(time.time() - self.recording_start_time)
        return 0
    
    def get_audio_levels(self):
        """Get audio levels"""
        return self.audio_levels.copy()
    
    def get_full_transcription(self):
        """Get combined transcription from all chunks"""
        return " ".join(self.chunk_transcripts)
    
    def shutdown(self):
        """Shutdown with model cleanup"""
        try:
            if self.chunks_manager.get_session_info()['is_active']:
                self.chunks_manager.end_session()
            
            # Cleanup local models
            if hasattr(self, 'model_manager') and self.model_manager:
                self.model_manager.cleanup()
            
            self.processing_queue.put(None)
            if hasattr(self, 'stream'):
                self.stream.close()
                
            print("🧹 Audio engine shutdown complete")
        except Exception as e:
            print(f"❌ Shutdown error: {e}")


class LocalReportGenerator:
    """Local report generation using fine-tuned Gemma 3n model"""
    
    @staticmethod
    def generate_report(transcription_text, report_type, language, ui_callbacks, custom_format=None, attachment=None, model_manager=None):
        """Generate medical report using local Gemma 3n model"""
        def make_local_report():
            try:
                if not transcription_text.strip():
                    print("⚠️ No transcript for report generation")
                    def update_no_content():
                        if 'update_generate_status' in ui_callbacks:
                            ui_callbacks['update_generate_status']("No transcript available", COLORS.get('accent_warning', '#F59E0B'))
                        if 'stop_generate_animation' in ui_callbacks:
                            ui_callbacks['stop_generate_animation']()
                        if 're_enable_button' in ui_callbacks:
                            ui_callbacks['re_enable_button']()
                    
                    if 'schedule_ui_update' in ui_callbacks:
                        ui_callbacks['schedule_ui_update'](update_no_content)
                    return
                
                if not model_manager:
                    print("❌ No model manager available")
                    def update_no_manager():
                        if 'update_generate_status' in ui_callbacks:
                            ui_callbacks['update_generate_status']("Model manager not available", COLORS.get('accent_danger', '#DC2626'))
                        if 'stop_generate_animation' in ui_callbacks:
                            ui_callbacks['stop_generate_animation']()
                        if 're_enable_button' in ui_callbacks:
                            ui_callbacks['re_enable_button']()
                    
                    if 'schedule_ui_update' in ui_callbacks:
                        ui_callbacks['schedule_ui_update'](update_no_manager)
                    return
                
                print("🤖 LOCAL REPORT GENERATION")
                print("=" * 50)
                print(f"📊 Report Type: {report_type}")
                print(f"🌍 Language: {language}")
                print(f"📝 Input Length: {len(transcription_text)} characters")
                
                if custom_format:
                    print(f"🎨 Custom Format: {len(custom_format)} characters")
                
                if attachment and attachment.strip():
                    print(f"📎 Attachment: {len(attachment)} characters")
                
                print("-" * 50)
                
                # Run async report generation
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                try:
                    report = loop.run_until_complete(
                        model_manager.generate_medical_report(
                            transcription_text, report_type, language, attachment
                        )
                    )
                finally:
                    loop.close()
                
                print("✅ LOCAL REPORT SUCCESS")
                print(f"📄 Output: {len(report)} chars")
                print("=" * 50)
                
                def update_success():
                    if 'display_summary' in ui_callbacks:
                        ui_callbacks['display_summary'](report, is_final_result=True)
                    if 'stop_generate_animation' in ui_callbacks:
                        ui_callbacks['stop_generate_animation']()
                
                if 'schedule_ui_update' in ui_callbacks:
                    ui_callbacks['schedule_ui_update'](update_success)
                    
            except Exception as e:
                print(f"❌ Local Report Exception: {e}")
                def update_exception():
                    # Truncate error for status display
                    truncated_error = f"Generation error: {str(e)[:20]}..." if len(str(e)) > 20 else f"Generation error: {str(e)}"
                    if 'update_generate_status' in ui_callbacks:
                        ui_callbacks['update_generate_status'](truncated_error, COLORS.get('accent_danger', '#DC2626'))
                    if 'stop_generate_animation' in ui_callbacks:
                        ui_callbacks['stop_generate_animation']()
                    if 're_enable_button' in ui_callbacks:
                        ui_callbacks['re_enable_button']()
                
                if 'schedule_ui_update' in ui_callbacks:
                    ui_callbacks['schedule_ui_update'](update_exception)
        
        # Show loading message
        loading_text = f"🚀 Generating {report_type.lower()} report in {language}...\n\n✨ AI is analyzing your content with advanced medical understanding.\n\n⏳This may take 30-60 seconds for comprehensive analysis."
        if custom_format:
            loading_text = f"🎨 Generating custom report in {language}...\n\n✨ Using your custom format template.\n\n⏳This may take 30-60 seconds for comprehensive analysis."
        
        if attachment and attachment.strip():
            loading_text += f"\n\n📎 Including imported document in analysis..."
        
        if 'display_summary' in ui_callbacks:
            ui_callbacks['display_summary'](loading_text)
        if 'start_generate_animation' in ui_callbacks:
            ui_callbacks['start_generate_animation']()
        
        report_thread = threading.Thread(target=make_local_report, daemon=True)
        report_thread.start()