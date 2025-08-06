# ui.py
# ============================================================================
# User Interface Components
# ============================================================================

import tkinter as tk
from tkinter import ttk, scrolledtext, Canvas, font
import os
from datetime import datetime
from config import *

from rich_text_widget import RichTextWidget
from pdf_generator import rich_text_to_pdf_with_dialog

from color_utils import lighten_color, darken_color
from file_operations import FileOperationsManager
from audio_manager import AudioUIManager
from animation_manager import AnimationManager
from prescription_manager import PrescriptionManager

class UIManager:
    def __init__(self, root, audio_engine):
        self.root = root
        self.audio_engine = audio_engine
        self.current_transcription = ""
        self.is_generating_report = False
        
        # Initialize managers
        self.file_manager = FileOperationsManager()
        self.audio_ui_manager = AudioUIManager(audio_engine, self)
        self.animation_manager = AnimationManager(root, audio_engine)
        self.prescription_manager = None  # Will be initialized when analysis section is created
        
        # Setup fonts
        self.setup_fonts()
        
        # Setup styles
        self.setup_styles()
        
        # Setup main window
        self.setup_window()
        
        # Create UI components
        self.create_ui()
        
        # Start animations
        self.animation_manager.start_animations()
        
        # Track model loading state
        self.models_ready = False
    
    def on_models_ready(self):
        """Called when models are successfully loaded"""
        self.models_ready = True
        # Only show ready status if models actually loaded successfully
        self.root.after(100, lambda: self.update_status("Ready", COLORS['accent_success'], "animate"))
    
    def setup_fonts(self):
        """Setup premium typography system"""
        self.title_font = font.Font(family="Segoe UI", size=32, weight="bold")
        self.subtitle_font = font.Font(family="Segoe UI", size=13)
        self.section_font = font.Font(family="Segoe UI", size=16, weight="bold")
        self.body_font = font.Font(family="Segoe UI", size=12)
        self.small_font = font.Font(family="Segoe UI", size=11)
        self.tiny_font = font.Font(family="Segoe UI", size=10)
        self.micro_font = font.Font(family="Segoe UI", size=9)
    
    def setup_styles(self):
        """Setup enhanced modern styles using color utilities"""
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Recording Button
        self.style.configure("CompactRecording.TButton",
                            font=("Segoe UI", 12, "bold"),
                            padding=(20, 8),
                            borderwidth=0,
                            focuscolor='none',
                            relief='flat')
        
        self.style.map("CompactRecording.TButton",
                      background=[('active', lighten_color(COLORS['primary'], 0.1)),
                                  ('!active', COLORS['primary'])],
                      foreground=[('active', COLORS['text_white']),
                                  ('!active', COLORS['text_white'])],
                      relief=[('!active', 'flat')])
        
        # Stop Recording Button
        self.style.configure("CompactStop.TButton",
                            font=("Segoe UI", 12, "bold"),
                            padding=(20, 8),
                            borderwidth=0,
                            focuscolor='none',
                            relief='flat')
        
        self.style.map("CompactStop.TButton",
                      background=[('active', darken_color(COLORS['accent_danger'], 0.1)),
                                  ('!active', COLORS['accent_danger'])],
                      foreground=[('active', COLORS['text_white']),
                                  ('!active', COLORS['text_white'])],
                      relief=[('!active', 'flat')])
        
        # Action Button
        self.style.configure("Action.TButton",
                            font=("Segoe UI", 11, "bold"),
                            padding=(20, 12),
                            borderwidth=0,
                            focuscolor='none',
                            relief='flat')
        
        self.style.map("Action.TButton",
                      background=[('active', darken_color(COLORS['accent_generate'], 0.1)),
                                  ('!active', COLORS['accent_generate'])],
                      foreground=[('active', COLORS['text_white']),
                                  ('!active', COLORS['text_white'])], 
                      relief=[('!active', 'flat')])
        
        # Disabled Action Button
        self.style.configure("ActionDisabled.TButton",
                            font=("Segoe UI", 11, "bold"),
                            padding=(20, 12),
                            borderwidth=0,
                            focuscolor='none',
                            relief='flat')
        
        self.style.map("ActionDisabled.TButton",
                      background=[('!active', COLORS['text_muted'])],
                      foreground=[('!active', COLORS['text_white'])],
                      relief=[('!active', 'flat')])
        
        # Clear Button Style
        self.style.configure("ClearButton.TButton",
                            font=("Segoe UI", 11),
                            padding=(15, 8),
                            borderwidth=1,
                            relief='flat')
        
        self.style.map("ClearButton.TButton",
                      background=[('active', COLORS['bg_hover']),
                                  ('!active', COLORS['bg_surface'])],
                      foreground=[('!active', COLORS['text_secondary'])],
                      bordercolor=[('!active', COLORS['border_light'])],
                      relief=[('!active', 'flat')])
        
        # Secondary Button
        self.style.configure("Secondary.TButton",
                            font=("Segoe UI", 10),
                            padding=(15, 8),
                            borderwidth=1,
                            relief='flat')
        
        self.style.map("Secondary.TButton",
                      background=[('active', COLORS['bg_hover']),
                                  ('!active', COLORS['bg_card'])],
                      foreground=[('!active', COLORS['text_primary'])],
                      bordercolor=[('!active', COLORS['border'])],
                      relief=[('!active', 'flat')])
        
        # Combobox
        self.style.configure("TCombobox",
                            fieldbackground=COLORS['bg_surface'],
                            background=COLORS['bg_card'],
                            borderwidth=2,
                            relief='flat')
        
        self.style.map("TCombobox",
                      bordercolor=[('focus', COLORS['primary']),
                                  ('!focus', COLORS['border'])],
                      fieldbackground=[('focus', COLORS['bg_card']),
                                      ('!focus', COLORS['bg_surface'])])
    
    def setup_window(self):
        """Setup main window configuration"""
        self.root.title(APP_TITLE)
        self.root.configure(bg=COLORS['bg_primary'])
        self.root.resizable(True, True)
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        
        # Set custom icon
        try:
            if os.path.exists(APP_ICON_PATH):
                self.root.iconbitmap(APP_ICON_PATH)
                print(f"✅ Custom icon loaded: {APP_ICON_PATH}")
            else:
                print(f"⚠️ Icon not found: {APP_ICON_PATH}")
        except Exception as e:
            print(f"⚠️ Could not load custom icon: {e}")
        
        # Center the window
        self.center_window()
        
        # Try to maximize window at startup
        try:
            self.root.state('zoomed')  # Windows
        except:
            try:
                self.root.attributes('-zoomed', True)  # Linux
            except:
                pass
        
        # Remove transparency - set to fully opaque
        try:
            self.root.attributes('-alpha', 1.0)
        except:
            pass
    
    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (WINDOW_WIDTH // 2)
        y = (self.root.winfo_screenheight() // 2) - (WINDOW_HEIGHT // 2)
        self.root.geometry(f'{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x}+{y}')
    
    def create_ui(self):
        """Create all UI components"""
        # Main scrollable container
        self.setup_scrollable_container()
        
        # Create main sections
        self.create_header()
        self.create_middle_section()
        self.create_bottom_section()
        self.create_footer()
    
    def setup_scrollable_container(self):
        """Setup scrollable main container"""
        self.canvas = tk.Canvas(self.root, bg=COLORS['bg_primary'], highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=COLORS['bg_primary'])
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Pack scrollbar first (on the right edge)
        self.scrollbar.pack(side="right", fill="y")
        # Then pack canvas to fill remaining space
        self.canvas.pack(fill="both", expand=True)
        
        # Mouse wheel scrolling
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        self.canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Main content frame
        main_frame = tk.Frame(self.scrollable_frame, bg=COLORS['bg_primary'])
        main_frame.pack(fill='both', expand=True)
        
        # Responsive centered container
        self.centered_container = tk.Frame(main_frame, bg=COLORS['bg_primary'])
        screen_width = self.root.winfo_screenwidth()
        side_padding = max(20, min(100, screen_width // 16))
        self.centered_container.pack(expand=True, fill='both', padx=side_padding, pady=40)
        
        # Content frame
        self.content_frame = tk.Frame(self.centered_container, bg=COLORS['bg_primary'])
        self.content_frame.pack(expand=True, fill='both')
    
    def create_header(self):
        """Create compact header section with centered title"""
        # Main header container
        header_frame = tk.Frame(self.content_frame, bg=COLORS['bg_card'], relief='flat', bd=0)
        header_frame.pack(fill='x', pady=(0, 30))
        
        # Shadow effect
        shadow_frame = tk.Frame(self.content_frame, height=2, bg=COLORS['shadow_light'])
        shadow_frame.place(in_=header_frame, relx=0, rely=1, relwidth=1)
        
        # Create a centered container for the header content
        header_outer = tk.Frame(header_frame, bg=COLORS['bg_card'])
        header_outer.pack(fill='both', expand=True, padx=30, pady=40)
        
        # Center the title content horizontally
        header_content = tk.Frame(header_outer, bg=COLORS['bg_card'])
        header_content.pack(anchor='center')
        
        # Title section
        title_container = tk.Frame(header_content, bg=COLORS['bg_card'])
        title_container.pack()
        
        title_label = tk.Label(title_container, text=APP_TITLE, font=("Segoe UI", 28, "bold"),
                            bg=COLORS['bg_card'], fg=COLORS['primary'])
        title_label.pack()
        
        subtitle_label = tk.Label(title_container, text=APP_DESCRIPTION,
                                font=("Segoe UI", 11), bg=COLORS['bg_card'], fg=COLORS['text_secondary'])
        subtitle_label.pack(pady=(5, 0))
    
    def create_middle_section(self):
        """Create middle section with audio visualization and transcription"""
        middle_row = tk.Frame(self.content_frame, bg=COLORS['bg_primary'])
        middle_row.pack(fill='x', pady=(0, 30))
        
        # Audio visualization frame - using AudioUIManager
        audio_frame = self.audio_ui_manager.create_audio_section(middle_row, self.section_font, self.create_button_tooltip)
        
        # Set wave canvas for animation manager
        wave_canvas = self.audio_ui_manager.get_wave_canvas()
        if wave_canvas:
            self.animation_manager.set_wave_canvas(wave_canvas)
        
        # Transcription frame
        self.create_transcription_section(middle_row)
    
    def create_transcription_section(self, parent):
        """Create transcription section"""
        transcription_frame = tk.Frame(parent, bg=COLORS['bg_card'], relief='flat', bd=0)
        transcription_frame.pack(side='right', fill='both', expand=True, padx=(15, 0))
        
        # Shadow effect
        trans_shadow = tk.Frame(parent, height=2, bg=COLORS['shadow_light'])
        trans_shadow.place(in_=transcription_frame, relx=0, rely=1, relwidth=1)
        
        # Header
        trans_header = tk.Frame(transcription_frame, bg=COLORS['bg_card'])
        trans_header.pack(fill='x', padx=20, pady=(25, 15))
        
        trans_title_container = tk.Frame(trans_header, bg=COLORS['bg_card'])
        trans_title_container.pack(side='left')
        
        tk.Label(trans_title_container, text="📝", font=("Segoe UI", 18),
                 bg=COLORS['bg_card'], fg=COLORS['accent_info']).pack(side='left', padx=(0, 10))
        
        transcription_title = tk.Label(trans_title_container, text="Live Speech Transcription", font=self.section_font,
                                      bg=COLORS['bg_card'], fg=COLORS['text_primary'])
        transcription_title.pack(side='left')
        
        # Controls
        trans_controls = tk.Frame(trans_header, bg=COLORS['bg_card'])
        trans_controls.pack(side='right', padx=(0, 20))
        
        clear_button = ttk.Button(trans_controls, text="Clear", command=self.clear_transcription, 
                                 style="ClearButton.TButton")
        clear_button.pack(side='right')
        clear_button.configure(cursor='hand2')
        self.create_button_tooltip(clear_button, "Clear the current audio transcript")
        
        # Transcription text area with scrollbar
        self.transcription_text = tk.scrolledtext.ScrolledText(
            transcription_frame,
            wrap=tk.WORD,
            font=self.body_font,
            bg=COLORS['bg_surface'],
            fg=COLORS['text_primary'],
            selectbackground=COLORS['primary'],
            selectforeground=COLORS['text_white'],
            relief='flat',
            bd=0,
            height=TEXT_AREA_HEIGHT,
            padx=20,
            pady=20
        )
        self.transcription_text.pack(fill='both', expand=True, padx=25, pady=(0, 25))
        self.transcription_text.config(state='normal')
        self.transcription_text.insert(tk.END, WELCOME_TEXT)
        self.transcription_text.config(state='disabled')
    
    def create_bottom_section(self):
        """Create bottom section with AI analysis and controls"""
        bottom_row = tk.Frame(self.content_frame, bg=COLORS['bg_primary'])
        bottom_row.pack(fill='both', expand=True)
        
        # AI Analysis section
        self.create_analysis_section(bottom_row)
        
        # Control panel
        self.create_control_panel(bottom_row)
    
    def create_analysis_section(self, parent):
        """Create AI analysis section with prescription manager"""
        analysis_frame = tk.Frame(parent, bg=COLORS['bg_card'], relief='flat', bd=0)
        analysis_frame.pack(side='left', fill='both', expand=True, padx=(0, 15))
        
        # Shadow effect
        analysis_shadow = tk.Frame(parent, height=2, bg=COLORS['shadow_light'])
        analysis_shadow.place(in_=analysis_frame, relx=0, rely=1, relwidth=1)
        
        # Header
        analysis_header = tk.Frame(analysis_frame, bg=COLORS['bg_card'])
        analysis_header.pack(fill='x', padx=20, pady=(25, 15))
        
        # Title
        analysis_title_container = tk.Frame(analysis_header, bg=COLORS['bg_card'])
        analysis_title_container.pack(side='left')
        
        tk.Label(analysis_title_container, text="🤖", font=("Segoe UI", 18),
                 bg=COLORS['bg_card'], fg=COLORS['accent_purple']).pack(side='left', padx=(0, 10))
        
        analysis_title = tk.Label(analysis_title_container, text="Structured Medical Report", font=self.section_font,
                                 bg=COLORS['bg_card'], fg=COLORS['text_primary'])
        analysis_title.pack(side='left')
        
        # Export and Import buttons
        export_controls = tk.Frame(analysis_header, bg=COLORS['bg_card'])
        export_controls.pack(side='right', padx=(0, 20))
        
        export_button = ttk.Button(export_controls, text="Export", command=self.export_pdf, 
                                 style="ClearButton.TButton")
        export_button.pack(side='right')
        export_button.configure(cursor='hand2')
        self.create_button_tooltip(export_button, "Export the medical report to PDF")
        
        # Spacing between buttons
        spacing_frame = tk.Frame(export_controls, bg=COLORS['bg_card'], width=10)
        spacing_frame.pack(side='right', padx=(5, 5))
        
        import_button = ttk.Button(export_controls, text="Import", command=self.import_document, 
                                 style="ClearButton.TButton")
        import_button.pack(side='right')
        import_button.configure(cursor='hand2')
        self.create_button_tooltip(import_button, "Import a document")
        
        # Rich text area with scrollbar
        self.summary_text = RichTextWidget(
            analysis_frame,
            wrap=tk.WORD,
            font=self.body_font,
            bg=COLORS['bg_surface'],
            fg=COLORS['text_primary'],
            selectbackground=COLORS['primary'],
            selectforeground=COLORS['text_white'],
            relief='flat',
            bd=0,
            height=TEXT_AREA_HEIGHT,
            padx=20,
            pady=20
        )
        self.summary_text.pack(fill='both', expand=True, padx=25, pady=(0, 15))
        self.summary_text.insert_formatted_text(ANALYSIS_WELCOME_TEXT)
        
        # Initialize prescription manager with the analysis frame
        self.prescription_manager = PrescriptionManager(analysis_frame)
    
    def create_control_panel(self, parent):
        """Create control panel section"""
        control_frame = tk.Frame(parent, bg=COLORS['bg_card'], relief='flat', bd=0)
        control_frame.pack(side='right', fill='y', padx=(15, 0))
        
        # Shadow effect
        control_shadow = tk.Frame(parent, height=2, bg=COLORS['shadow_light'])
        control_shadow.place(in_=control_frame, relx=0, rely=1, relwidth=1)
        
        # Header
        control_header = tk.Frame(control_frame, bg=COLORS['bg_card'])
        control_header.pack(fill='x', pady=(25, 20))
        
        control_title_container = tk.Frame(control_header, bg=COLORS['bg_card'])
        control_title_container.pack()
        
        tk.Label(control_title_container, text="⚙️", font=("Segoe UI", 18),
                 bg=COLORS['bg_card'], fg=COLORS['accent_teal']).pack(side='left', padx=(0, 10))
        
        control_title = tk.Label(control_title_container, text="AI Configuration", font=self.section_font,
                                bg=COLORS['bg_card'], fg=COLORS['text_primary'])
        control_title.pack(side='left')
        
        # Control content
        control_content = tk.Frame(control_frame, bg=COLORS['bg_card'])
        control_content.pack(fill='both', expand=True, padx=30, pady=(0, 25))
        
        # Report type section
        self.create_report_type_section(control_content)
        
        # Language section
        self.create_language_section(control_content)
        
        # Generate button with status
        self.create_generate_section(control_content)
    
    def create_report_type_section(self, parent):
        """Create report format selection section"""
        report_section = tk.Frame(parent, bg=COLORS['bg_surface'], relief='flat', bd=0)
        report_section.pack(fill='x', pady=(0, 25))
        
        # Header
        report_header = tk.Frame(report_section, bg=COLORS['bg_surface'])
        report_header.pack(fill='x')
        
        tk.Label(report_header, text="Report Format", font=("Segoe UI", 13, "bold"),
                 bg=COLORS['bg_surface'], fg=COLORS['text_primary']).pack(padx=20, pady=12)
        
        # Radio buttons
        self.report_type_var = tk.StringVar(value=REPORT_TYPE_DEFAULT)
        report_buttons_frame = tk.Frame(report_section, bg=COLORS['bg_surface'])
        report_buttons_frame.pack(fill='x', padx=20, pady=20)
        
        self.report_types = REPORT_TYPES
        self.report_buttons = {}
        
        for report_type in self.report_types:
            rb_frame = tk.Frame(report_buttons_frame, bg=COLORS['bg_card'])
            rb_frame.pack(fill='x', pady=2)
            
            font_weight = "bold" if report_type == REPORT_TYPE_DEFAULT else "normal"
            
            rb = tk.Radiobutton(rb_frame, text=f"  {report_type}", variable=self.report_type_var, value=report_type,
                               bg=COLORS['bg_card'], fg=COLORS['text_primary'], font=("Segoe UI", 11, font_weight),
                               selectcolor=COLORS['primary'],
                               activebackground=COLORS['primary_light'],
                               activeforeground=COLORS['text_white'],
                               relief='flat', bd=0, indicatoron=True, anchor='w',
                               command=self.update_report_selection, cursor='hand2') 
            rb.pack(fill='x', padx=15, pady=8)
            
            self.report_buttons[report_type] = rb
    
    def create_language_section(self, parent):
        """Create language selection section"""
        language_section = tk.Frame(parent, bg=COLORS['bg_surface'], relief='flat', bd=0)
        language_section.pack(fill='x', pady=(0, 25))
        
        # Header
        language_header = tk.Frame(language_section, bg=COLORS['bg_surface'])
        language_header.pack(fill='x')
        
        tk.Label(language_header, text="Report Language", font=("Segoe UI", 13, "bold"),
                 bg=COLORS['bg_surface'], fg=COLORS['text_primary']).pack(padx=20, pady=12)
        
        # Language dropdown
        self.language_var = tk.StringVar(value="English")
        language_frame = tk.Frame(language_section, bg=COLORS['bg_surface'])
        language_frame.pack(fill='x', padx=20, pady=20)
        
        # Center the combobox
        language_center_frame = tk.Frame(language_frame, bg=COLORS['bg_surface'])
        language_center_frame.pack()
        
        self.language_combo = ttk.Combobox(language_center_frame, textvariable=self.language_var, values=LANGUAGES,
                                         state="readonly", width=25, font=self.body_font)
        self.language_combo.pack()
    
    def create_generate_section(self, parent):
        """Create generate button section with status display"""
        generate_section = tk.Frame(parent, bg=COLORS['bg_glass'], relief='flat', bd=0)
        generate_section.pack(fill='x', pady=(15, 0))
        
        # Generate button
        self.generate_button = ttk.Button(generate_section, text="GENERATE", 
                                        command=self.generate_report, style="Action.TButton")
        self.generate_button.pack(fill='x', padx=20, pady=(20, 10))
        self.generate_button.configure(cursor='hand2')
        
        # Status label below the button
        self.generate_status_label = tk.Label(generate_section, text="", font=("Segoe UI", 10),
                                            bg=COLORS['bg_glass'], fg=COLORS['text_secondary'],
                                            wraplength=200, justify='center')
        self.generate_status_label.pack(padx=20, pady=(0, 20))
        
        # Add tooltip to generate button
        self.create_tooltip(self.generate_button)
    
    def create_footer(self):
        """Create footer section"""
        footer_frame = tk.Frame(self.content_frame, bg=COLORS['bg_primary'])
        footer_frame.pack(fill='x', pady=(30, 0))
        
        # Divider
        divider = tk.Frame(footer_frame, height=1, bg=COLORS['primary'])
        divider.pack(fill='x', pady=(0, 20))
        
        # Footer content
        footer_content = tk.Frame(footer_frame, bg=COLORS['bg_primary'])
        footer_content.pack()
        
        # App name
        app_info = tk.Label(footer_content, text=APP_TITLE, font=("Segoe UI", 11, "bold"),
                        bg=COLORS['bg_primary'], fg=COLORS['primary'])
        app_info.pack(side='left')
        
        # Version
        version_info = tk.Label(footer_content, text=f" v. {APP_VERSION}", font=("Segoe UI", 11),
                            bg=COLORS['bg_primary'], fg=COLORS['primary'])
        version_info.pack(side='left')
        
        # Separator
        separator = tk.Label(footer_content, text=" • ", font=self.tiny_font,
                            bg=COLORS['bg_primary'], fg=COLORS['text_muted'])
        separator.pack(side='left')
        
        # Powered by Gemma 3n
        powered_by = tk.Label(footer_content, text="Powered by Gemma 3n",
                            font=self.tiny_font, bg=COLORS['bg_primary'], fg=COLORS['primary'])
        powered_by.pack(side='left')
        
        # Separator
        separator2 = tk.Label(footer_content, text=" • ", font=self.tiny_font,
                            bg=COLORS['bg_primary'], fg=COLORS['text_muted'])
        separator2.pack(side='left')
        
        # Copyright
        copyright_info = tk.Label(footer_content, text="© 2025 Young-wouk KIM",
                                font=self.tiny_font, bg=COLORS['bg_primary'], fg=COLORS['text_muted'])
        copyright_info.pack(side='left')
        
        # Separator
        separator3 = tk.Label(footer_content, text=" • ", font=self.tiny_font,
                            bg=COLORS['bg_primary'], fg=COLORS['text_muted'])
        separator3.pack(side='left')
        
        # Website link
        website_link = tk.Label(footer_content, text="wouk1805.com", font=self.tiny_font,
                            bg=COLORS['bg_primary'], fg=COLORS['accent_info'], cursor='hand2')
        website_link.pack(side='left')
        website_link.bind("<Button-1>", self.open_website)
    
    # ========================================================================
    # EVENT HANDLERS
    # ========================================================================
    
    def schedule_ui_update(self, callback):
        """Schedule a UI update to run on the main thread"""
        self.root.after(0, callback)
    
    def on_record_click(self):
        """Handle record button click with import file reset behavior"""
        if not self.audio_engine.is_recording:
            # Reset imported file when clicking Start
            print("🎬 Starting recording - resetting imported file...")
            self.file_manager.reset_imported_content()
            
            if self.audio_ui_manager.start_recording():
                # Clear transcription
                self.transcription_text.config(state='normal')
                self.transcription_text.delete("1.0", tk.END)
                self.transcription_text.config(state='disabled')
                
                # Show recording message
                recording_message = RECORDING_ACTIVE_TEXT
                
                # Update summary section
                self.summary_text.clear()
                self.summary_text.insert_formatted_text(recording_message)
                
                # Reset prescription status
                if self.prescription_manager:
                    self.prescription_manager.reset_prescription_status()
                
                print("✅ Recording started successfully")
            else:
                print("❌ Failed to start recording")
        else:
            # Stop recording
            print("🛑 Stopping recording...")
            
            if self.audio_ui_manager.stop_recording():
                # Auto-generate with delay
                def maybe_generate():
                    # Get transcription from audio engine
                    full_transcription = self.audio_engine.get_full_transcription()
                    if full_transcription.strip():
                        self.current_transcription = full_transcription
                        print("🤖 Auto-generating report...")
                        self.generate_report()
                    else:
                        print("ℹ️ No content for report generation")
                
                self.root.after(5000, maybe_generate)
                print("✅ Stop initiated")
    
    def import_document(self):
        """Import a PDF document using FileOperationsManager"""
        success, content, message = self.file_manager.import_pdf_document(self.summary_text)
        
        if success:
            print(f"✅ Document imported: {message}")
            # Reset prescription status when importing new document
            if self.prescription_manager:
                self.prescription_manager.reset_prescription_status()
        else:
            print(f"❌ Import failed: {message}")
    
    def clear_transcription(self):
        """Clear all transcription data with import file reset behavior"""
        print("🧹 Clearing all transcripts")
        
        # Reset imported file when clicking Clear
        self.file_manager.reset_imported_content()
        
        # Clear UI transcription
        self.current_transcription = ""
        
        self.transcription_text.config(state='normal')
        self.transcription_text.delete("1.0", tk.END)
        self.transcription_text.insert(tk.END, CLEARED_TEXT)
        self.transcription_text.config(state='disabled')
        
        # Clear summary
        self.summary_text.clear()
        self.summary_text.insert_formatted_text(ANALYSIS_WELCOME_TEXT)
        
        # Reset prescription status
        if self.prescription_manager:
            self.prescription_manager.reset_prescription_status()
        
        # Clear audio engine transcripts
        if hasattr(self.audio_engine, 'chunk_transcripts'):
            self.audio_engine.chunk_transcripts = []
            print("🧹 Cleared chunk transcripts")
        
        # Reset chronometer
        if hasattr(self, 'audio_ui_manager') and self.audio_ui_manager:
            self.audio_ui_manager.reset_chronometer()
            print("⏰ Chronometer reset to 00:00")
        
        self.update_status("Cleared", COLORS['accent_info'], "animate")

    def generate_report(self):
        """Generate AI report using local Gemma 3n model - Keep imported file in memory"""
        # Get transcription from current stored value or audio engine
        current_transcript = self.current_transcription.strip()
        if not current_transcript:
            current_transcript = self.audio_engine.get_full_transcription().strip()
        
        if not current_transcript:
            print("⚠️ No transcript available for report generation")
            
            self.generate_status_label.config(text="No transcript available",
                                            fg=COLORS['accent_warning'])
            self.root.after(4000, lambda: self.generate_status_label.config(text=""))
            return
        
        # Get report settings
        report_type = self.report_type_var.get()
        language = self.language_var.get()
        
        # Load custom format if Custom report type is selected
        custom_format = None
        if report_type.lower() == "custom":
            success, custom_format, message = self.file_manager.load_custom_report_format()
            if success:
                print(f"🎯 Using custom report format: {len(custom_format)} chars")
            else:
                print(f"⚠️ Custom report selected but no valid format found: {message}")
        
        print(f"🚀 Generating {report_type} report in {language}")
        print(f"📝 Using transcript: {len(current_transcript)} chars")
        if custom_format:
            print(f"🎨 Custom format: {custom_format[:100]}..." if len(custom_format) > 100 else f"🎨 Custom format: {custom_format}")
        
        # Keep imported file in memory and do NOT clear it
        attachment = self.file_manager.get_imported_content()
        if attachment:
            print(f"📎 USING imported document as attachment: {len(attachment)} chars")
            print(f"📋 Attachment preview: {attachment[:100]}..." if len(attachment) > 100 else f"📋 Attachment content: {attachment}")
        else:
            print("📎 No imported document available")
        
        # Set generation state
        self.is_generating_report = True
        
        # Disable generate button and remove tooltip/cursor
        self.disable_generate_button()
        
        # Force UI update to show disabled button
        self.root.update_idletasks()
        
        # Set status to generating with orange color
        status_text = "Generating report..."
        self.generate_status_label.config(text=status_text, fg=COLORS['accent_orange'])
        
        # Force UI update to show the orange "Generating..." status
        self.root.update_idletasks()
        
        print(f"🔄 Status set to '{status_text}' in orange")
        
        # Import LocalReportGenerator from updated audio module
        from audio import LocalReportGenerator
        
        # Create UI callbacks
        ui_callbacks = {
            'display_summary': self.display_summary,
            'start_generate_animation': self.start_generate_animation,
            'stop_generate_animation': self.stop_generate_animation,
            'schedule_ui_update': self.schedule_ui_update,
            'update_generate_status': self.update_generate_status,
            'root': self.root,
            're_enable_button': self.re_enable_generate_button
        }
        
        # Add a small delay to ensure UI updates are visible
        def start_local_generation():
            print("🔄 Starting local report generation...")
            print(f"📎 Sending attachment to local model: {'YES' if attachment else 'NO'}")
            LocalReportGenerator.generate_report(
                current_transcript, 
                report_type, 
                language, 
                ui_callbacks, 
                custom_format, 
                attachment,
                self.audio_engine.model_manager  # Pass model manager
            )
        
        # Schedule local generation with small delay to ensure UI update is visible
        self.root.after(100, start_local_generation)
    
    def disable_generate_button(self):
        """Disable generate button and remove tooltip/cursor"""
        # Disable button with disabled style
        self.generate_button.config(state='disabled', style="ActionDisabled.TButton")
        
        # Remove hand cursor (revert to default)
        self.generate_button.configure(cursor='')
        
        # Destroy any existing tooltip window
        if hasattr(self, 'tooltip'):
            try:
                self.tooltip.destroy()
                del self.tooltip
            except:
                pass
        
        # Remove existing tooltip bindings completely
        self.generate_button.unbind("<Enter>")
        self.generate_button.unbind("<Leave>")
        self.generate_button.unbind("<Motion>")
        self.generate_button.unbind("<ButtonPress>")
        self.generate_button.unbind("<ButtonRelease>")
        
        print("🚫 Generate button disabled - tooltip destroyed and cursor removed")

    def enable_generate_button(self):
        """Enable generate button and restore tooltip/cursor"""
        # Enable button with normal style
        self.generate_button.config(state='normal', style="Action.TButton")
        
        # Restore hand cursor
        self.generate_button.configure(cursor='hand2')
        
        # Make sure any old tooltip is destroyed first
        if hasattr(self, 'tooltip'):
            try:
                self.tooltip.destroy()
                del self.tooltip
            except:
                pass
        
        # Remove any existing bindings first
        self.generate_button.unbind("<Enter>")
        self.generate_button.unbind("<Leave>")
        
        # Restore tooltip with fresh bindings
        self.create_tooltip(self.generate_button)
        
        print("✅ Generate button enabled - fresh tooltip and cursor restored")

    def re_enable_generate_button(self):
        """Re-enable the generate button and reset state"""
        self.enable_generate_button()
        self.is_generating_report = False
        print("🔄 Generate button re-enabled after error")

    def update_generate_status(self, message, color=COLORS['text_secondary']):
        """Update the generate status label with truncation for long messages"""
        # Truncate very long messages to prevent UI overflow
        if len(message) > 40:
            display_message = message[:37] + "..."
        else:
            display_message = message
            
        self.generate_status_label.config(text=display_message, fg=color)
        self.root.update_idletasks()
        print(f"📊 Status updated: {message}")  # Log full message
        
        # Auto-clear status after 4 seconds
        self.root.after(4000, lambda: self.generate_status_label.config(text=""))
    
    # ========================================================================
    # UI CALLBACKS (called by audio engine)
    # ========================================================================
    
    def update_status(self, message, color=COLORS['text_secondary'], animation_type="static"):
        """Update status label with enhanced visual feedback using animation manager"""
        status_colors = {
            "Starting": COLORS['accent_info'],
            "Recording": COLORS['accent_danger'],
            "Stopping": COLORS['accent_warning'],
            "Finalizing": COLORS['accent_orange'],
            "Processing": COLORS['accent_orange'],
            "Complete": COLORS['accent_success'],
            "Ready": COLORS['accent_success'],
            "Error": COLORS['accent_danger'],
            "Failed": COLORS['accent_danger'],
        }
        
        # Auto-detect color based on message
        for status, status_color in status_colors.items():
            if status in message:
                color = status_color
                break
        
        # Use animation manager for animated updates
        if animation_type == "animate" and hasattr(self.audio_ui_manager, 'status_label'):
            self.animation_manager.animate_status(self.audio_ui_manager.status_label, message, color)
        elif hasattr(self.audio_ui_manager, 'status_label'):
            self.audio_ui_manager.status_label.config(text=message, fg=color)
        
        self.root.update_idletasks()
    
    def append_transcription(self, text):
        """Append text to transcription area"""
        if not text or text.strip() == "":
            return
        
        print(f"📝 New transcription: {text[:50]}...")
        
        self.transcription_text.config(state='normal')
        
        # If this is the first transcription, clear placeholder text
        current_content = self.transcription_text.get("1.0", tk.END).strip()
        if not self.current_transcription and f"Welcome to {APP_TITLE}" in current_content:
            self.transcription_text.delete("1.0", tk.END)
        
        # Add text with single line break
        self.transcription_text.insert(tk.END, f"{text}\n")
        self.transcription_text.see(tk.END)
        self.transcription_text.config(state='disabled')
        
        # Update current transcription from audio engine
        self.current_transcription = self.audio_engine.get_full_transcription()
    
    def display_summary(self, summary_content, is_final_result=False):
        """Display AI summary with prescription detection and XML removal"""
        print(f"🤖 Displaying summary: {len(summary_content)} characters, final={is_final_result}")
        
        # Process prescriptions and get cleaned content
        cleaned_content = summary_content
        if self.prescription_manager and is_final_result:
            cleaned_content = self.prescription_manager.check_summary_for_prescription(summary_content)
            print(f"🧹 Using cleaned content: {len(cleaned_content)} chars (removed prescription XML)")
        
        # Use RichTextWidget's method to insert cleaned formatted text
        self.summary_text.insert_formatted_text(cleaned_content, clear_first=True)
        
        # Scroll to top for better readability
        self.summary_text.see("1.0")
        
        # Only show success status and re-enable button for final results
        if is_final_result:
            # Do not clear imported document content after generation
            # Keep it persistent for multiple generations with different formats
            if self.file_manager.has_imported_content():
                imported_size = len(self.file_manager.get_imported_content())
                print(f"📎 PRESERVED imported file for next generation: {imported_size} chars")
            
            # Re-enable generate button with tooltip and cursor
            self.enable_generate_button()
            
            # Only show success status if we were actually generating
            if self.is_generating_report:
                print("✅ Report generation completed - updating status to success")
                
                # Set generation state to False FIRST
                self.is_generating_report = False
                
                # Show success status
                self.generate_status_label.config(text="Report successfully generated",
                                                fg=COLORS['accent_success'])
                
                # Clear status after 4 seconds
                self.root.after(4000, lambda: self.generate_status_label.config(text=""))
            else:
                print("ℹ️ Display summary called but not in generating state - keeping current status")
    
    # ========================================================================
    # EXPORT FUNCTIONS
    # ========================================================================
    
    def export_pdf(self):
        """Export report content to PDF using FileOperationsManager"""
        try:
            report_content = self.summary_text.get_text()
            if not report_content or len(report_content.strip()) < 50:
                print("⚠️ No substantial report to export")
                return
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_filename = f"{APP_TITLE}_{timestamp}.pdf"
            
            # Use the file manager for export
            result = self.file_manager.export_to_pdf(
                rich_text_widget=self.summary_text,
                default_filename=default_filename,
                dialog_title="Export Medical Report"
            )
            
            if result['success']:
                print(f"✅ {result['message']}")
            elif result['cancelled']:
                print("ℹ️ Export cancelled by user")
            else:
                print(f"❌ {result['message']}")
                
        except Exception as e:
            print(f"❌ Export failed: {e}")
    
    # ========================================================================
    # UTILITY METHODS
    # ========================================================================
    
    def start_generate_animation(self):
        """Start generate button animation (handled by status label)"""
        pass
    
    def stop_generate_animation(self):
        """Stop generate button animation (handled by status label)"""
        pass
    
    def update_report_selection(self):
        """Update font weight when report selection changes"""
        selected = self.report_type_var.get()
        for report_type, button in self.report_buttons.items():
            if report_type == selected:
                button.config(font=("Segoe UI", 11, "bold"))
            else:
                button.config(font=("Segoe UI", 11, "normal"))
    
    def create_button_tooltip(self, widget, text):
        """Create tooltip for buttons"""
        def show_tooltip(event):
            self.tooltip = tk.Toplevel()
            self.tooltip.wm_overrideredirect(True)
            self.tooltip.wm_geometry(f"+{event.x_root + 10}+{event.y_root + 10}")
            
            label = tk.Label(self.tooltip, text=text, 
                           bg=COLORS['bg_card'], fg=COLORS['text_primary'],
                           relief='solid', bd=1, font=("Segoe UI", 10),
                           padx=10, pady=5)
            label.pack()
        
        def hide_tooltip(event):
            if hasattr(self, 'tooltip'):
                self.tooltip.destroy()
                del self.tooltip
        
        widget.bind("<Enter>", show_tooltip)
        widget.bind("<Leave>", hide_tooltip)
    
    def create_tooltip(self, widget):
        """Create tooltip for generate button"""
        def show_tooltip(event):
            # Don't show tooltip if button is disabled
            if widget['state'] == 'disabled':
                return
                
            # Destroy any existing tooltip first
            if hasattr(self, 'tooltip'):
                try:
                    self.tooltip.destroy()
                    del self.tooltip
                except:
                    pass
            
            report_format = self.report_type_var.get().lower()
            report_language = self.language_var.get()
            tooltip_text = f"Generate a {report_format} medical report in {report_language}"
            
            self.tooltip = tk.Toplevel()
            self.tooltip.wm_overrideredirect(True)
            self.tooltip.wm_geometry(f"+{event.x_root + 10}+{event.y_root + 10}")
            
            label = tk.Label(self.tooltip, text=tooltip_text, 
                           bg=COLORS['bg_card'], fg=COLORS['text_primary'],
                           relief='solid', bd=1, font=("Segoe UI", 10),
                           padx=10, pady=5)
            label.pack()
        
        def hide_tooltip(event):
            if hasattr(self, 'tooltip'):
                try:
                    self.tooltip.destroy()
                    del self.tooltip
                except:
                    pass
        
        # Bind events to widget
        widget.bind("<Enter>", show_tooltip)
        widget.bind("<Leave>", hide_tooltip)
        
        # Also bind to button press to hide tooltip immediately
        widget.bind("<Button-1>", hide_tooltip)
    
    def open_website(self, event=None):
        """Open website in browser"""
        import webbrowser
        webbrowser.open("https://wouk1805.com")
    
    def setup_centered_layout(self):
        """Setup the perfectly centered layout"""
        self.root.update_idletasks()
        self.centered_container.update_idletasks()
        self.content_frame.update_idletasks()
    
    # ========================================================================
    # CLEANUP
    # ========================================================================
    
    def cleanup(self):
        """Cleanup all managers and UI components"""
        print("🧹 Starting UI cleanup...")
        
        try:
            # Cleanup managers
            if hasattr(self, 'animation_manager'):
                self.animation_manager.cleanup()
            
            if hasattr(self, 'audio_ui_manager'):
                self.audio_ui_manager.cleanup()
            
            if hasattr(self, 'file_manager'):
                self.file_manager.clear_imported_content()
            
            if hasattr(self, 'prescription_manager'):
                self.prescription_manager.cleanup()
            
            print("✅ UI cleanup completed")
            
        except Exception as e:
            print(f"❌ Error during UI cleanup: {e}")