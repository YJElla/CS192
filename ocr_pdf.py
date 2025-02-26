import os
import re
from PIL import Image, ImageEnhance, ImageFilter
from pdf2image import convert_from_path
import pytesseract
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

def extract_structured_data2(text):
    structured_data = []

    # Define regex patterns                
    course_pattern = re.compile(r"([A-Za-z]+\s*\d+)\s*([\w\s,\s*&-]+?)\s*([\d.,]+ | Inc | [A-F][+-]?)\s*(\(?\d+\)?)?")  # Matches course code, description, grade, and units

    for line in text.splitlines():
        line = line.strip()  # Remove leading/trailing spaces

        # Remove random unwanted characters (keep alphanumeric, spaces, and essential symbols)
        line = re.sub(r"[^A-Za-z0-9\s.,()-]", " ", line)  # Keeps letters, numbers, spaces, periods, commas, parentheses
        line = re.sub(r"\s+", " ", line).strip()  # Normalize multiple space
        
        # Match course details
        course_match = course_pattern.match(line)
        if course_match:
            course_code = course_match.group(1).strip()
            description = course_match.group(2).strip()
            grade = course_match.group(3).strip()
            units = course_match.group(4).strip() if course_match.group(4) else "Unknown"

            structured_data.append({
                "Course Code": course_code,
                "Description": description,
                "Grade": grade,
                "Units": units
            })

    return structured_data

def extract_text_from_pdf(pdf_path):
    doc = convert_from_path(pdf_path)

    structured_data_processed = {}  # Holds structured data from pre-processed text
    processed_text_output = ""  # Pre-processed OCR text

    # Define regex patterns for capturing data
    patterns = {
        "name": r"Name:\s*([A-Za-z\s]+)",
        "course_degree": r"COLLEGE OF (.+)",
        "course_data": r"([A-Za-z]+\s*\d+)\s*([\w\s,&-]+?)\s*([\d.]+)\s*(\d+)",  # Course Code, Description, Grade, Units
        "semester": r"(1st Semester|2nd Semester|Midyear|First Semester|Second Semester)\s*,?\s*(\d{4}-\d{4})",  # Matches semester and year
    }

    for page_number, page_image in enumerate(doc):
        try:
            # Preprocess the image for better OCR results
            processed_image = page_image.convert('L')
            processed_image = processed_image.filter(ImageFilter.MedianFilter())
            enhancer = ImageEnhance.Contrast(processed_image)
            processed_image = enhancer.enhance(2)

            # Extract text from the processed image
            processed_text = pytesseract.image_to_string(processed_image)
            processed_text_output += f"\n\n=== Page {page_number + 1} ===\n{processed_text}"

            # Store structured data for both raw and pre-processed text
            structured_data_processed[f"Page_{page_number + 1}"] = extract_structured_data2(processed_text)

        except Exception as e:
            logging.error(f"Error processing page {page_number + 1}: {e}")
            structured_data_processed[f"Page_{page_number + 1}"] = {"Error": str(e)}

    # Convert structured data to JSON format for easy reading
    return json.dumps({
        "processed_text": processed_text_output.strip(),
        "structured_data_processed": structured_data_processed
    }, ensure_ascii=False, indent=4)


def extract_structured_data(text, patterns):
    """Extracts structured data from OCR text using regex patterns."""
    page_data = {}

    # Extract semester and academic year
    semester_match = re.search(patterns["semester"], text)
    if semester_match:
        page_data["Semester"] = semester_match.group(1).strip()
        page_data["Academic Year"] = semester_match.group(2).strip()
    else:
        page_data["Semester"] = "Not found"
        page_data["Academic Year"] = "Not found"

    # Extract course numbers, descriptions, grades, and units
    courses = []
    for match in re.finditer(patterns["course_data"], text):
        course_no = match.group(1).strip()
        description = match.group(2).strip()
        grade = match.group(3).strip()
        units = match.group(4).strip()

        courses.append({
            "Course Code": course_no,
            "Description": description,
            "Grade": grade,
            "Units": units
        })

    page_data["Courses"] = courses  # Add courses list to page data
    return page_data
