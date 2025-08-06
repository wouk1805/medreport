# Set your OpenAI API key here
API_KEY = "..."

# Configuration
OUTPUT_FILENAME = "medreport_text"
OPENAI_MODEL = "gpt-4o"
LANGUAGE = "English"

# Prompt Configuration
MEDICAL_REPORT_PROMPT = """Generate a realistic, detailed medical report in SOAP format for a random medical consultation. 

Requirements:
- Choose any medical specialty and condition randomly
- Use proper medical terminology
- Include realistic vital signs, lab values, and examination findings
- Make it professionally written and well-structured
- Include assessment and plan sections
- If medications or tests are prescribed, mention them in the plan section AND add prescription XML tags AT THE END
- Make each report unique with different patients, ages, symptoms, and conditions
- Use these formatting tags: **bold**, *italic*, ***bold italic***, # Header
- Write in {language}

For prescriptions, add XML tags at the very end of the report (not in code blocks):

Example if prescribing medication:
<prescription>
<title>Medication</title>
<patient>Mr. John DOE, 45 years old</patient>
<content>- Omeprazole 20mg daily
- Amoxicillin 500mg twice daily</content>
<context>Gastritis treatment</context>
</prescription>

Example if prescribing tests:
<prescription>
<title>Laboratory</title>
<patient>Mrs. Jane SMITH, 32 years old</patient>
<content>Complete blood count
Liver function tests</content>
<context>Follow-up for anemia</context>
</prescription>

Generate a complete, realistic medical report that a physician would actually write."""

TRANSCRIPTION_PROMPT = """Convert this professional medical report into a realistic audio transcription of a natural conversation between a doctor and patient during a consultation. 

Make it sound like real speech captured by imperfect audio recording with these characteristics:
- Include both doctor and patient speaking naturally (no role labels, no timestamps)
- Add speech disfluencies (um..., uh..., you know...)
- Include false starts, repetitions, and corrections
- Make some sentences incomplete or run-on
- Add conversational elements ("so...", "well...", "okay...")
- Include some unclear references ("this thing...", "that issue...")
- Add realistic speech-to-text errors: mishearings, repeated words, missing words
- Word substitutions that sound similar
- Make it sound spontaneous and natural, not scripted
- The audio is in 8-second chunks, so add line breaks roughly every 8 seconds of speech
- No role indicators (don't write "Doctor:" or "Patient:")
- No timestamps
- Make it feel like a real conversation with natural back-and-forth dialogue
- Include realistic audio transcription imperfections

Original medical report:
{medical_report}

Generate a realistic, imperfect audio transcription that captures what this consultation would sound like in natural conversation with typical speech-to-text errors."""

import openai
import json
import time
from datetime import datetime
import random
from typing import List, Dict, Tuple
import os
from datasets import Dataset
import pandas as pd

def get_user_configuration():
    """Get user configuration for dataset generation."""
    
    print("🏥 Medical Dataset Generator Configuration")
    print("=" * 50)
    
    # Get number of examples
    while True:
        try:
            num_samples = int(input("How many examples do you want to generate? (default: 10): ") or "10")
            if num_samples > 0:
                break
            else:
                print("Please enter a positive number.")
        except ValueError:
            print("Please enter a valid number.")
    
    # Get starting ID offset
    while True:
        try:
            start_offset = int(input(f"Starting ID? (default: 1, examples will be ID 1 to {num_samples}): ") or "1")
            if start_offset > 0:
                break
            else:
                print("Please enter a positive number.")
        except ValueError:
            print("Please enter a valid number.")
    
    print(f"\n✅ Configuration:")
    print(f"   📊 Examples to generate: {num_samples}")
    print(f"   🏁 Starting ID: {start_offset}")
    print(f"   🏁 Ending ID: {start_offset + num_samples - 1}")
    print(f"   📁 Output file: {OUTPUT_FILENAME}.json/.csv/.jsonl")
    print(f"   🤖 Model: {OPENAI_MODEL}")
    print(f"   🌍 Language: {LANGUAGE}")
    
    confirm = input(f"\nProceed with generation? (y/n): ").lower().strip()
    if confirm not in ['y', 'yes']:
        print("Generation cancelled.")
        return None, None
    
    return num_samples, start_offset

def format_timestamp():
    """Get formatted timestamp for logging."""
    return datetime.now().strftime("%H:%M:%S")

class MedicalDatasetGenerator:
    def __init__(self, api_key: str):
        """Initialize the dataset generator with OpenAI API key."""
        self.client = openai.OpenAI(api_key=api_key)

    def generate_medical_report(self, language: str = "English", sample_num: int = 0) -> str:
        """Generate a high-quality SOAP medical report."""
        
        try:
            start_time = time.time()
            timestamp = format_timestamp()
            print(f"🔄 [{timestamp}] API Call 1 (Sample {sample_num}): Generating medical report...")
            print(f"   Model: {OPENAI_MODEL}")
            print(f"   Language: {language}")
            
            response = self.client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are an experienced physician writing medical reports. Generate realistic, professional SOAP notes."},
                    {"role": "user", "content": MEDICAL_REPORT_PROMPT.format(language=language)}
                ],
                temperature=0.8,
                max_tokens=1500
            )
            
            end_time = time.time()
            duration = end_time - start_time
            result = response.choices[0].message.content.strip()
            timestamp_end = format_timestamp()
            
            print(f"✅ [{timestamp_end}] API Call 1 (Sample {sample_num}) completed - Generated {len(result)} characters in {duration:.2f}s")
            print(f"📄 OpenAI Response 1 (Sample {sample_num}):")
            print("-" * 50)
            
            # Truncate if too long
            if len(result) > 800:
                print(result[:800] + "...")
            else:
                print(result)
                
            print("-" * 50)
            return result
            
        except Exception as e:
            timestamp_error = format_timestamp()
            print(f"❌ [{timestamp_error}] API Call 1 (Sample {sample_num}) failed: {e}")
            return None

    def create_realistic_transcription(self, medical_report: str, sample_num: int = 0) -> str:
        """Convert a medical report into a realistic, low-quality audio transcription with errors."""

        try:
            start_time = time.time()
            timestamp = format_timestamp()
            print(f"🔄 [{timestamp}] API Call 2 (Sample {sample_num}): Creating realistic transcription with errors...")
            print(f"   Model: {OPENAI_MODEL}")
            print(f"   Input length: {len(medical_report)} characters")
            
            response = self.client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You convert formal medical reports into realistic, imperfect audio transcriptions of natural doctor-patient conversations with speech-to-text errors."},
                    {"role": "user", "content": TRANSCRIPTION_PROMPT.format(medical_report=medical_report)}
                ],
                temperature=0.9,
                max_tokens=2000
            )
            
            end_time = time.time()
            duration = end_time - start_time
            result = response.choices[0].message.content.strip()
            timestamp_end = format_timestamp()
            
            print(f"✅ [{timestamp_end}] API Call 2 (Sample {sample_num}) completed - Generated {len(result)} characters in {duration:.2f}s")
            print(f"📄 OpenAI Response 2 (Sample {sample_num}):")
            print("-" * 50)
            
            # Truncate if too long
            if len(result) > 800:
                print(result[:800] + "...")
            else:
                print(result)
                
            print("-" * 50)
            return result
            
        except Exception as e:
            timestamp_error = format_timestamp()
            print(f"❌ [{timestamp_error}] API Call 2 (Sample {sample_num}) failed: {e}")
            return None

    def generate_training_pair(self, language: str = "English", sample_num: int = 0) -> Tuple[str, str]:
        """Generate a single training pair (transcription, report)."""
        
        timestamp = format_timestamp()
        print(f"\n📋 [{timestamp}] Generating training pair {sample_num} in {language}...")
        print("=" * 60)
        
        # Generate high-quality medical report
        report = self.generate_medical_report(language, sample_num)
        if not report:
            print(f"❌ Failed to generate medical report for sample {sample_num}")
            return None, None
            
        # Create realistic transcription with errors in one step
        transcription = self.create_realistic_transcription(report, sample_num)
        if not transcription:
            print(f"❌ Failed to generate transcription for sample {sample_num}")
            return None, None
        
        timestamp_end = format_timestamp()
        print(f"✅ [{timestamp_end}] Training pair {sample_num} generated successfully!")
        print("=" * 60)
        
        return transcription, report

    def save_dataset_locally(self, dataset_samples: List[Dict], output_formats: List[str] = ["json"], sample_num: int = 0):
        """Save dataset in multiple local formats."""
        
        print(f"💾 Saving {len(dataset_samples)} samples locally (up to sample {sample_num})...")
        
        try:
            if "json" in output_formats:
                with open(f"{OUTPUT_FILENAME}.json", 'w', encoding='utf-8') as f:
                    json.dump(dataset_samples, f, indent=2, ensure_ascii=False)
                print(f"✓ Saved as JSON: {OUTPUT_FILENAME}.json (Sample {sample_num})")
            
            if "csv" in output_formats:
                df = pd.DataFrame(dataset_samples)
                df.to_csv(f"{OUTPUT_FILENAME}.csv", index=False, encoding='utf-8')
                print(f"✓ Saved as CSV: {OUTPUT_FILENAME}.csv (Sample {sample_num})")
            
            if "jsonl" in output_formats:
                with open(f"{OUTPUT_FILENAME}.jsonl", 'w', encoding='utf-8') as f:
                    for sample in dataset_samples:
                        f.write(json.dumps(sample, ensure_ascii=False) + '\n')
                print(f"✓ Saved as JSONL: {OUTPUT_FILENAME}.jsonl (Sample {sample_num})")
                
        except Exception as e:
            print(f"❌ Error saving files (Sample {sample_num}): {e}")

    def generate_dataset(self, num_samples: int, start_id: int = 1, language: str = "English", 
                        save_formats: List[str] = ["json", "csv"], 
                        batch_size: int = 10, 
                        save_incrementally: bool = True) -> Dataset:
        """Generate a complete dataset with the specified number of samples."""
        
        script_start_time = time.time()
        timestamp = format_timestamp()
        
        print(f"\n🚀 [{timestamp}] Starting dataset generation...")
        print(f"Generating {num_samples} medical transcription-report pairs...")
        print(f"Starting from ID: {start_id}")
        print(f"Save mode: {'Incremental (after each sample)' if save_incrementally else 'Batch (at the end)'}")
        
        dataset_samples = []
        successful_generations = 0
        
        for i in range(0, num_samples, batch_size):
            batch_end = min(i + batch_size, num_samples)
            batch_timestamp = format_timestamp()
            print(f"\n[{batch_timestamp}] Generating batch {i//batch_size + 1}/{(num_samples-1)//batch_size + 1} (samples {start_id + i}-{start_id + batch_end - 1})")
            
            for j in range(i, batch_end):
                actual_sample_id = start_id + j
                try:
                    transcription, report = self.generate_training_pair(language, actual_sample_id)
                    
                    if transcription and report:
                        sample = {
                            "input": transcription,
                            "output": report,
                            "language": language,
                            "sample_id": actual_sample_id
                        }
                        dataset_samples.append(sample)
                        successful_generations += 1
                        success_timestamp = format_timestamp()
                        print(f"✓ [{success_timestamp}] Generated sample {actual_sample_id} ({j + 1}/{num_samples})")
                        
                        # Save incrementally if enabled
                        if save_incrementally:
                            self.save_dataset_locally(dataset_samples, save_formats, actual_sample_id)
                            save_timestamp = format_timestamp()
                            print(f"💾 [{save_timestamp}] Saved {len(dataset_samples)} samples so far (Sample {actual_sample_id})")
                        
                    else:
                        error_timestamp = format_timestamp()
                        print(f"✗ [{error_timestamp}] Failed to generate sample {actual_sample_id}")
                        
                except Exception as e:
                    error_timestamp = format_timestamp()
                    print(f"✗ [{error_timestamp}] Error generating sample {actual_sample_id}: {e}")
                
                # Add delay to respect API rate limits
                time.sleep(1)
            
            # Longer delay between batches
            if batch_end < num_samples:
                delay_timestamp = format_timestamp()
                print(f"[{delay_timestamp}] Waiting 10 seconds before next batch...")
                time.sleep(10)
        
        script_end_time = time.time()
        total_duration = script_end_time - script_start_time
        final_timestamp = format_timestamp()
        
        print(f"\n[{final_timestamp}] Successfully generated {successful_generations}/{num_samples} samples")
        print(f"⏱️  Total generation time: {total_duration:.2f} seconds ({total_duration/60:.2f} minutes)")
        if successful_generations > 0:
            avg_time_per_sample = total_duration / successful_generations
            print(f"⏱️  Average time per sample: {avg_time_per_sample:.2f} seconds")
        
        # Final save (in case incremental was disabled or as backup)
        if dataset_samples:  # Only save if we have data
            if not save_incrementally:
                print(f"\nFinal save: Saving dataset locally...")
                self.save_dataset_locally(dataset_samples, save_formats, successful_generations)
            else:
                print(f"\n💾 Final backup save completed (Total: {successful_generations} samples)")
        else:
            print("No data to save!")
            return None
        
        # Create HuggingFace Dataset
        df = pd.DataFrame(dataset_samples)
        dataset = Dataset.from_pandas(df)
        
        return dataset

    def test_file_creation(self):
        """Test function to verify file creation works."""
        test_data = [
            {
                "input": "So tell me what's been bothering you... um... Well doctor I've been having chest pain...",
                "output": "# MEDICAL REPORT\n**Subjective:** 45-year-old patient with chest pain...",
                "language": "English",
                "sample_id": 1
            }
        ]
        
        print("Testing file creation...")
        self.save_dataset_locally(test_data, ["json", "csv", "jsonl"])
        
        # Check if files were created
        import os
        files_to_check = [f"{OUTPUT_FILENAME}.json", f"{OUTPUT_FILENAME}.csv", f"{OUTPUT_FILENAME}.jsonl"]
        for file in files_to_check:
            if os.path.exists(file):
                print(f"✓ {file} created successfully")
            else:
                print(f"✗ {file} was NOT created")

# Example usage
def main():
    # Initialize generator with API key from top of file
    generator = MedicalDatasetGenerator(API_KEY)
    
    # Get user configuration
    config = get_user_configuration()
    if config is None:
        return
    
    num_samples, start_id = config
    
    # Test file creation first
    print("\n=== Testing File Creation ===")
    generator.test_file_creation()
    print("\n" + "="*50 + "\n")
    
    # Generate dataset directly without asking
    print("=== Starting Full Dataset Generation ===")
    
    # Generate dataset with local saving options
    language = LANGUAGE
    
    dataset = generator.generate_dataset(
        num_samples=num_samples,
        start_id=start_id,
        language=language,
        save_formats=["json", "csv", "jsonl"],  # Choose formats: json, csv, jsonl
        save_incrementally=True  # Set to False to save only at the end
    )
    
    # Print sample
    if dataset and len(dataset) > 0:
        print("\nSample from dataset:")
        print("="*50)
        print("INPUT (Transcription):")
        print(dataset[0]["input"][:500] + "..." if len(dataset[0]["input"]) > 500 else dataset[0]["input"])
        print("\nOUTPUT (Report):")
        print(dataset[0]["output"][:500] + "..." if len(dataset[0]["output"]) > 500 else dataset[0]["output"])
        print(f"\nSample ID: {dataset[0]['sample_id']}")
        print("="*50)

if __name__ == "__main__":
    main()