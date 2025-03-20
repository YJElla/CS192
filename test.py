import re

def extract_structured_data(text):
    structured_data = []

    # Define regex patterns                
    course_pattern = re.compile(
        r"([A-Za-z]+(?:\s[A-Za-z]+)?\s*\d+(?:\.\d+)?)\s+"          # Course Code (e.g., "Eng 10", "Fil 40")
        r"((?:\b(?:[A-Za-z&-,]{2,}|\b[A-Za-z]\b)\s*)+?)\s+"            # Description (Multiple words, e.g., "College English")
        r"(\d+(?:[.,]\d{1,2})?|[A-F][+-]?)?"  # Grade (Numerical first, e.g., "2.25", "1.75", "A")
        r"(\d+|\(\d+\))?",
        re.MULTILINE                   # Units (Strictly a whole number or in parentheses, e.g., "3", "(3)")
    )


    for line in text.splitlines():
        line = line.strip()  # Remove leading/trailing spaces

        # Remove random unwanted characters (keep alphanumeric, spaces, and essential symbols)
        line = re.sub(r"[^A-Za-z0-9\s.,()-]", " ", line)  # Keeps letters, numbers, spaces, periods, commas, parentheses
        line = re.sub(r'\bll\b', '11', line)  # Fix 'll' → '11'
        line = re.sub(r'\bl\b', '1', line)    # Fix 'l' → '1'
        line = re.sub(r"\s+", " ", line).strip()  # Normalize multiple space
        # Match course details
        course_match = course_pattern.match(line)
        if course_match:
            course_code = course_match.group(1).strip()
            description = course_match.group(2).strip()
            grade = (course_match.group(3).strip()) if course_match.group(3) else "N/A"
            units = course_match.group(4).strip() if course_match.group(4) else "Unknown"

            structured_data.append({
                "Course Code": course_code,
                "Description": description,
                "Grade": grade,
                "Units": units
            })

    return structured_data

# Example input
text = """
=== Page 1 ===

CE 26 Analytical and Computational Methods in Civil | |
Engineering | 2 3

CE 27 Analytical and Computational Methods in Civil |
Engineering Il 2.25 | 3

CE 199 Undergraduate Research Project Inc 5 3

UNIVERSITY OF THE PHILIPPINES DILIMAN, Office of the University Registrar, Kalaw Street, UP Campus, Diliman, Quezon City"""

# Run parser
parsed_courses = extract_structured_data(text)

for course in parsed_courses:
    print(course)
