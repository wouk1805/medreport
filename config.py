# config.py
# ============================================================================
# Configuration and Constants
# ============================================================================

# AUDIO CONFIGURATION
SAMPLE_RATE = 16000
CHANNELS = 1
CHUNK_SECONDS = 10      # X-second chunk length
SEND_INTERVAL = 8       # Send new chunk every X seconds

# APPLICATION SETTINGS
APP_TITLE = "MedReport"
APP_VERSION = "3.3"
WINDOW_WIDTH = 1500
WINDOW_HEIGHT = 800
APP_ICON_PATH = "resources/main_icon.ico"

# COLOR PALETTE
COLORS = {
    # Cool neutral backgrounds
    'bg_primary': '#F8F9FB',          # Cool white
    'bg_secondary': '#F6F7F8',        # Light cool gray
    'bg_card': '#FFFFFF',             # Pure white
    'bg_surface': '#F9FAFB',          # Subtle cool tint
    'bg_hover': '#F1F3F4',            # Cool hover
    'bg_glass': '#FFFFFF',            # Glass white
    
    # Cool gray primary
    'primary': '#475569',             # Slate gray
    'primary_light': '#64748B',       # Light slate
    'primary_dark': '#334155',        # Dark slate
    'gradient_start': '#52525B',      # Cool gray
    'gradient_end': '#71717A',        # Light cool gray
    
    # Cool sophisticated accents
    'accent_success': '#059669',      # Cool emerald
    'accent_generate': '#10B981',     # Softer, more muted green
    'accent_warning': '#D97706',      # Warm amber contrast
    'accent_danger': '#DC2626',       # Clean red
    'accent_info': '#0284C7',         # Sky blue
    'accent_purple': '#7C3AED',       # Cool violet
    'accent_pink': '#DB2777',         # Cool pink
    'accent_teal': '#0F766E',         # Cool teal
    'accent_orange': '#EA580C',       # Warm orange contrast
    'accent_cyan': '#0891B2',         # Cool cyan
    'accent_yellow': '#DAA520',       # Goldenrod
    
    # Cool text hierarchy
    'text_primary': '#1E293B',        # Cool dark
    'text_secondary': '#475569',      # Cool medium
    'text_muted': '#94A3B8',          # Cool light
    'text_white': '#FFFFFF',          # Pure white
    'text_accent': '#475569',         # Slate accent
    
    # Cool borders and effects
    'border': '#E2E8F0',              # Cool border
    'border_light': '#F1F5F9',        # Light cool border
    'border_focus': '#CBD5E1',        # Cool focus
    'shadow_light': '#F8FAFC',        # Cool shadow
    'shadow_medium': '#E2E8F0',       # Medium cool shadow
    
    # Cool interactive states
    'focus_ring': '#E2E8F0',          # Cool focus ring
    'selection': '#F1F5F9',           # Cool selection
}

# GRADIENT WAVE COLORS
WAVE_COLORS = [
    '#A78BFA',
    '#818CF8',
    '#60A5FA',
    '#22D3EE',
    '#34D399',
    '#FBBF24',
    '#F472B6',
]

# REPORT TYPES AND LANGUAGES
REPORT_TYPES = ["General", "Narrative", "Custom"]
REPORT_TYPE_DEFAULT = REPORT_TYPES[0]
LANGUAGES = ["English", "French", "Spanish", "German", "Italian", "Portuguese", "Chinese", "Japanese", "Korean", "Russian"]

# ANIMATION SETTINGS
WAVE_ANIMATION_DELAY = 40  # milliseconds
TIMER_UPDATE_DELAY = 1000  # milliseconds
STATUS_ANIMATION_DELAY = 200  # milliseconds

# UI DIMENSIONS
WAVE_CANVAS_HEIGHT = 240
TEXT_AREA_HEIGHT = 14
TOTAL_WAVE_BARS = 7

# AUDIO SENSITIVITY SETTINGS
VOLUME_SENSITIVITY = 0.03  # RMS normalization factor
AUDIO_DECAY_RATE = 0.6     # How fast audio levels decay when silent
LEVEL_SMOOTHING = 0.8      # Audio level smoothing factor

# APP METADATA
APP_DESCRIPTION = "Generate your medical report from a real-time audio recording in just a few minutes"

# INITIAL UI TEXT CONTENT
WELCOME_TEXT = f"""✨ Welcome to {APP_TITLE}, powered by Gemma 3n!


        🚀 Next-generation medical transcription powered by advanced AI

        🎯 Real-time processing with professional accuracy

        📊 Intelligent analysis and reporting capabilities

        🔒 100% confidential and secure — all data is processed locally with no internet transmission, ensuring complete privacy


➡️ Click 'START' to begin capturing your medical consultation with real-time AI transcription!"""

ANALYSIS_WELCOME_TEXT = """🤖 Structured Medical Report


        🚀 Advanced medical intelligence ready to activate

        📊 Professional report generation in multiple formats

        🌍 Multi-language support with contextual understanding

        ✨ Real-time insights and intelligent summarization

        💊 Automatically generate adapted prescriptions based on analysis


🎙️ Start recording to unlock powerful AI capabilities!"""

RECORDING_ACTIVE_TEXT = """🎙️ Recording Active


        ✨ Speak clearly into your microphone

        🔄 Transcription will appear in real time

        🚀 AI analysis will be available when you stop recording"""

CLEARED_TEXT = """✨ Transcription cleared


Ready for new recording!


➡️ Click 'START' to begin capturing your medical consultation with real-time AI transcription!"""

TIPS_TEXT = """• Speak clearly at normal pace
• Minimize background noise"""