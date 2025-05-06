import os
import re
from PIL import Image, ImageEnhance, ImageFilter
from pdf2image import convert_from_path
import pytesseract
import json
import logging
import numpy as np

# Set up logging
logging.basicConfig(level=logging.INFO)
def fix_grade(grade):
    """Fix grades that were extracted incorrectly."""
    grade = grade.replace(",", ".")  # Convert comma to dot for decimal consistency
    
    if re.fullmatch(r"\d{3}", grade):  # E.g., "175" → "1.75"
        return f"{grade[0]}.{grade[1:]}"
    elif re.fullmatch(r"\d{2}", grade):  # E.g., "15" → "1.5"
        return f"{grade[0]}.{grade[1]}"
    
    return grade  # Return unchanged if it's already valid

def extract_structured_data(text,seen_keys):
    structured_data = []
    
    # to remove duplicates and keep the first occurrence


    # Define regex patterns                
    course_pattern = re.compile(
        r"([A-Za-z]+(?:\s[A-Za-z]+)?\s*\d+(?:\.\d+)?)\s+"          # Course Code (e.g., "Eng 10", "Fil 40")
        r"((?:\b(?:[A-Za-z&-,]{2,}|\b[A-Za-z]\b)\s*)+?)\s+"            # Description (Multiple words, e.g., "College English")
        r"(\d+(?:[.,]\d{1,2})?|Inc|[A-F][+-]?)?\s*[|]?\s*"  # Grade (Numerical first, e.g., "2.25", "1.75", "A")
        r"(\d+|\(\d+\))?"                   # Units (Strictly a whole number or in parentheses, e.g., "3", "(3)")
    )



    for line in text.splitlines():
        line = line.strip()  # Remove leading/trailing spaces
        
        course_match = course_pattern.match(line)
        if course_match:
            course_code = course_match.group(1).strip()
            description = course_match.group(2).strip()
            grade = fix_grade(course_match.group(3).strip()) if course_match.group(3) else "N/A"
            units = course_match.group(4).strip() if course_match.group(4) else "Unknown"

            key = (course_code.upper(), description.lower().strip())
            #print("KEY:", key)  # Debug print
            if key not in seen_keys:
                structured_data.append({
                    "Course Code": course_code,
                    "Description": description,
                    "Grade": grade,
                    "Units": units
                })
                #print("Seen Keys:", seen_keys)  # Debug print
                seen_keys.add(key)
            else:
                print("Duplicate found:", key)
    return structured_data

def extract_text_from_pdf(pdf_path):
    seen_keys = set()
    doc = convert_from_path(pdf_path)
    doc = convert_from_path(pdf_path, dpi=300)  # Default is 200

    raw_text_output = ""  # Holds raw text from OCR
    structured_data_processed = {}  # Holds structured data from pre-processed text
    processed_text_output = ""  # Pre-processed OCR text

    for page_number, page_image in enumerate(doc):
        try:
            # Preprocess the image for better OCR results
            processed_image = page_image.convert('L')
            processed_image = processed_image.filter(ImageFilter.MedianFilter())
            enhancer = ImageEnhance.Contrast(processed_image)
            processed_image = enhancer.enhance(2)

            # Extract text from the processed image
            custom_config = r'--oem 3 --psm 6'  # LSTM-based, assume block of text
            raw_text = pytesseract.image_to_string(processed_image, config=custom_config)
            processed_text = "\n".join(preprocess(raw_text))
            raw_text_output += f"\n\n=== Page {page_number + 1} ===\n{raw_text}"
            processed_text_output += f"\n\n=== Page {page_number + 1} ===\n{processed_text}"

            # Store structured data for both raw and pre-processed text
            structured_data_processed[f"Page_{page_number + 1}"] = extract_structured_data(processed_text,seen_keys)

        except Exception as e:
            logging.error(f"Error processing page {page_number + 1}: {e}")
            structured_data_processed[f"Page_{page_number + 1}"] = {"Error": str(e)}

    # Convert structured data to JSON format for easy reading
    return json.dumps({
        "raw_text": raw_text_output.strip(),
        "processed_text": processed_text_output.strip(),
        "structured_data_processed": structured_data_processed
    }, ensure_ascii=False, indent=4)


def is_probable_course_line(line):
    line = line.strip()

    # Ends with a number (unit) — common pattern for units
    ends_with_unit = re.search(r"(\d+|\(\d+\))?" , line)

    if not ends_with_unit:
        return False  # discard lines without unit at the end

    starts_with_course_like = re.match(
        r"([A-Za-z]+(?:\s[A-Za-z]+)?\s*\d+(?:\.\d+)?)\s+", line
    )

    return bool(starts_with_course_like)

def preprocess(raw_text):
    cleaned_lines = []
    for line in raw_text.splitlines():
        line = re.sub(r'[|/\\@#*~]', '', line)  # strip symbols that sneak in
        line = re.sub(r"[^A-Za-z0-9\s.,()-]", " ", line)  # Keep alphanum and common punct
        line = re.sub(r'\bll\b', '11', line)  # Fix 'll' → '11'
        line = re.sub(r'\bl\b', '1', line)    # Fix 'l' → '1'
        line = re.sub(r"\s+", " ", line).strip()  # Normalize spacing

        if is_probable_course_line(line):
            cleaned_lines.append(line)
    return cleaned_lines

def binarize_image(pil_img):
    np_img = np.array(pil_img)
    threshold = 180
    binary = (np_img > threshold) * 255  # White if above threshold, else black
    return Image.fromarray(binary.astype('uint8'))