# main.py
# ============================================================================
# Main Application Entry Point
# ============================================================================

import tkinter as tk
import signal
import sys
from audio import AudioEngine
from ui import UIManager
from config import *

class App:
    """Main application class"""
    
    def __init__(self):
        print(f"🚀 Initializing {APP_TITLE}...")
        
        # Create main window
        self.root = tk.Tk()
        
        # Setup graceful shutdown handling
        self.setup_shutdown_handlers()
        
        # Setup UI callbacks for audio engine
        self.ui_callbacks = {
            'update_status': self.update_status_callback,
            'append_transcription': self.append_transcription_callback,
            'schedule_ui_update': self.schedule_ui_update_callback
        }
        
        # Initialize audio engine
        print("🎙️ Initializing audio engine...")
        self.audio_engine = AudioEngine(self.ui_callbacks)
        
        # Initialize UI manager
        print("🎨 Initializing UI manager...")
        self.ui_manager = UIManager(self.root, self.audio_engine)
        
        # Connect callbacks
        self.setup_callbacks()
        
        print(f"✅ {APP_TITLE} initialized successfully")
    
    def setup_shutdown_handlers(self):
        """Setup graceful shutdown for different exit scenarios"""
        def signal_handler(sig, frame):
            print("\n🛑 Shutdown signal received")
            self.graceful_shutdown()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        self.root.protocol("WM_DELETE_WINDOW", self.on_window_close)
    
    def setup_callbacks(self):
        """Setup callback connections between components"""
        # Update UI callbacks to use UI manager methods
        self.ui_callbacks['update_status'] = self.ui_manager.update_status
        self.ui_callbacks['append_transcription'] = self.ui_manager.append_transcription
        self.ui_callbacks['schedule_ui_update'] = self.ui_manager.schedule_ui_update
        
        print("🔗 Callbacks connected successfully")
    
    def update_status_callback(self, message, color, animation_type):
        """Thread-safe callback wrapper for status updates"""
        def update():
            self.ui_manager.update_status(message, color, animation_type)
        
        self.root.after(0, update)
    
    def append_transcription_callback(self, text):
        """Thread-safe callback wrapper for transcription updates"""
        def update():
            self.ui_manager.append_transcription(text)
        
        self.root.after(0, update)
    
    def schedule_ui_update_callback(self, callback):
        """Thread-safe UI update scheduling"""
        self.root.after(0, callback)
    
    def on_window_close(self):
        """Handle window close event gracefully"""
        print("🪟 Window close requested")
        self.graceful_shutdown()
        self.root.destroy()
    
    def graceful_shutdown(self):
        """Perform graceful shutdown of all components"""
        print("🛑 Initiating graceful shutdown...")
        
        try:
            # Stop recording if active
            if hasattr(self.audio_engine, 'is_recording') and self.audio_engine.is_recording:
                print("⏹️ Stopping active recording...")
                self.audio_engine.stop_recording()
            
            # Shutdown audio engine
            if hasattr(self.audio_engine, 'shutdown'):
                print("🔇 Shutting down audio engine...")
                self.audio_engine.shutdown()
            
            print("✅ Graceful shutdown complete")
            
        except Exception as e:
            print(f"⚠️ Error during shutdown: {e}")
    
    def run(self):
        """Start the application main loop"""
        try:
            print(f"🎬 Starting {APP_TITLE} main loop...")
            
            # Setup final window configuration
            self.root.after(100, self.ui_manager.setup_centered_layout)
            
            # Print configuration summary
            print(f"🔧 CONFIGURATION SUMMARY:")
            print(f"   Chunk Size: {CHUNK_SECONDS}s every {SEND_INTERVAL}s")
            print(f"   Sample Rate: {SAMPLE_RATE}Hz, Channels: {CHANNELS}")
            
            # Start the main event loop
            print(f"🌟 {APP_TITLE} is ready!")
            self.root.mainloop()
            
        except KeyboardInterrupt:
            print("\n🛑 Application interrupted by user")
            self.graceful_shutdown()
        except Exception as e:
            print(f"❌ Application error: {e}")
            self.graceful_shutdown()
        finally:
            print(f"👋 {APP_TITLE} closed gracefully")

def main():
    """Application entry point"""
    try:
        print(f"🎯 Starting {APP_TITLE} v{APP_VERSION}")
        print("=" * 60)
        
        app = App()
        app.run()
        
    except ImportError as e:
        print(f"💥 Missing dependency: {e}")
        print("Please install required packages:")
        print("pip install sounddevice scipy numpy requests tkinter")
        return 1
    except Exception as e:
        print(f"💥 Failed to start {APP_TITLE}: {e}")
        return 1
    
    print("✅ Application exited cleanly")
    return 0

if __name__ == "__main__":
    sys.exit(main())