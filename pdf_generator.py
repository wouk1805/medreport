# pdf_generator.py
# ============================================================================
# PDF Generator that uses raw markdown from RichTextWidget
# ============================================================================

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch
from reportlab.lib.colors import black, blue, red, green
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from tkinter import filedialog
import tkinter as tk
import os
import subprocess
import platform
import re
from datetime import datetime

def open_pdf(file_path):
    try:
        if platform.system() == 'Darwin':  # macOS
            subprocess.call(('open', file_path))
        elif platform.system() == 'Windows':  # Windows
            os.startfile(file_path)
        else:  # Linux and other Unix systems
            subprocess.call(('xdg-open', file_path))
        return True
    except Exception as e:
        print(f"Could not open PDF automatically: {e}")
        return False

def create_medical_styles():
    """Create professional medical report styles with enhanced design"""
    styles = getSampleStyleSheet()
    
    # Enhanced Document title with better design
    styles.add(ParagraphStyle(
        name='DocumentTitle',
        parent=styles['Title'],
        fontSize=20,
        spaceAfter=24,
        spaceBefore=16,
        alignment=TA_CENTER,
        textColor=black,  # Changed from blue to black
        fontName='Helvetica-Bold',
        borderWidth=2,
        borderColor=black,
        borderPadding=12,
        backColor='#F8F9FA'  # Light gray background
    ))
    
    # Main headers (# headers)
    styles.add(ParagraphStyle(
        name='MainHeader',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=12,
        spaceBefore=16,
        textColor=black,  # Changed from blue to black
        fontName='Helvetica-Bold',
        borderWidth=1,
        borderColor=black,
        borderPadding=8
    ))
    
    # Section headers (## headers)
    styles.add(ParagraphStyle(
        name='SectionHeader',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=8,
        spaceBefore=12,
        textColor=black,
        fontName='Helvetica-Bold'
    ))
    
    # Medical body text
    styles.add(ParagraphStyle(
        name='MedicalBody',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=6,
        spaceBefore=3,
        alignment=TA_LEFT,
        fontName='Helvetica',
        leading=14
    ))
    
    # Enhanced generation info with better styling
    styles.add(ParagraphStyle(
        name='GenerationInfo',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=20,
        spaceBefore=12,
        alignment=TA_CENTER,
        fontName='Helvetica',
        textColor=black,
        borderWidth=1,
        borderColor=black,
        borderPadding=8
    ))
    
    return styles

def convert_markdown_to_reportlab(markdown_text):
    """Convert markdown text to ReportLab-compatible XML"""
    print(f"🔧 Converting markdown to ReportLab format...")
    print(f"📝 Input length: {len(markdown_text)} characters")
    
    # Start with the original text
    xml_text = markdown_text
    
    # Escape XML characters first (but preserve our formatting)
    xml_text = xml_text.replace('&', '&amp;')
    xml_text = xml_text.replace('<', '&lt;')
    xml_text = xml_text.replace('>', '&gt;')
    
    # Convert markdown headers (most specific first)
    xml_text = re.sub(r'^### (.+)$', r'<para style="SectionHeader">\1</para>', xml_text, flags=re.MULTILINE)
    xml_text = re.sub(r'^## (.+)$', r'<para style="SectionHeader">\1</para>', xml_text, flags=re.MULTILINE)
    xml_text = re.sub(r'^# (.+)$', r'<para style="MainHeader">\1</para>', xml_text, flags=re.MULTILINE)
    
    # Convert inline formatting (order is important!)
    # Bold + italic combination first
    xml_text = re.sub(r'\*\*\*(.+?)\*\*\*', r'<b><i>\1</i></b>', xml_text)
    
    # Bold + underline combination
    xml_text = re.sub(r'___(.+?)___', r'<b><u>\1</u></b>', xml_text)
    
    # Individual formatting
    xml_text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', xml_text)  # **bold**
    xml_text = re.sub(r'__(.+?)__', r'<u>\1</u>', xml_text)      # __underline__
    xml_text = re.sub(r'_(.+?)_', r'<i>\1</i>', xml_text)        # _italic_
    xml_text = re.sub(r'\*(.+?)\*', r'<i>\1</i>', xml_text)      # *italic*
    
    print(f"✅ Conversion complete")
    print(f"🎨 Output preview: {xml_text[:200]}..." if len(xml_text) > 200 else f"🎨 Output: {xml_text}")
    
    return xml_text

def create_pdf_from_markdown(markdown_text, output_filename):
    """Create professional PDF from markdown text"""
    try:
        print(f"📄 Creating PDF from markdown...")
        
        # Create document with professional margins
        doc = SimpleDocTemplate(
            output_filename, 
            pagesize=A4,
            rightMargin=72,  # 1 inch
            leftMargin=72,   # 1 inch
            topMargin=72,    # 1 inch
            bottomMargin=72  # 1 inch
        )
        
        # Get medical styles
        styles = create_medical_styles()
        story = []
        
        # Convert markdown to XML
        xml_content = convert_markdown_to_reportlab(markdown_text)
        
        # Process the content
        process_content_to_story(xml_content, story, styles)
        
        # Build the PDF
        doc.build(story)
        print("✅ PDF created successfully with formatting preserved")
        return True
        
    except Exception as e:
        print(f"❌ Error creating PDF: {e}")
        import traceback
        traceback.print_exc()
        return False

def process_content_to_story(xml_content, story, styles):
    """Process XML content and add to story"""
    
    # Split into paragraphs
    paragraphs = xml_content.split('\n\n')
    
    for para_text in paragraphs:
        para_text = para_text.strip()
        if not para_text:
            continue
        
        # Split into lines
        lines = para_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                story.append(Spacer(1, 6))
                continue
            
            try:
                # Check for special paragraph styles
                if '<para style="MainHeader">' in line:
                    # Extract content from header tag
                    content = re.sub(r'<para style="MainHeader">(.+?)</para>', r'\1', line)
                    story.append(Paragraph(content, styles['MainHeader']))
                    story.append(Spacer(1, 8))
                    
                elif '<para style="SectionHeader">' in line:
                    # Extract content from section header tag
                    content = re.sub(r'<para style="SectionHeader">(.+?)</para>', r'\1', line)
                    story.append(Paragraph(content, styles['SectionHeader']))
                    story.append(Spacer(1, 6))
                    
                else:
                    # Regular paragraph with inline formatting
                    story.append(Paragraph(line, styles['MedicalBody']))
                    story.append(Spacer(1, 4))
                    
            except Exception as e:
                print(f"⚠️ Error processing line: {e}")
                # Fallback: remove all XML tags and use plain text
                plain_line = re.sub(r'<[^>]*>', '', line)
                if plain_line.strip():
                    story.append(Paragraph(plain_line, styles['MedicalBody']))
                    story.append(Spacer(1, 4))

def create_simple_pdf(plain_text, output_filename):
    """Create basic PDF from plain text"""
    try:
        print(f"📄 Creating PDF from plain text...")
        
        doc = SimpleDocTemplate(output_filename, pagesize=A4)
        styles = create_medical_styles()
        story = []
        
        # Process plain text into paragraphs
        paragraphs = plain_text.split('\n\n')
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if paragraph:
                # Only check for explicit markdown headers (starting with #)
                if paragraph.startswith('#'):
                    # This is a markdown header that wasn't converted - treat as header
                    clean_header = paragraph.lstrip('#').strip()
                    header_level = len(paragraph) - len(paragraph.lstrip('#'))
                    
                    if header_level == 1:
                        story.append(Paragraph(f'<b>{clean_header}</b>', styles['MainHeader']))
                    else:
                        story.append(Paragraph(f'<b>{clean_header}</b>', styles['SectionHeader']))
                else:
                    # Regular paragraph
                    story.append(Paragraph(paragraph, styles['MedicalBody']))
                story.append(Spacer(1, 6))
        
        doc.build(story)
        print("✅ PDF created successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error creating PDF: {e}")
        return False

# Utility functions
def generate_default_filename(prefix="Medical_report"):
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{current_time}.pdf"

def get_save_path(default_filename=None, initial_dir=None, title="Save PDF as..."):
    root = tk.Tk()
    root.withdraw()
    
    if initial_dir is None:
        initial_dir = os.getcwd()
    if default_filename is None:
        default_filename = generate_default_filename()
    
    try:
        output_path = filedialog.asksaveasfilename(
            initialdir=initial_dir,
            initialfile=default_filename,
            defaultextension=".pdf",
            filetypes=[("Fichiers PDF", "*.pdf"), ("Tous les fichiers", "*.*")],
            title=title
        )
        return output_path if output_path else None
    finally:
        root.destroy()

# Export function
def rich_text_to_pdf_with_dialog(rich_text_widget, 
                                default_filename=None, 
                                initial_dir=None, 
                                auto_open=True,
                                dialog_title="Save the medical report as..."):
    """Export rich text widget to PDF with formatting preserved"""
    
    if default_filename is None:
        default_filename = generate_default_filename()
    
    # Get save path from user
    output_path = get_save_path(default_filename, initial_dir, dialog_title)
    
    if not output_path:
        return {
            'success': False,
            'file_path': None,
            'cancelled': True,
            'message': 'Cancelled by user'
        }
    
    print(f"📄 Starting PDF export to: {output_path}")
    
    # Get the raw markdown text from the widget
    try:
        raw_markdown = rich_text_widget.get_raw_markdown()
        print(f"💾 Retrieved raw markdown: {len(raw_markdown)} characters")
        print(f"📝 Markdown preview: {raw_markdown[:100]}...")
        
        if raw_markdown and raw_markdown.strip():
            # Use the raw markdown with formatting tags
            pdf_created = create_pdf_from_markdown(raw_markdown, output_path)
        else:
            print("⚠️ No raw markdown available, using display text")
            display_text = rich_text_widget.get_text()
            pdf_created = create_simple_pdf(display_text, output_path)
            
    except AttributeError as e:
        print(f"⚠️ Widget doesn't support get_raw_markdown(): {e}")
        # Fallback to display text
        display_text = rich_text_widget.get_text()
        pdf_created = create_simple_pdf(display_text, output_path)
    
    if not pdf_created:
        return {
            'success': False,
            'file_path': output_path,
            'cancelled': False,
            'message': 'Failed to create PDF file'
        }
    
    # Open PDF if requested
    opened = True
    if auto_open:
        opened = open_pdf(output_path)
    
    return {
        'success': True,
        'file_path': output_path,
        'cancelled': False,
        'message': f'PDF with formatting created successfully{" and opened" if opened else ""}: {output_path}'
    }