# rich_text_widget.py
# ============================================================================
# Rich Text Widget - Stores raw markdown, displays formatted text
# ============================================================================

import tkinter as tk
from tkinter import scrolledtext, font
import re
from config import COLORS

class RichTextWidget:
    """Rich text widget that stores raw markdown and displays formatted text"""
    
    def __init__(self, parent, **kwargs):
        # Extract our custom parameters
        self.bg_color = kwargs.pop('bg', COLORS['bg_surface'])
        self.fg_color = kwargs.pop('fg', COLORS['text_primary'])
        
        # Force read-only
        kwargs['state'] = 'disabled'
        
        # Create the scrolled text widget
        self.widget = scrolledtext.ScrolledText(parent, **kwargs)
        self.widget.config(bg=self.bg_color, fg=self.fg_color)
        
        # Store both raw and formatted text
        self._raw_markdown_text = ""      # Raw text with ** and * tags (for PDF export)
        self._formatted_display_text = "" # Clean text without tags (for display)
        
        print("✅ Rich text widget created with dual storage approach")
        
        # Setup fonts and tags
        self.setup_fonts()
        self.setup_tags()
        
        # Configure as read-only
        self.widget.config(
            state='disabled',
            cursor='arrow',
            selectbackground=COLORS['primary'],
            selectforeground=COLORS['text_white']
        )
    
    def setup_fonts(self):
        """Setup different font styles"""
        base_font = font.Font(family="Segoe UI", size=12)
        
        self.fonts = {
            'normal': base_font,
            'bold': font.Font(family="Segoe UI", size=12, weight='bold'),
            'italic': font.Font(family="Segoe UI", size=12, slant='italic'),
            'bold_italic': font.Font(family="Segoe UI", size=12, weight='bold', slant='italic'),
            'underline': font.Font(family="Segoe UI", size=12, underline=True),
            'bold_underline': font.Font(family="Segoe UI", size=12, weight='bold', underline=True),
            'italic_underline': font.Font(family="Segoe UI", size=12, slant='italic', underline=True),
            'bold_italic_underline': font.Font(family="Segoe UI", size=12, weight='bold', slant='italic', underline=True),
            'main_header': font.Font(family="Segoe UI", size=16, weight='bold'),
            'section_header': font.Font(family="Segoe UI", size=14, weight='bold'),
            'sub_header': font.Font(family="Segoe UI", size=13, weight='bold')
        }
    
    def setup_tags(self):
        """Configure text tags for different formatting styles"""
        # Bold text
        self.widget.tag_configure('bold', font=self.fonts['bold'], foreground=COLORS['text_primary'])
        
        # Italic text  
        self.widget.tag_configure('italic', font=self.fonts['italic'], foreground=COLORS['text_primary'])
        
        # Underline text
        self.widget.tag_configure('underline', font=self.fonts['underline'], foreground=COLORS['text_primary'])
        
        # Combined styles
        self.widget.tag_configure('bold_italic', font=self.fonts['bold_italic'], foreground=COLORS['text_primary'])
        self.widget.tag_configure('bold_underline', font=self.fonts['bold_underline'], foreground=COLORS['text_primary'])
        self.widget.tag_configure('italic_underline', font=self.fonts['italic_underline'], foreground=COLORS['text_primary'])
        self.widget.tag_configure('bold_italic_underline', font=self.fonts['bold_italic_underline'], foreground=COLORS['text_primary'])
        
        # Markdown headers (based on # symbols only)
        self.widget.tag_configure('main_header', font=self.fonts['main_header'], foreground=COLORS['primary'])
        self.widget.tag_configure('section_header', font=self.fonts['section_header'], foreground=COLORS['primary'])
        self.widget.tag_configure('sub_header', font=self.fonts['sub_header'], foreground=COLORS['text_primary'])
    
    def insert_formatted_text(self, raw_markdown_text, clear_first=True):
        """Insert text with markdown formatting - stores raw and displays formatted"""
        
        # STEP 1: Store the raw markdown text (with ** and * tags)
        self._raw_markdown_text = raw_markdown_text
        print(f"💾 Stored raw markdown: {len(raw_markdown_text)} chars")
        print(f"📝 Raw preview: {raw_markdown_text[:100]}...")
        
        # STEP 2: Convert markdown to clean display text and apply formatting
        self._formatted_display_text = self._remove_markdown_tags(raw_markdown_text)
        print(f"🎨 Created display text: {len(self._formatted_display_text)} chars")
        print(f"👁️ Display preview: {self._formatted_display_text[:100]}...")
        
        # STEP 3: Display the formatted text with visual styling
        self.widget.config(state='normal')
        
        try:
            if clear_first:
                self.widget.delete("1.0", tk.END)
            
            # Parse and insert with formatting applied
            self._parse_and_insert_with_formatting(raw_markdown_text)
            
            # Scroll to top
            self.widget.see("1.0")
            
        finally:
            # Return to read-only state
            self.widget.config(state='disabled')
            print("✅ Text displayed with formatting applied")
    
    def _remove_markdown_tags(self, text):
        """Remove markdown formatting tags to create clean display text"""
        clean_text = text
        
        # Remove markdown formatting (order matters!)
        clean_text = re.sub(r'\*\*\*(.+?)\*\*\*', r'\1', clean_text)  # ***bold italic***
        clean_text = re.sub(r'\*\*(.+?)\*\*', r'\1', clean_text)      # **bold**
        clean_text = re.sub(r'___(.+?)___', r'\1', clean_text)        # ___bold underline___
        clean_text = re.sub(r'__(.+?)__', r'\1', clean_text)          # __underline__
        clean_text = re.sub(r'_(.+?)_', r'\1', clean_text)            # _italic_
        clean_text = re.sub(r'\*(.+?)\*', r'\1', clean_text)          # *italic*
        clean_text = re.sub(r'^#+\s*', '', clean_text, flags=re.MULTILINE)  # # headers
        
        return clean_text
    
    def _parse_and_insert_with_formatting(self, raw_text):
        """Parse raw markdown and insert with visual formatting applied"""
        lines = raw_text.split('\n')
        
        for line_num, line in enumerate(lines):
            if line_num > 0:
                self.widget.insert(tk.END, '\n')
            
            # Check for markdown headers only (based on # symbols)
            header_level = self._get_markdown_header_level(line)
            if header_level > 0:
                clean_line = re.sub(r'^#+\s*', '', line)
                
                if header_level == 1:
                    self.widget.insert(tk.END, clean_line, 'main_header')
                elif header_level == 2:
                    self.widget.insert(tk.END, clean_line, 'section_header')
                else:  # 3 or more
                    self.widget.insert(tk.END, clean_line, 'sub_header')
                continue
            
            # Process inline formatting for regular text
            self._process_inline_formatting(line)
    
    def _get_markdown_header_level(self, line):
        """Get the header level based on # symbols (0 = not a header)"""
        stripped = line.strip()
        if not stripped.startswith('#'):
            return 0
            
        # Count consecutive # symbols at the start
        level = 0
        for char in stripped:
            if char == '#':
                level += 1
            else:
                break
        
        # Must be followed by space or end of line to be valid header
        if level < len(stripped) and stripped[level] != ' ':
            return 0
            
        return level
    
    def _process_inline_formatting(self, line):
        """Process inline markdown formatting and apply visual styles"""
        current_pos = 0
        
        # Pattern to match all formatting types (most specific first)
        pattern = r'(\*\*\*(.+?)\*\*\*|\*\*(.+?)\*\*|___(.+?)___|__(.+?)__|_(.+?)_|\*(.+?)\*)'
        
        for match in re.finditer(pattern, line):
            # Insert text before the match (no formatting)
            if match.start() > current_pos:
                self.widget.insert(tk.END, line[current_pos:match.start()])
            
            # Determine formatting type and content
            full_match = match.group(0)
            content = None
            tag = 'normal'
            
            if full_match.startswith('***') and full_match.endswith('***'):
                content = match.group(2)
                tag = 'bold_italic'
            elif full_match.startswith('**') and full_match.endswith('**'):
                content = match.group(3)
                tag = 'bold'
            elif full_match.startswith('___') and full_match.endswith('___'):
                content = match.group(4)
                tag = 'bold_underline'
            elif full_match.startswith('__') and full_match.endswith('__'):
                content = match.group(5)
                tag = 'underline'
            elif full_match.startswith('_') and full_match.endswith('_'):
                content = match.group(6)
                tag = 'italic'
            elif full_match.startswith('*') and full_match.endswith('*'):
                content = match.group(7)
                tag = 'italic'
            
            # Insert formatted content (without the markdown tags)
            if content:
                self.widget.insert(tk.END, content, tag)
            
            current_pos = match.end()
        
        # Insert remaining text
        if current_pos < len(line):
            self.widget.insert(tk.END, line[current_pos:])
    
    # ============================================================================
    # PUBLIC API METHODS
    # ============================================================================
    
    def get_text(self):
        """Get clean display text (without markdown tags)"""
        return self._formatted_display_text
    
    def get_raw_markdown(self):
        """Get raw markdown text (with ** and * tags) for PDF export"""
        return self._raw_markdown_text
    
    def clear(self):
        """Clear all content"""
        self._raw_markdown_text = ""
        self._formatted_display_text = ""
        
        self.widget.config(state='normal')
        self.widget.delete("1.0", tk.END)
        self.widget.config(state='disabled')
        
        print("🧹 Widget cleared - both raw and display text reset")
    
    def has_content(self):
        """Check if widget has any content"""
        return bool(self._raw_markdown_text.strip())
    
    def get_content_info(self):
        """Get information about stored content (for debugging)"""
        return {
            'raw_length': len(self._raw_markdown_text),
            'display_length': len(self._formatted_display_text),
            'has_markdown': bool(re.search(r'[\*_#]', self._raw_markdown_text)),
            'raw_preview': self._raw_markdown_text[:100] + "..." if len(self._raw_markdown_text) > 100 else self._raw_markdown_text,
            'display_preview': self._formatted_display_text[:100] + "..." if len(self._formatted_display_text) > 100 else self._formatted_display_text
        }
    
    # ============================================================================
    # WIDGET DELEGATION METHODS
    # ============================================================================
    
    def pack(self, **kwargs):
        return self.widget.pack(**kwargs)
    
    def grid(self, **kwargs):
        return self.widget.grid(**kwargs)
    
    def place(self, **kwargs):
        return self.widget.place(**kwargs)
    
    def config(self, **kwargs):
        # Block attempts to make widget editable
        if 'state' in kwargs and kwargs['state'] != 'disabled':
            print("⚠️ Blocked attempt to make read-only widget editable")
            kwargs.pop('state')
        return self.widget.config(**kwargs)
    
    def configure(self, **kwargs):
        # Block attempts to make widget editable
        if 'state' in kwargs and kwargs['state'] != 'disabled':
            print("⚠️ Blocked attempt to make read-only widget editable")
            kwargs.pop('state')
        return self.widget.configure(**kwargs)
    
    def bind(self, sequence, func):
        return self.widget.bind(sequence, func)
    
    def see(self, index):
        return self.widget.see(index)