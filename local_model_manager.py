# local_model_manager.py
# ============================================================================
# Local Gemma 3n Dual Model Manager for MedReport - Audio + Report Models
# ============================================================================

import torch
import threading
import asyncio
from concurrent.futures import ThreadPoolExecutor
import os
import gc
import sys
import traceback
from enum import Enum

# Import config if available, otherwise use defaults
try:
    from config import COLORS
except ImportError:
    print("⚠️ Config not found, using default colors")
    COLORS = {
        'accent_info': '#0284C7',
        'accent_success': '#059669', 
        'accent_danger': '#DC2626',
        'accent_warning': '#F59E0B'
    }

class ModelType(Enum):
    """Enum for different model types"""
    AUDIO = "audio"
    REPORT = "report"

class LocalModelManager:
    """Manages dual local Gemma 3n models using Unsloth for MedReport"""
    
    def __init__(self, ui_callbacks=None, debug_mode=False):
        self.ui_callbacks = ui_callbacks or {}
        self.debug_mode = debug_mode
        
        # Model configurations
        self.model_configs = {
            ModelType.AUDIO: {
                'name': "wouk1805/medreport_audio",
                'description': "Audio transcription model"
            },
            ModelType.REPORT: {
                'name': "wouk1805/medreport_report", 
                'description': "Medical report generation model"
            }
        }
        
        # Model instances
        self.models = {
            ModelType.AUDIO: {'model': None, 'processor': None, 'loaded': False},
            ModelType.REPORT: {'model': None, 'processor': None, 'loaded': False}
        }
        
        # Thread pool for model operations
        self.executor = ThreadPoolExecutor(max_workers=3, thread_name_prefix="DualModel")
        
        # Loading locks for thread safety
        self.loading_locks = {
            ModelType.AUDIO: threading.Lock(),
            ModelType.REPORT: threading.Lock()
        }
        
        print(f"🤖 Dual LocalModelManager initialized")
        print(f"   📻 Audio model: {self.model_configs[ModelType.AUDIO]['name']}")
        print(f"   📄 Report model: {self.model_configs[ModelType.REPORT]['name']}")
        
        if self.debug_mode:
            self._print_system_info()
    
    def _print_system_info(self):
        """Print system information for debugging"""
        print("\n" + "="*60)
        print("🔍 SYSTEM DEBUG INFO")
        print("="*60)
        print(f"Python version: {sys.version}")
        print(f"PyTorch version: {torch.__version__}")
        print(f"CUDA available: {torch.cuda.is_available()}")
        
        if torch.cuda.is_available():
            print(f"CUDA version: {torch.version.cuda}")
            print(f"GPU count: {torch.cuda.device_count()}")
            for i in range(torch.cuda.device_count()):
                props = torch.cuda.get_device_properties(i)
                print(f"GPU {i}: {props.name}")
                print(f"  Total memory: {props.total_memory / 1e9:.1f}GB")
        
        print("="*60)
    
    def _load_single_model(self, model_type: ModelType):
        """Load a specific model using Unsloth"""
        with self.loading_locks[model_type]:
            if self.models[model_type]['loaded']:
                print(f"✅ {model_type.value.capitalize()} model already loaded")
                return True
            
            model_name = self.model_configs[model_type]['name']
            model_desc = self.model_configs[model_type]['description']
            
            print(f"🔄 Loading {model_desc}: {model_name}")
            self._update_status(f"Loading {model_type.value} model...", COLORS['accent_info'])
            
            try:
                # Import Unsloth (lazy import to handle missing dependency gracefully)
                try:
                    from unsloth import FastModel
                    if self.debug_mode:
                        print(f"✅ Unsloth imported for {model_type.value} model")
                except ImportError as e:
                    raise Exception(f"Unsloth not installed. Please install with: pip install unsloth\nError: {e}")
                
                # Try loading with different quantization strategies
                print(f"📥 Loading {model_type.value} model: {model_name}")
                
                try:
                    # Strategy 1: 4-bit quantization (requires latest bitsandbytes)
                    print(f"🔄 Trying 4-bit quantization for {model_type.value}...")
                    model, processor = FastModel.from_pretrained(
                        model_name=model_name,
                        dtype=None,
                        max_seq_length=2048,
                        load_in_4bit=True,
                        full_finetuning=False,
                    )
                    print(f"✅ {model_type.value.capitalize()} loaded with 4-bit quantization")
                    
                except Exception as quant_error:
                    print(f"⚠️ 4-bit loading failed for {model_type.value}: {quant_error}")
                    
                    try:
                        # Strategy 2: No quantization, let Unsloth handle optimization
                        print(f"🔄 Trying without quantization for {model_type.value}...")
                        model, processor = FastModel.from_pretrained(
                            model_name=model_name,
                            dtype=None,
                            max_seq_length=2048,
                            load_in_4bit=False,
                            full_finetuning=False,
                        )
                        print(f"✅ {model_type.value.capitalize()} loaded without quantization")
                        
                    except Exception as no_quant_error:
                        print(f"⚠️ No quantization failed for {model_type.value}: {no_quant_error}")
                        
                        # Strategy 3: Basic loading with minimal options
                        print(f"🔄 Trying basic loading for {model_type.value}...")
                        model, processor = FastModel.from_pretrained(
                            model_name=model_name,
                            max_seq_length=1024,  # Reduced context
                            full_finetuning=False,
                        )
                        print(f"✅ {model_type.value.capitalize()} loaded with basic settings")
                
                # Set to evaluation mode
                model.eval()
                
                # Store model and processor
                self.models[model_type]['model'] = model
                self.models[model_type]['processor'] = processor
                self.models[model_type]['loaded'] = True
                
                print(f"🎉 {model_type.value.capitalize()} model loaded successfully")
                return True
                
            except Exception as e:
                error_msg = f"Failed to load {model_type.value} model: {str(e)}"
                print(f"❌ {error_msg}")
                if self.debug_mode:
                    traceback.print_exc()
                
                # Truncate error message for UI display
                truncated_error = f"{model_type.value.capitalize()} loading failed: {str(e)[:25]}..." if len(str(e)) > 25 else f"{model_type.value.capitalize()} loading failed: {str(e)}"
                self._update_status(truncated_error, COLORS['accent_danger'])
                return False
    
    def load_models(self, model_types=None):
        """Load specified models or all models"""
        if model_types is None:
            model_types = [ModelType.AUDIO, ModelType.REPORT]
        elif isinstance(model_types, ModelType):
            model_types = [model_types]
        
        print(f"🔄 Loading {len(model_types)} model(s)...")
        
        results = {}
        for model_type in model_types:
            results[model_type] = self._load_single_model(model_type)
        
        # Update UI status based on results
        loaded_count = sum(results.values())
        total_count = len(model_types)
        
        if loaded_count == total_count:
            print(f"🎉 All {total_count} models loaded successfully")
            self._update_ready_status()
            return True
        elif loaded_count > 0:
            print(f"⚠️ {loaded_count}/{total_count} models loaded")
            self._update_status(f"{loaded_count}/{total_count} models ready", COLORS['accent_warning'])
            return True
        else:
            print(f"❌ No models loaded successfully")
            self._update_status("Model loading failed", COLORS['accent_danger'])
            return False
    
    def _update_status(self, message, color):
        """Update UI status if callback available - THREAD SAFE"""
        if 'schedule_ui_update' in self.ui_callbacks:
            def update_ui():
                if 'update_status' in self.ui_callbacks:
                    try:
                        self.ui_callbacks['update_status'](message, color, "static")
                    except Exception as e:
                        print(f"⚠️ Status update error: {e}")
            
            self.ui_callbacks['schedule_ui_update'](update_ui)
        elif self.debug_mode:
            print(f"📊 Status: {message}")
    
    def _update_ready_status(self):
        """Update to ready status after successful model loading"""
        if 'update_ready_status' in self.ui_callbacks:
            try:
                self.ui_callbacks['update_ready_status']()
            except Exception as e:
                print(f"⚠️ Ready status update error: {e}")
        elif 'on_models_ready' in self.ui_callbacks:
            try:
                self.ui_callbacks['on_models_ready']()
            except Exception as e:
                print(f"⚠️ Models ready callback error: {e}")
        elif self.debug_mode:
            print("📊 Status: Ready")
    
    def _generate_text(self, model_type: ModelType, messages, max_new_tokens=512):
        """Generate text using specified model"""
        if not self.models[model_type]['loaded'] or not self.models[model_type]['model']:
            raise Exception(f"{model_type.value.capitalize()} model not loaded")
        
        model = self.models[model_type]['model']
        processor = self.models[model_type]['processor']
        
        try:
            # Apply chat template and generate
            inputs = processor.apply_chat_template(
                messages,
                add_generation_prompt=True,
                tokenize=True,
                return_dict=True,
                return_tensors="pt",
            )
            
            # Move to appropriate device
            if torch.cuda.is_available():
                inputs = inputs.to("cuda")
            
            # Generate response
            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=max_new_tokens,
                    do_sample=True,
                    temperature=0.3,
                    top_p=0.9,
                    pad_token_id=processor.eos_token_id,
                )
            
            # Decode only the new tokens (skip input)
            input_length = inputs['input_ids'].shape[1]
            generated_tokens = outputs[0][input_length:]
            response = processor.decode(generated_tokens, skip_special_tokens=True)
            
            return response.strip()
            
        except Exception as e:
            print(f"❌ {model_type.value.capitalize()} generation error: {e}")
            if self.debug_mode:
                traceback.print_exc()
            raise
    
    def _transcribe_audio_core(self, wav_file_path):
        """Core audio transcription logic - used by both production and test methods"""
        try:
            file_name = os.path.basename(wav_file_path) if os.path.exists(wav_file_path) else 'audio input'
            print(f"🎙️ Transcribing with audio model: {file_name}")
            
            # Unified logic for all transcription (production and test)
            messages = [{
                "role": "user",
                "content": [
                    {"type": "audio", "audio": wav_file_path},
                    {"type": "text", "text": "Transcribe this medical consultation audio file. Return only the transcribed text without any additional commentary."}
                ]
            }]
            
            # Generate transcription using audio model
            transcription = self._generate_text(ModelType.AUDIO, messages, max_new_tokens=256)
            
            print(f"📝 Audio transcription: {transcription[:100]}..." if len(transcription) > 100 else f"📝 Audio transcription: {transcription}")
            return transcription
            
        except Exception as e:
            error_msg = f"Audio transcription error: {str(e)}"
            print(f"❌ {error_msg}")
            if self.debug_mode:
                traceback.print_exc()
            # Truncate for UI status display
            truncated_error = f"Transcription failed: {str(e)[:20]}..." if len(str(e)) > 20 else f"Transcription failed: {str(e)}"
            return f"[Transcription Error: {truncated_error}]"

    async def transcribe_audio_chunk(self, wav_file_path):
        """Production method: Transcribe audio chunk using dedicated audio model"""
        # Ensure audio model is loaded
        if not self.models[ModelType.AUDIO]['loaded']:
            print("🔄 Loading audio model for transcription...")
            success = self.load_models([ModelType.AUDIO])
            if not success:
                raise Exception("Failed to load audio model")
        
        def _transcribe():
            return self._transcribe_audio_core(wav_file_path)
        
        # Run transcription in thread pool
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, _transcribe)
    
    def _generate_report_core(self, transcription, report_type="General", language="English", attachment=None):
        """Core report generation logic - used by both production and test methods"""
        try:
            print(f"📄 Generating {report_type} report in {language} using report model")
            
            # Build comprehensive medical report prompt optimized for report model
            system_prompt = "You are a professional medical assistant specialized in generating accurate, well-structured medical reports based on consultation transcripts."
            
            # Build user prompt
            user_content = f"""Generate a {report_type.lower()} medical report in {language} based on this consultation transcript:

{transcription}"""
            
            # Add attachment context if provided
            if attachment and attachment.strip():
                user_content += f"\n\nAdditional context from patient records:\n{attachment}"
            
            # Add prescription instructions
            user_content += """

When prescriptions are mentioned, include them in XML format:
<prescription>
    <title>Medication/Procedure Name</title>
    <patient>Patient Information</patient>
    <content>Prescription Details</content>
    <context>Medical Context</context>
</prescription>"""
            
            user_content += "\n\nGenerate a professional medical report now:"
            
            messages = [
                {
                    "role": "system",
                    "content": [{"type": "text", "text": system_prompt}]
                },
                {
                    "role": "user", 
                    "content": [{"type": "text", "text": user_content}]
                }
            ]
            
            if self.debug_mode:
                print(f"📝 Generating report with {len(transcription)} chars transcription")
            
            # Generate report using report model
            max_tokens = 1024 if report_type.lower() != "brief" else 512
            report = self._generate_text(ModelType.REPORT, messages, max_new_tokens=max_tokens)
            
            print(f"📄 Generated report: {len(report)} characters")
            return report
            
        except Exception as e:
            error_msg = f"Report generation error: {str(e)}"
            print(f"❌ {error_msg}")
            if self.debug_mode:
                traceback.print_exc()
            # Truncate for UI display
            truncated_error = f"Generation failed: {str(e)[:25]}..." if len(str(e)) > 25 else f"Generation failed: {str(e)}"
            return f"# Report Generation Error\n\n{truncated_error}\n\nPlease try again or contact support."

    async def generate_medical_report(self, transcription, report_type="General", language="English", attachment=None):
        """Production method: Generate medical report using dedicated report model"""
        # Ensure report model is loaded
        if not self.models[ModelType.REPORT]['loaded']:
            print("🔄 Loading report model for generation...")
            success = self.load_models([ModelType.REPORT])
            if not success:
                raise Exception("Failed to load report model")
        
        def _generate_report():
            return self._generate_report_core(transcription, report_type, language, attachment)
        
        # Run generation in thread pool
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, _generate_report)
    
    def test_real_audio_transcription(self):
        """Test transcription with real audio using dedicated audio model"""
        print("\n🧪 TESTING AUDIO MODEL TRANSCRIPTION")
        print("-" * 40)
        
        if not self.models[ModelType.AUDIO]['loaded']:
            print("❌ Audio model not loaded")
            return False
        
        try:
            # Import required libraries for audio processing
            try:
                from datasets import load_dataset, Audio
                import soundfile as sf
                import numpy as np
            except ImportError as e:
                print(f"❌ Missing required libraries: {e}")
                print("Install with: pip install datasets soundfile")
                return False
            
            print("📥 Loading audio sample from wouk1805/medreport_audio_204")
            
            # Load only sample #9 to save bandwidth and time
            try:
                dataset = load_dataset("wouk1805/medreport_audio_204", split="train[:10]")
                print(f"✅ Dataset loaded: {len(dataset)} samples")
            except Exception as e:
                print(f"❌ Failed to load dataset: {e}")
                return False
            
            # Get sample #9
            if len(dataset) <= 9:
                print(f"❌ Dataset only has {len(dataset)} samples, can't get sample #9")
                return False
            
            test_sample = dataset[9]
            print(f"✅ Retrieved sample #9")
            
            # Cast audio to 16kHz if needed
            dataset = dataset.cast_column("audio", Audio(sampling_rate=16000))
            audio_sample = dataset[9]['audio']
            
            # Save audio locally as file (same as production workflow)
            audio_path = "test_audio_sample_9.wav"
            audio_array = audio_sample['array']
            sampling_rate = audio_sample['sampling_rate']
            
            # Save as WAV file
            sf.write(audio_path, audio_array, sampling_rate)
            print(f"✅ Audio saved: {audio_path} ({len(audio_array)} samples, {sampling_rate}Hz)")
            
            # Get reference transcription if available
            reference_text = test_sample.get('text', 'No reference text available')
            print(f"📝 Reference: {reference_text}")
            
            # Use the same core function as production with file path
            print("🎙️ Running audio model transcription (using core function with file)...")
            result = self._transcribe_audio_core(audio_path)
            
            print(f"✅ Audio model result:\n{result}")
            print(f"📋 Reference text:\n{reference_text}")
            
            # Cleanup
            try:
                os.remove(audio_path)
                print(f"🧹 Cleaned up temporary audio file")
            except:
                pass
            
            return True
            
        except Exception as e:
            print(f"❌ Audio model test failed: {e}")
            if self.debug_mode:
                traceback.print_exc()
            return False
    
    def test_report_generation(self, test_transcription="Patient reports chest pain and shortness of breath during exercise. Vital signs are stable."):
        """Test report generation using dedicated report model"""
        print("\n🧪 TESTING REPORT MODEL GENERATION")
        print("-" * 40)
        
        if not self.models[ModelType.REPORT]['loaded']:
            print("❌ Report model not loaded")
            return False
        
        try:
            print(f"📄 Generating test report with report model (using core function)")
            
            # Use the same core function as production
            result = self._generate_report_core(
                transcription=test_transcription, 
                report_type="Brief",  # Use brief for tests
                language="English"
            )
            
            print(f"✅ Report model result:\n{result}")
            return True
            
        except Exception as e:
            print(f"❌ Report model test failed: {e}")
            if self.debug_mode:
                traceback.print_exc()
            return False
    
    def cleanup(self):
        """Clean up all models and resources"""
        print("🧹 Cleaning up dual models...")
        
        try:
            # Clear all models from memory
            for model_type in ModelType:
                if self.models[model_type]['model'] is not None:
                    del self.models[model_type]['model']
                    self.models[model_type]['model'] = None
                
                if self.models[model_type]['processor'] is not None:
                    del self.models[model_type]['processor']
                    self.models[model_type]['processor'] = None
                
                self.models[model_type]['loaded'] = False
            
            # Force garbage collection
            gc.collect()
            
            # Clear CUDA cache if available
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                print("🗑️ CUDA cache cleared")
            
            # Shutdown executor
            self.executor.shutdown(wait=True)
            
            print("✅ Dual model cleanup completed")
            
        except Exception as e:
            print(f"⚠️ Cleanup error: {e}")
    
    def get_model_info(self):
        """Get information about loaded models"""
        info = {
            'audio_model': {
                'name': self.model_configs[ModelType.AUDIO]['name'],
                'loaded': self.models[ModelType.AUDIO]['loaded']
            },
            'report_model': {
                'name': self.model_configs[ModelType.REPORT]['name'], 
                'loaded': self.models[ModelType.REPORT]['loaded']
            },
            'using_unsloth': True
        }
        
        if torch.cuda.is_available():
            info['cuda_memory_allocated'] = torch.cuda.memory_allocated() / 1e9
            info['cuda_memory_cached'] = torch.cuda.memory_reserved() / 1e9
        
        return info


# ============================================================================
# STANDALONE TESTING AND DEBUGGING
# ============================================================================

def main():
    """Main function for standalone testing"""
    print("🚀 MedReport Dual Model Manager - Debug Mode")
    print("=" * 60)
    
    # Create model manager in debug mode
    manager = LocalModelManager(debug_mode=True)
    
    try:
        print("\n🔧 TESTING DUAL MODEL LOADING")
        print("-" * 40)
        
        # Load both models
        success = manager.load_models()
        
        if success:
            print("\n📊 MODEL INFO:")
            info = manager.get_model_info()
            for key, value in info.items():
                if isinstance(value, dict):
                    print(f"  {key}:")
                    for k, v in value.items():
                        print(f"    {k}: {v}")
                else:
                    print(f"  {key}: {value}")
            
            # Test audio transcription with audio model
            manager.test_real_audio_transcription()
            
            # Test report generation with report model
            # manager.test_report_generation()
        
        else:
            print("\n❌ Model loading failed")
    
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
    
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        traceback.print_exc()
    
    finally:
        # Cleanup
        manager.cleanup()
        print("\n👋 Debug session completed")


if __name__ == "__main__":
    main()