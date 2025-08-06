# audio_manager.py
# ============================================================================
# Audio UI Management and Controls
# ============================================================================

import tkinter as tk
from tkinter import ttk
from config import COLORS

class AudioUIManager:
    """Manages the audio recording UI components and interactions"""
    
    def __init__(self, audio_engine, ui_callbacks):
        self.audio_engine = audio_engine
        self.ui_callbacks = ui_callbacks
        
        # UI components (will be set by parent)
        self.record_button = None
        self.timer_label = None
        self.status_label = None
        self.wave_canvas = None
        
        # State tracking
        self.chronometer_running = False
    
    def create_audio_section(self, parent, section_font, create_button_tooltip_func):
        """Create the complete audio recording section"""
        # Audio visualization frame
        audio_frame = tk.Frame(parent, bg=COLORS['bg_card'], relief='flat', bd=0)
        audio_frame.pack(side='left', fill='both', expand=True, padx=(0, 15))
        
        # Shadow effect
        audio_shadow = tk.Frame(parent, height=2, bg=COLORS['shadow_light'])
        audio_shadow.place(in_=audio_frame, relx=0, rely=1, relwidth=1)
        
        # Header with recording controls
        audio_header = tk.Frame(audio_frame, bg=COLORS['bg_card'])
        audio_header.pack(fill='x', padx=20, pady=(25, 10))
        
        # Title
        audio_title_container = tk.Frame(audio_header, bg=COLORS['bg_card'])
        audio_title_container.pack(side='left')
        
        tk.Label(audio_title_container, text="🎵", font=("Segoe UI", 18),
                 bg=COLORS['bg_card'], fg=COLORS['accent_orange']).pack(side='left', padx=(0, 10))
        
        audio_title = tk.Label(audio_title_container, text="Audio Recorder", font=section_font,
                              bg=COLORS['bg_card'], fg=COLORS['text_primary'])
        audio_title.pack(side='left')
        
        # Recording controls
        controls_container = tk.Frame(audio_header, bg=COLORS['bg_card'])
        controls_container.pack(side='right', padx=(0, 20))
        
        # Record button
        self.record_button = ttk.Button(controls_container, text="START", width=8,
                                      command=self.on_record_click, style="CompactRecording.TButton")
        self.record_button.pack(side='left')
        self.record_button.configure(cursor='hand2')
        create_button_tooltip_func(self.record_button, "Start audio recording")
        
        # Audio wave canvas
        from config import WAVE_CANVAS_HEIGHT
        self.wave_canvas = tk.Canvas(audio_frame, height=WAVE_CANVAS_HEIGHT, bg=COLORS['bg_surface'],
                                highlightthickness=0, relief='flat', bd=0)
        self.wave_canvas.pack(fill='x', padx=20, pady=(15, 10))
        
        # Bottom status area
        status_area = tk.Frame(audio_frame, bg=COLORS['bg_card'])
        status_area.pack(fill='x', padx=20, pady=(15, 15))
        
        # Timer
        timer_container = tk.Frame(status_area, bg=COLORS['bg_surface'], relief='flat', bd=0)
        timer_container.pack(side='left')
        
        tk.Label(timer_container, text="⏱️", font=("Segoe UI", 12),
                 bg=COLORS['bg_surface'], fg=COLORS['primary']).pack(side='left', padx=(10, 5))
        
        self.timer_label = tk.Label(timer_container, text="00:00", font=("Segoe UI", 16),
                                  bg=COLORS['bg_surface'], fg=COLORS['text_secondary'])
        self.timer_label.pack(side='left', padx=(0, 10))
        
        # Status
        self.status_label = tk.Label(status_area, text="Initialization...", font=("Segoe UI", 12),
                                   bg=COLORS['bg_card'], fg=COLORS['text_secondary'])
        self.status_label.pack(side='right')
        
        # Tips section
        self.create_tips_section(audio_frame)
        
        return audio_frame
    
    def create_tips_section(self, parent):
        """Create tips section for audio recording"""
        from config import TIPS_TEXT
        
        tips_section = tk.Frame(parent, bg=COLORS['bg_card'], relief='flat', bd=0)
        tips_section.pack(fill='x', padx=20, pady=(10, 15))
        
        # Header
        tips_header = tk.Frame(tips_section, bg=COLORS['bg_card'])
        tips_header.pack(fill='x')
        
        tk.Label(tips_header, text="💡 Pro Tips", font=("Segoe UI", 12),
                 bg=COLORS['bg_card'], fg=COLORS['text_secondary']).pack(anchor='w', padx=20, pady=8)
        
        # Tips content
        tips_content = tk.Frame(tips_section, bg=COLORS['bg_card'])
        tips_content.pack(fill='x', padx=20, pady=(0, 10))
        
        tk.Label(tips_content, text=TIPS_TEXT, font=("Segoe UI", 9), justify='left',
                 bg=COLORS['bg_card'], fg=COLORS['text_muted']).pack(anchor='w')
    
    def on_record_click(self):
        """Handle record button click"""
        if hasattr(self.ui_callbacks, 'on_record_click'):
            self.ui_callbacks.on_record_click()
        else:
            # Fallback to direct handling
            self._handle_record_click()
    
    def _handle_record_click(self):
        """Direct handling of record button click"""
        if not self.audio_engine.is_recording:
            self.start_recording()
        else:
            self.stop_recording()
    
    def start_recording(self):
        """Start recording process"""
        print("🎬 Starting recording from audio manager...")
        
        # Update button appearance
        self.record_button.config(text="STOP", style="CompactStop.TButton")
        self.update_status("Starting...", COLORS['accent_info'])
        
        if self.audio_engine.start_recording():
            self.update_status("Recording", COLORS['accent_danger'])
            self.start_chronometer()
            print("✅ Recording started successfully")
            return True
        else:
            # Revert UI if start failed
            self.record_button.config(text="START", style="CompactRecording.TButton")
            self.update_status("Failed to start", COLORS['accent_danger'])
            return False
    
    def stop_recording(self):
        """Stop recording process"""
        print("🛑 Stopping recording from audio manager...")
        
        # Update button appearance
        self.record_button.config(text="START", style="CompactRecording.TButton")
        self.update_status("Finalizing...", COLORS['accent_warning'])
        
        if self.audio_engine.stop_recording():
            self.stop_chronometer()
            print("✅ Stop initiated")
            return True
        else:
            print("❌ Failed to stop recording")
            return False
    
    def start_chronometer(self):
        """Start the chronometer timer"""
        print("⏰ Starting chronometer...")
        self.chronometer_running = True
        self.timer_label.config(text="00:00", fg=COLORS['text_secondary'])
        self._update_chronometer()
    
    def stop_chronometer(self):
        """Stop the chronometer timer"""
        print("⏹️ Stopping chronometer")
        self.chronometer_running = False
    
    def reset_chronometer(self):
        """Reset the chronometer to 00:00"""
        print("🔄 Resetting chronometer to 00:00")
        self.chronometer_running = False
        if self.timer_label:
            self.timer_label.config(text="00:00", fg=COLORS['text_secondary'])
            self.timer_label.update_idletasks()
        if self.status_label:
            self.status_label.config(text="Ready", fg=COLORS['accent_success'])
            self.status_label.update_idletasks()
    
    def _update_chronometer(self):
        """Update chronometer display"""
        try:
            if self.chronometer_running and self.audio_engine and self.audio_engine.is_recording:
                elapsed = self.audio_engine.get_recording_elapsed_time()
                
                if elapsed >= 0:
                    minutes = elapsed // 60
                    seconds = elapsed % 60
                    timer_text = f"{minutes:02d}:{seconds:02d}"
                    
                    # Color coding based on duration
                    if elapsed > 300:  # 5 minutes
                        color = COLORS['accent_danger']
                    elif elapsed > 60:  # 1 minute
                        color = COLORS['accent_warning']
                    else:
                        color = COLORS['text_secondary']
                    
                    if self.timer_label:
                        self.timer_label.config(text=timer_text, fg=color)
                    
                    # Schedule next update
                    if hasattr(self.ui_callbacks, 'schedule_ui_update'):
                        self.ui_callbacks.schedule_ui_update(lambda: self._schedule_next_update())
                    else:
                        self._schedule_next_update()
                else:
                    self._schedule_next_update()
            else:
                print("⏹️ Recording stopped - chronometer stopped")
                self.chronometer_running = False
                
        except Exception as e:
            print(f"❌ Chronometer error: {e}")
            if self.chronometer_running:
                self._schedule_next_update()
    
    def _schedule_next_update(self):
        """Schedule the next chronometer update"""
        if self.chronometer_running:
            if hasattr(self.ui_callbacks, 'root') and self.ui_callbacks.root:
                self.ui_callbacks.root.after(1000, self._update_chronometer)
    
    def update_status(self, message, color=COLORS['text_secondary']):
        """Update the status label directly"""
        if self.status_label:
            self.status_label.config(text=message, fg=color)
            self.status_label.update_idletasks()
            print(f"📊 Audio status: {message}")
    
    def get_wave_canvas(self):
        """Get the wave canvas for animation"""
        return self.wave_canvas
    
    def reset_ui_state(self):
        """Reset UI to initial state"""
        if self.record_button:
            self.record_button.config(text="START", style="CompactRecording.TButton")
        
        if self.timer_label:
            self.timer_label.config(text="00:00", fg=COLORS['text_secondary'])
        
        if self.status_label:
            self.status_label.config(text="Ready", fg=COLORS['accent_success'])
        
        self.chronometer_running = False
        print("🔄 Audio UI state reset")
    
    def cleanup(self):
        """Cleanup audio UI manager"""
        self.chronometer_running = False
        print("🧹 Audio UI manager cleaned up")