from flask import Flask, render_template, request, jsonify
from io import BytesIO
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.units import inch

app = Flask(__name__)

def generate_pdf(data2, data1):
    try:
        # Extracting data from the input JSON
        selected_semester = data2[0]["semesterName"] + " " + str(data2[0]["semesterYear"])

        # Create a PDF document
        pdf_buffer = BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=landscape(A4),
                                leftMargin=1 * inch, rightMargin=1 * inch, topMargin=0.5 * inch, bottomMargin=0.5 * inch)

        # Adding elements to the PDF
        img_path = 'static/images/diulogoside.png'
        img = Image(img_path, width=250, height=64)

        spcc = Spacer(1, 0.1 * inch)
        story = [img, spcc, spcc, spcc, spcc]

        title_style = getSampleStyleSheet()["Title"]
        title = Paragraph("<font size=24 color=#000000><b>Academic Result</b></font>", title_style)
        story.append(title)

        student_info_text = (
            f"<font size=12><b>Student ID:</b> {data1['studentId']}<br></br><br/>"
            f"<b>Student Name:</b> {data1['studentName']}<br></br><br/>"
            f"<b>Program:</b> {data1['programName']}<br></br><br/>"
            f"<b>Semester:</b> {data1['semesterName']}</font>"
        )

        info = Paragraph(student_info_text, getSampleStyleSheet()["Normal"])
        story.extend([spcc, spcc, info, spcc, spcc, spcc])

        title_res = Paragraph(f"<font size=18 color=#000000><b>Result of {selected_semester}</b></font>", title_style)
        story.append(title_res)

        table_data = [["Course Code", "Course Title", "Credit", "GPA"]]

        for course in data2:
            course_code = course['customCourseId']
            course_title = course["courseTitle"]
            total_credit = course["totalCredit"]
            gpa = course.get("pointEquivalent", "")  # Use get to handle missing key gracefully
            table_data.append([str(course_code), course_title, str(total_credit), str(gpa)])

        try:
            table_data.append(["", "", "Total SGPA", str(data2[0].get("cgpa", ""))])  # Use get to handle missing key
        except (IndexError, KeyError):
            raise ValueError("Invalid data format for calculating Total SGPA")

        table = Table(table_data, colWidths=[100, 400, 100, 100])

        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), (0.85, 0.85, 0.85)),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
            ("BACKGROUND", (0, 1), (-1, -1), (0.95, 0.95, 0.95)),
            ("GRID", (0, 0), (-1, -1), 1, (0.7, 0.7, 0.7)),
        ]))

        story.extend([spcc, spcc, table, spcc, spcc])

        footer_text = "<font size=10 color=gray><i>Generated by cyr0x</i></font>"
        footer = Paragraph(footer_text, getSampleStyleSheet()["Normal"])
        story.append(Spacer(1, 0.1 * inch))
        story.append(footer)

        # Build and save the PDF
        doc.build(story)

        # Reset buffer position to the beginning before returning
        pdf_buffer.seek(0)
        return pdf_buffer

    except Exception as e:
        print("Error generating PDF:", str(e))
        raise

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_pdf', methods=['POST'])
def generate_pdf_route():
    try:
        json_data = request.get_json()
        result_data = json_data.get('data', [])
        student_info = json_data.get('stdData', {})
        pdf_buffer = generate_pdf(result_data, student_info)
        return jsonify({'pdf_content': pdf_buffer.read().decode('latin-1')})

    except Exception as e:
        print("Error in generate_pdf_route:", str(e))
        return jsonify({'error': 'Failed to generate PDF'}), 500

# if __name__ == '__main__':
#     app.run(debug=True, host='0.0.0.0', port=6969)
