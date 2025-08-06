# animation_manager.py
# ============================================================================
# Animation Management
# ============================================================================

import time
import math
from config import WAVE_COLORS, WAVE_ANIMATION_DELAY, TOTAL_WAVE_BARS
from color_utils import lighten_color

class AnimationManager:
    """Manages wave animations only"""
    
    def __init__(self, root, audio_engine):
        self.root = root
        self.audio_engine = audio_engine
        self.animation_running = False
        self.wave_canvas = None
        self.wave_animation_active = False
    
    def start_animations(self):
        """Start wave animation loop"""
        self.animation_running = True
        self.start_wave_animation()
        print("✅ Animation manager started")
    
    def stop_animations(self):
        """Stop all animations"""
        self.animation_running = False
        self.wave_animation_active = False
        print("⏹️ Animation manager stopped")
    
    def set_wave_canvas(self, canvas):
        """Set the canvas for wave animations"""
        self.wave_canvas = canvas
        print("🎨 Wave canvas set for animations")
    
    def start_wave_animation(self):
        """Start the wave animation loop"""
        if self.animation_running:
            self.wave_animation_active = True
            self._draw_wave_frame()
    
    def _draw_wave_frame(self):
        """Draw a single frame of the wave animation"""
        if not self.wave_animation_active or not self.wave_canvas:
            return
        
        try:
            self.draw_futuristic_waves()
            
            # Schedule next frame
            if self.animation_running:
                self.root.after(WAVE_ANIMATION_DELAY, self._draw_wave_frame)
                
        except Exception as e:
            print(f"❌ Wave animation error: {e}")
            # Continue animation despite errors
            if self.animation_running:
                self.root.after(WAVE_ANIMATION_DELAY, self._draw_wave_frame)
    
    def draw_futuristic_waves(self):
        """Draw futuristic audio wave visualization"""
        if not self.wave_canvas:
            return
        
        canvas = self.wave_canvas
        canvas.delete("waves")
        
        width = canvas.winfo_width()
        height = canvas.winfo_height()
        
        if width <= 1 or height <= 1:
            return
        
        # Get audio levels from engine
        audio_levels = []
        if self.audio_engine and hasattr(self.audio_engine, 'get_audio_levels'):
            try:
                audio_levels = self.audio_engine.get_audio_levels()
            except Exception as e:
                print(f"⚠️ Error getting audio levels: {e}")
                audio_levels = [0.0] * TOTAL_WAVE_BARS
        else:
            audio_levels = [0.0] * TOTAL_WAVE_BARS
        
        # Enhanced bar dimensions
        total_bars = TOTAL_WAVE_BARS
        bar_width = max(16, (width - 120) // total_bars)
        spacing = 12
        start_x = (width - (total_bars * bar_width + (total_bars - 1) * spacing)) // 2
        max_height = height - 60
        center_y = height // 2
        
        # Check if recording for different visualization modes
        is_recording = False
        if self.audio_engine and hasattr(self.audio_engine, 'is_recording'):
            try:
                is_recording = self.audio_engine.is_recording
            except:
                is_recording = False
        
        if is_recording:
            # Active recording visualization
            self._draw_active_waves(canvas, audio_levels, total_bars, bar_width, spacing, start_x, max_height, center_y)
        else:
            # Idle animation
            self._draw_idle_waves(canvas, total_bars, bar_width, spacing, start_x, center_y)
    
    def _draw_active_waves(self, canvas, audio_levels, total_bars, bar_width, spacing, start_x, max_height, center_y):
        """Draw active recording wave visualization"""
        for i in range(total_bars):
            level = audio_levels[i] if i < len(audio_levels) else 0.0
            
            if level > 0.005:
                bar_height = max(int(level * max_height * 0.8), 8)
            else:
                bar_height = 6
            
            x = start_x + i * (bar_width + spacing)
            y_top = center_y - bar_height // 2
            y_bottom = center_y + bar_height // 2
            
            color = WAVE_COLORS[i % len(WAVE_COLORS)]
            
            # Glow effect for high levels
            if level > 0.2:
                glow_color = lighten_color(color, 0.7)
                canvas.create_rectangle(
                    x - 3, y_top - 3, x + bar_width + 3, y_bottom + 3,
                    fill=glow_color, outline="", tags="waves"
                )
            
            # Main bar
            canvas.create_rectangle(
                x, y_top, x + bar_width, y_bottom,
                fill=color, outline="", tags="waves"
            )
            
            # Inner highlight
            if bar_height > 12:
                highlight_color = lighten_color(color, 0.4)
                canvas.create_rectangle(
                    x + 3, y_top + 3, x + bar_width - 3, y_top + max(bar_height // 4, 6),
                    fill=highlight_color, outline="", tags="waves"
                )
            
            # Energy pulse for high levels
            if level > 0.6:
                pulse_size = int(level * 8)
                pulse_color = lighten_color(color, 0.8)
                canvas.create_oval(
                    x + bar_width//2 - pulse_size, center_y - pulse_size,
                    x + bar_width//2 + pulse_size, center_y + pulse_size,
                    fill="", outline=pulse_color, width=2, tags="waves"
                )
    
    def _draw_idle_waves(self, canvas, total_bars, bar_width, spacing, start_x, center_y):
        """Draw idle animation waves"""
        time_factor = time.time() * 2.0
        
        for i in range(total_bars):
            base_height = 8
            wave_height = base_height + 20 * (math.sin(time_factor + i * 0.7) * 0.5 + 0.5)
            
            x = start_x + i * (bar_width + spacing)
            y_top = center_y - wave_height // 2
            y_bottom = center_y + wave_height // 2
            
            color = WAVE_COLORS[i % len(WAVE_COLORS)]
            idle_color = lighten_color(color, 0.8)
            
            canvas.create_rectangle(
                x, y_top, x + bar_width, y_bottom,
                fill=idle_color, outline="", tags="waves"
            )
            
            if wave_height > 15:
                glow_color = lighten_color(idle_color, 0.5)
                canvas.create_rectangle(
                    x - 1, y_top - 1, x + bar_width + 1, y_bottom + 1,
                    fill="", outline=glow_color, width=1, tags="waves"
                )
    
    def animate_status(self, status_label, message, color):
        """Simple direct status update"""
        if not status_label:
            return
        
        # Direct update
        status_label.config(text=message, fg=color)
        status_label.update_idletasks()
        print(f"📊 Simple status update: {message}")
    
    def cleanup(self):
        """Cleanup animation manager"""
        self.stop_animations()
        self.wave_canvas = None
        print("🧹 Animation manager cleaned up")