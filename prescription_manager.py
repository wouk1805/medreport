# prescription_manager.py
# ============================================================================
# XML-Based Prescription Detection and PDF Generation
# ============================================================================

import tkinter as tk
from tkinter import ttk
import re
import os
import xml.etree.ElementTree as ET
from datetime import datetime
from config import COLORS

# PDF generation imports
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.colors import black
from reportlab.lib.enums import TA_LEFT, TA_CENTER

class PrescriptionManager:
    """Simplified prescription detection and PDF generation"""
    
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.prescription_frame = None
        self.prescription_label = None
        self.status_label = None
        self.prescription_buttons = []
        self.current_summary = ""
        self.prescription_data = None
        
        # Ensure prescriptions directory exists
        self.prescriptions_dir = "prescriptions"
        if not os.path.exists(self.prescriptions_dir):
            os.makedirs(self.prescriptions_dir)
            print(f"📁 Created prescriptions directory: {self.prescriptions_dir}")
        
        self.create_prescription_section()
    
    def create_prescription_section(self):
        """Create the prescription section"""
        self.prescription_frame = tk.Frame(self.parent_frame, bg=COLORS['bg_card'])
        self.prescription_frame.pack(fill='x', padx=(30, 40), pady=(15, 25))
        
        # Title container
        title_container = tk.Frame(self.prescription_frame, bg=COLORS['bg_card'])
        title_container.pack(side='left')

        # Symbol and title
        tk.Label(
            title_container, 
            text="💊", 
            font=("Segoe UI", 16), 
            bg=COLORS['bg_card'], 
            fg=COLORS['accent_yellow']
        ).pack(side='left', padx=(0, 8))

        self.prescription_label = tk.Label(
            title_container, 
            text="Recommended Prescriptions", 
            font=("Segoe UI", 13, "bold"),
            bg=COLORS['bg_card'], 
            fg=COLORS['text_primary']
        )
        self.prescription_label.pack(side='left')

        # Status label
        self.status_label = tk.Label(
            self.prescription_frame,
            text="None",
            font=("Segoe UI", 12),
            bg=COLORS['bg_card'],
            fg=COLORS['text_muted']
        )
        self.status_label.pack(side='right')

        print("💊 Prescription section created")
    
    def check_summary_for_prescription(self, summary_text):
        """Check if summary contains XML prescription tags and return cleaned text"""
        self.current_summary = summary_text
        self.prescription_data = []
        
        # Find all prescription XML blocks
        matches = re.findall(r'<prescription>(.*?)</prescription>', summary_text, re.DOTALL | re.IGNORECASE)
        full_xml_blocks = re.findall(r'<prescription>.*?</prescription>', summary_text, re.DOTALL | re.IGNORECASE)
        
        for i, match in enumerate(matches):
            full_xml = f"<prescription>{match}</prescription>"
            
            print(f"💊 Found prescription XML block {i+1}:")
            print(f"📋 {full_xml}")
            print("-" * 50)
            
            parsed = self._parse_prescription_xml(full_xml)
            if parsed:
                self.prescription_data.append(parsed)
                print(f"💊 Parsed prescription {i+1}: {parsed['title']}")

        # Remove prescription XML blocks from summary
        cleaned_summary = summary_text
        for xml_block in full_xml_blocks:
            cleaned_summary = cleaned_summary.replace(xml_block, "").strip()
        
        # Clean up extra whitespace
        cleaned_summary = re.sub(r'\n\s*\n\s*\n', '\n\n', cleaned_summary)
        cleaned_summary = cleaned_summary.strip()

        if self.prescription_data:
            print(f"💊 {len(self.prescription_data)} prescription(s) parsed successfully.")
            self.update_prescription_ui(True)
        else:
            print("💊 No valid prescriptions found.")
            self.update_prescription_ui(False)
        
        return cleaned_summary
    
    def _parse_prescription_xml(self, xml_string):
        """Parse prescription XML and extract data"""
        try:
            xml_string = xml_string.strip()
            root = ET.fromstring(xml_string)
            
            # Extract elements
            title_elem = root.find('title')
            content_elem = root.find('content')
            patient_elem = root.find('patient')
            context_elem = root.find('context')
            
            # Extract text with defaults
            title = title_elem.text.strip() if title_elem is not None and title_elem.text else "Prescription"
            content = content_elem.text.strip() if content_elem is not None and content_elem.text else ""
            patient = patient_elem.text.strip() if patient_elem is not None and patient_elem.text else ""
            context = context_elem.text.strip() if context_elem is not None and context_elem.text else ""
            
            if title_elem is None or content_elem is None:
                print("⚠️ Missing title or content in prescription XML")
                return None
            
            return {
                'title': title,
                'content': content,
                'patient': patient,
                'context': context
            }
            
        except ET.ParseError as e:
            print(f"❌ XML parsing error: {e}")
            return None
        except Exception as e:
            print(f"❌ Error parsing prescription XML: {e}")
            return None
    
    def update_prescription_ui(self, has_prescription):
        """Update the prescription UI based on detection status"""
        # Clear previous buttons
        for btn in self.prescription_buttons:
            btn.destroy()
        self.prescription_buttons.clear()

        if has_prescription and self.prescription_data:
            self.status_label.pack_forget()

            for idx, prescription in enumerate(self.prescription_data):
                title = prescription['title']
                button_text = title[:30] + "..." if len(title) > 30 else title

                btn = ttk.Button(
                    self.prescription_frame,
                    text=button_text,
                    command=lambda i=idx: self.generate_prescription_pdf(i),
                    style="ClearButton.TButton"
                )
                btn.configure(cursor='hand2')
                btn.pack(side='right', padx=(8, 0))

                self.prescription_buttons.append(btn)

            print(f"💊 {len(self.prescription_data)} button(s) added to UI.")
        else:
            self.status_label.pack(side='right')
            print("💊 No prescription detected - showing 'None'")
    
    def generate_prescription_pdf(self, index=0):
        """Generate simplified prescription PDF"""
        if not self.prescription_data or index >= len(self.prescription_data):
            print("❌ Invalid prescription index or no data available")
            return

        prescription = self.prescription_data[index]

        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_title = re.sub(r'[^\w\s-]', '', prescription['title']).strip()
            safe_title = re.sub(r'[\s]+', '_', safe_title)
            filename = f"{safe_title}_{timestamp}.pdf"
            filepath = os.path.join(self.prescriptions_dir, filename)

            print(f"💊 Generating prescription PDF: {filepath}")
            success = self._create_prescription_pdf(filepath, prescription)

            if success:
                print(f"✅ Prescription PDF created: {filepath}")
                try:
                    self._open_pdf(filepath)
                except Exception as e:
                    print(f"⚠️ Could not open PDF automatically: {e}")
            else:
                print("❌ Failed to create prescription PDF")

        except Exception as e:
            print(f"❌ Error generating prescription PDF: {e}")
    
    def _create_prescription_pdf(self, filepath, prescription_data):
        """Create simplified prescription PDF"""
        try:
            doc = SimpleDocTemplate(
                filepath,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )
            
            # Simplified styles
            styles = getSampleStyleSheet()
            
            title_style = ParagraphStyle(
                name='PrescriptionTitle',
                parent=styles['Title'],
                fontSize=18,
                spaceAfter=24,
                alignment=TA_CENTER,
                textColor=black,
                fontName='Helvetica-Bold'
            )
            
            content_style = ParagraphStyle(
                name='ContentBold',
                parent=styles['Normal'],
                fontSize=12,
                spaceAfter=12,
                alignment=TA_LEFT,
                fontName='Helvetica-Bold',
                leading=16
            )
            
            header_style = ParagraphStyle(
                name='Header',
                parent=styles['Normal'],
                fontSize=11,
                spaceAfter=16,
                alignment=TA_CENTER,
                fontName='Helvetica-Oblique'
            )
            
            # Build content
            story = []
            
            # Header
            timestamp = datetime.now().strftime("%B %d, %Y at %H:%M")
            story.append(Paragraph(f"Generated on {timestamp}", header_style))
            story.append(Spacer(1, 12))
            
            # Title
            story.append(Paragraph("Prescription", title_style))
            story.append(Spacer(1, 12))
            
            # Patient info
            if prescription_data.get('patient'):
                story.append(Paragraph(f"Patient: {prescription_data['patient']}", styles['Normal']))
                story.append(Spacer(1, 12))
            
            # Content
            content_lines = prescription_data['content'].split('\n')
            for line in content_lines:
                if line.strip():
                    story.append(Paragraph(line.strip(), content_style))
                else:
                    story.append(Spacer(1, 6))
            
            # Context
            if prescription_data.get('context'):
                story.append(Paragraph(f"Context: {prescription_data['context']}", styles['Normal']))
                story.append(Spacer(1, 12))
            
            # Signature
            story.append(Spacer(1, 24))
            story.append(Paragraph("Doctor Kim", header_style))
            
            doc.build(story)
            return True
            
        except Exception as e:
            print(f"❌ Error creating prescription PDF: {e}")
            return False
    
    def _open_pdf(self, filepath):
        """Open PDF file with default system application"""
        import subprocess
        import platform
        
        try:
            if platform.system() == 'Darwin':  # macOS
                subprocess.call(('open', filepath))
            elif platform.system() == 'Windows':  # Windows
                os.startfile(filepath)
            else:  # Linux
                subprocess.call(('xdg-open', filepath))
        except Exception as e:
            print(f"❌ Could not open PDF: {e}")
            raise
    
    def reset_prescription_status(self):
        """Reset prescription status to default"""
        self.prescription_data = None
        self.current_summary = ""
        
        # Clear all buttons
        for button in self.prescription_buttons:
            button.destroy()
        self.prescription_buttons = []
        
        self.status_label.config(text="None")
        self.status_label.pack(side='right')
        
        print("💊 Prescription status reset to 'None'")
    
    def cleanup(self):
        """Cleanup prescription manager"""
        if self.prescription_frame:
            self.prescription_frame.destroy()
        print("🧹 Prescription manager cleaned up")