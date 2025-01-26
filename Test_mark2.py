from flask import Flask, render_template, request, redirect, flash, jsonify
import pandas as pd
import pymysql

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Load data from CSV
file_path = "C:\\Users\\shank\\Desktop\\InfyStaa_Database\\Flask - Data Collection Form\\Mark_entry.csv"
data = pd.read_csv(file_path)

# Extract unique Standards and Sections
standards = data['Std'].unique()
sections_mapping = {
    std: data[data['Std'] == std]['Section'].unique().tolist()
    for std in standards
}
exam_types = ["I MID", "Quarterly", "II MID", "Half Yearly"]

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Kumar@007'
app.config['MYSQL_DB'] = 'student_marks'

def get_db_connection():
    return pymysql.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        database=app.config['MYSQL_DB'],
        cursorclass=pymysql.cursors.DictCursor
    )

@app.route('/')
def index():
    return render_template('index_2.html', standards=standards, sections_mapping=sections_mapping, exam_types=exam_types)

@app.route('/get_students', methods=['POST'])
def get_students():
    standard = request.json.get('standard')
    section = request.json.get('section')
    
    filtered_data = data[(data['Std'] == standard) & (data['Section'] == section)]
    students = filtered_data[['DEPT_ID', 'Student_Name', 'Subjects']].to_dict(orient='records')
    
    return jsonify(students)

@app.route('/submit', methods=['POST'])
def submit():
    marks_data = request.json.get('marks_data')
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            sql = """
                INSERT INTO scores 
                (dept_id, student_name, standard, section, subject, marks, exam_type) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            for record in marks_data:
                cursor.execute(sql, (
                    record['dept_id'],
                    record['student_name'],
                    record['standard'],
                    record['section'],
                    record['subject'],
                    record['marks'],
                    record['exam_type']
                ))
        connection.commit()
        connection.close()
        return jsonify({"message": "Data successfully submitted"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
