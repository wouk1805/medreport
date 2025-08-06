# file_operations.py
# ============================================================================
# File Import/Export Operations
# ============================================================================

import os
from tkinter import filedialog
from datetime import datetime
from pdf_generator import rich_text_to_pdf_with_dialog

class FileOperationsManager:
    """File import/export operations manager"""
    
    def __init__(self):
        self.imported_document_content = ""
    
    def import_pdf_document(self, summary_text_widget=None):
        """Import a PDF document and return its content with filename header"""
        try:
            # Try to import PyMuPDF
            try:
                import fitz  # PyMuPDF
            except ImportError:
                error_msg = "PyMuPDF library is required to import PDF files.\n\nPlease install it with:\npip install PyMuPDF"
                print("❌ PyMuPDF not installed.")
                if summary_text_widget:
                    error_text = "❌ **Import Error**\n\nPyMuPDF library is required to import PDF files.\n\nPlease install it with:\n```\npip install PyMuPDF\n```"
                    summary_text_widget.insert_formatted_text(error_text, clear_first=True)
                return False, "", error_msg
            
            # Open file dialog
            file_path = filedialog.askopenfilename(
                title="Import Document",
                filetypes=[
                    ("PDF files", "*.pdf"),
                    ("All files", "*.*")
                ],
                initialdir=os.getcwd()
            )
            
            if not file_path:
                print("ℹ️ Import cancelled by user")
                return False, "", "Import cancelled by user"
            
            # Extract filename
            filename = os.path.basename(file_path)
            print(f"📄 Importing document: {file_path}")
            
            # Read PDF content
            doc = fitz.open(file_path)
            formatted_content = ""
            
            for page_num in range(doc.page_count):
                page = doc.load_page(page_num)
                text_dict = page.get_text("dict")
                page_content = self._extract_formatted_text_from_dict(text_dict)
                
                if page_content.strip():
                    formatted_content += page_content
                    if page_num < doc.page_count - 1:
                        formatted_content += "\n\n---\n\n"
            
            doc.close()
            
            if not formatted_content.strip():
                error_msg = "No text content found in PDF"
                print(f"⚠️ {error_msg}")
                if summary_text_widget:
                    error_text = f"⚠️ **Import Warning**\n\n{error_msg}"
                    summary_text_widget.insert_formatted_text(error_text, clear_first=True)
                return False, "", error_msg
            
            # Create formatted content with filename header
            final_content = f"*Imported from: {filename}*\n\n" + formatted_content.strip()
            
            # Store the imported content
            self.imported_document_content = final_content
            
            # Display if widget provided
            if summary_text_widget:
                summary_text_widget.insert_formatted_text(final_content, clear_first=True)
            
            success_msg = f"Document imported successfully: {len(final_content)} characters"
            print(f"✅ {success_msg}")
            
            return True, final_content, success_msg
            
        except Exception as e:
            error_msg = f"Error importing document: {str(e)}"
            print(f"❌ {error_msg}")
            if summary_text_widget:
                error_text = f"❌ **Import Error**\n\nFailed to import document:\n{str(e)}"
                summary_text_widget.insert_formatted_text(error_text, clear_first=True)
            return False, "", error_msg
    
    def _extract_formatted_text_from_dict(self, text_dict):
        """Extract text with formatting from PyMuPDF text dictionary"""
        formatted_text = ""
        
        try:
            for block in text_dict.get("blocks", []):
                if "lines" not in block:  # Skip image blocks
                    continue
                
                block_text = ""
                for line in block["lines"]:
                    line_text = ""
                    
                    for span in line["spans"]:
                        text = span.get("text", "")
                        if not text.strip():
                            continue
                        
                        # Get font information
                        font_flags = span.get("flags", 0)
                        font_name = span.get("font", "").lower()
                        
                        # Determine formatting
                        is_bold = bool(font_flags & 2**4) or "bold" in font_name
                        is_italic = bool(font_flags & 2**1) or "italic" in font_name or "oblique" in font_name
                        
                        # Apply markdown formatting
                        formatted_span = text
                        if is_bold and is_italic:
                            formatted_span = f"***{text}***"
                        elif is_bold:
                            formatted_span = f"**{text}**"
                        elif is_italic:
                            formatted_span = f"*{text}*"
                        
                        line_text += formatted_span
                    
                    if line_text.strip():
                        block_text += line_text + "\n"
                
                if block_text.strip():
                    formatted_text += block_text + "\n"
        
        except Exception as e:
            print(f"⚠️ Error extracting formatting, using plain text: {e}")
            # Fallback to plain text extraction
            try:
                for block in text_dict.get("blocks", []):
                    if "lines" not in block:
                        continue
                    for line in block["lines"]:
                        for span in line["spans"]:
                            text = span.get("text", "")
                            if text.strip():
                                formatted_text += text
                        formatted_text += "\n"
                    formatted_text += "\n"
            except:
                formatted_text = "Error extracting text content"
        
        return formatted_text
    
    def export_to_pdf(self, rich_text_widget, default_filename=None, dialog_title="Export Medical Report"):
        """Export rich text widget content to PDF"""
        try:
            # Check if there's content to export
            report_content = rich_text_widget.get_text()
            if not report_content or len(report_content.strip()) < 50:
                print("⚠️ No substantial report content to export")
                return {
                    'success': False,
                    'file_path': None,
                    'cancelled': False,
                    'message': 'No substantial content to export'
                }
            
            # Generate default filename if not provided
            if not default_filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                default_filename = f"MedReport_{timestamp}.pdf"
            
            print(f"📄 Starting PDF export with filename: {default_filename}")
            
            # Use the rich text PDF generator
            result = rich_text_to_pdf_with_dialog(
                rich_text_widget=rich_text_widget,
                default_filename=default_filename,
                dialog_title=dialog_title,
                auto_open=True
            )
            
            if result['success']:
                print(f"✅ {result['message']}")
            elif result['cancelled']:
                print("ℹ️ Export cancelled by user")
            else:
                print(f"❌ {result['message']}")
            
            return result
                
        except Exception as e:
            error_msg = f"Export failed: {str(e)}"
            print(f"❌ {error_msg}")
            return {
                'success': False,
                'file_path': None,
                'cancelled': False,
                'message': error_msg
            }
    
    def get_imported_content(self):
        """Get the current imported document content"""
        return self.imported_document_content
    
    def clear_imported_content(self):
        """Clear the imported document content"""
        self.imported_document_content = ""
        print("🧹 Cleared imported document content")
    
    def reset_imported_content(self):
        """Reset imported content (alias for clear)"""
        self.clear_imported_content()
        print("🔄 Reset imported document content")
    
    def has_imported_content(self):
        """Check if there's imported content"""
        return bool(self.imported_document_content.strip())
    
    def load_custom_report_format(self, custom_file="custom_report_format.txt"):
        """Load custom report format from file"""
        try:
            if os.path.exists(custom_file):
                with open(custom_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        success_msg = f"Custom report format loaded: {len(content)} characters"
                        print(f"✅ {success_msg}")
                        return True, content, success_msg
                    else:
                        error_msg = "Custom report format file is empty"
                        print(f"⚠️ {error_msg}")
                        return False, "", error_msg
            else:
                error_msg = "Custom report format file not found"
                print(f"ℹ️ {error_msg}")
                return False, "", error_msg
        except Exception as e:
            error_msg = f"Error loading custom report format: {str(e)}"
            print(f"❌ {error_msg}")
            return False, "", error_msg