"""
Smart College Application Generator Using AI
Flask Backend with Gemini API Integration
"""

from flask import Flask, render_template, request, jsonify, send_file
import google.generativeai as genai
from pdf_generator import generate_pdf
import os
import io
import re
from dotenv import load_dotenv
load_dotenv()


# Initialize Flask app
app = Flask(__name__)


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  # IMPORTANT: Replace this!

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')
# College name (customize as needed)
COLLEGE_NAME = "{data['college']}"

def generate_application_content(data):
    """
    Function to generate professional application content using Gemini API
    """
    
    prompt = f"""
    You are an expert college application writer.

            Generate a professional and formal college application based on the student's details.

            Use the student's name, enrollment number, department, application category, and issue description to create the application.

            Generate a complete formal college application.

            The application must include:

                 1. Introduction
                 2. Reason for application
                 3. Polite request paragraph
                 4. Closing paragraph
                 5. Professional language
                 6. Appropriate subject
                 Do not make the application shorter than 120 words.

                 Subject Rules:
                    - Subject must be short and professional.
                    - Do not include student name.
                    - Do not include enrollment number.
                    - Maximum 8 words.

                    The application should include:
                    1. Introduction
                    2. Reason  
                    3. Leave/Request paragraph
                    4. Assurance paragraph
                    5. Professional closing                     

            Rules:

            1. Do not copy the user's text word-for-word.
            2. Convert the issue into professional formal language.
            3. Keep the application between 100 and 150 words.
            4. Use simple and professional student-friendly language.
            5. Do not make the application overly formal.
            6. Do not mention submitting medical certificates unless the user specifically states it.
            7. Do not invent extra details.
            8. Keep the subject short (maximum 6 words).
            9. Write naturally as a college student.
            10. Create an appropriate subject automatically.
            11. Use proper grammar and formatting.
            12. Do not include explanations, notes, or headings.
            13. Return only the final application.

            Student Name: {data['student_name']}
            Enrollment Number: {data['enrollment_no']}
            Department: {data['department']}
            Application Category: {data['category']}
            Issue Description: {data['reason']}

            Format:

            To,
            The Principal,
            {data['college']}

            Subject: [Generate Suitable Subject]

            Respected Sir/Madam,

            [Write a formal application paragraph based on the issue.]

            I shall be highly grateful for your kind consideration.

            Thanking You.

            Yours Faithfully,
            {data['student_name']}
            Enrollment No: {data['enrollment_no']}
            Department: {data['department']}

    
    Important: Return ONLY the application text, no extra comments or explanations.
    """
    
    try:
        # Generate content using Gemini
        print("=== GEMINI FUNCTION CALLED ===")
        print(data)
        print("Sending request to Gemini...")

        response = model.generate_content(prompt)

        print("Gemini response received")
        print(response.text)

        application_text = response.text.strip()

        return application_text

    except Exception as e:
        print("=== GEMINI API ERROR ===")
        print(repr(e))
        return generate_fallback_application(data)

def generate_fallback_application(data):
    """
    Fallback function to generate application without AI (if API fails)
    """
    category_subjects = {
        "Leave Application": "Request for Leave of Absence",
        "Fee Issue": "Regarding Fee Payment Issue",
        "Examination Issue": "Request for Examination Related Concern",
        "Faculty Complaint": "Regarding Faculty Conduct Issue",
        "Canteen Complaint": "Complaint Regarding Canteen Services",
        "Library Issue": "Regarding Library Services Issue",
        "ID Card Issue": "Request for ID Card Related Assistance"
    }
    
    subject = category_subjects.get(data['category'], "Application Request")
    
    body = f"""This is to bring to your kind attention that I, {data['student_name']} (Enrollment No: {data['enrollment_no']}), from the Department of {data['department']}, wish to submit the following matter:

{data['reason']}

I kindly request you to look into this matter and take appropriate action at the earliest convenience.

I shall be highly grateful for your kind consideration and prompt response."""
    
    application = f"""To,
The Principal,
{COLLEGE_NAME}

Subject: {subject}

Respected Sir/Madam,

{body}

Thanking You.

Yours faithfully,
{data['student_name']}
Enrollment No: {data['enrollment_no']}
Department: {data['department']}"""
    
    return application

@app.route('/')
def index():
    """Render the main application page"""
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_application():
    """
    API endpoint to generate application using AI
    Receives form data and returns generated application
    """
    try:
        # Get form data
        data = {
                'student_name': request.form.get('student_name', '').strip(),
                'enrollment_no': request.form.get('enrollment_no', '').strip(),
                'department': request.form.get('department', '').strip(),
                'college': request.form.get('college', '').strip(),
                'category': request.form.get('category', '').strip(),
                 'date': request.form.get('date', '').strip(),
                'reason': request.form.get('reason', '').strip()
             }
        
        # Validation - check if all fields are filled
        for key, value in data.items():
            if not value:
                return jsonify({
                    'success': False,
                    'error': f'Please fill in the {key.replace("_", " ")} field'
                }), 400
        
        # Generate application content
        application_text = generate_application_content(data)
        
        return jsonify({
            'success': True,
            'application': application_text
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'An error occurred: {str(e)}'
        }), 500

@app.route('/download-pdf', methods=['POST'])
def download_pdf():
    """
    API endpoint to download application as PDF
    """
    try:
        data = request.get_json()
        application_text = data.get('application', '')
        
        if not application_text:
            return jsonify({'success': False, 'error': 'No application text provided'}), 400
        
        # Generate PDF
        pdf_buffer = generate_pdf(application_text)
        
        # Return PDF as downloadable file
        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name='college_application.pdf',
            mimetype='application/pdf'
        )
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500



if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)