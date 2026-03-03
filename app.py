import os
import uuid
import shutil
import pandas as pd
from flask import Flask, request, render_template, send_file, jsonify, url_for
from config import *
from processor import process_alumni_row

app = Flask(__name__)

# Configure upload/output directories
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tmp_uploads')
OUTPUT_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tmp_outputs')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'ods', 'csv'}

# New columns to add to the output
NEW_COLUMNS = [
    COL_LINKEDIN_URL,
    COL_LINKEDIN_STATUS,
    COL_DATA_SOURCE,
    COL_ENRICHED_ROLE,
    COL_ENRICHED_COMPANY,
    COL_ENRICHED_LOCATION
]


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Please upload .xlsx, .xls, .ods, or .csv'}), 400

    # Generate unique ID for this job
    job_id = str(uuid.uuid4())[:8]
    ext = file.filename.rsplit('.', 1)[1].lower()
    input_path = os.path.join(UPLOAD_FOLDER, f'{job_id}_input.{ext}')
    output_path = os.path.join(OUTPUT_FOLDER, f'{job_id}_enriched.xlsx')

    file.save(input_path)

    try:
        # Read the uploaded file
        if ext == 'csv':
            df = pd.read_csv(input_path)
        else:
            df = pd.read_excel(input_path)

        total = len(df)
        if total == 0:
            return jsonify({'error': 'The uploaded file is empty'}), 400

        # Validate required column
        if COL_NAME not in df.columns:
            available = ', '.join(df.columns.tolist())
            return jsonify({
                'error': f'Column "{COL_NAME}" not found. Available columns: {available}'
            }), 400

        # Process each row
        results = []
        for idx, row in df.iterrows():
            try:
                enriched = process_alumni_row(row)
                record = row.to_dict()
                record.update(enriched)
                results.append(record)
            except Exception as e:
                print(f"Error processing row {idx}: {e}")
                record = row.to_dict()
                for col in NEW_COLUMNS:
                    record[col] = ""
                record[COL_LINKEDIN_STATUS] = f"Error: {str(e)[:100]}"
                results.append(record)

        # Save to output Excel
        result_df = pd.DataFrame(results)
        result_df.to_excel(output_path, index=False)

        return jsonify({
            'success': True,
            'total_processed': len(results),
            'download_url': url_for('download_file', job_id=job_id)
        })

    except Exception as e:
        return jsonify({'error': f'Processing failed: {str(e)}'}), 500
    finally:
        # Clean up input file
        if os.path.exists(input_path):
            os.remove(input_path)


@app.route('/download/<job_id>')
def download_file(job_id):
    output_path = os.path.join(OUTPUT_FOLDER, f'{job_id}_enriched.xlsx')
    if not os.path.exists(output_path):
        return jsonify({'error': 'File not found or expired'}), 404

    return send_file(
        output_path,
        as_attachment=True,
        download_name='enriched_alumni.xlsx',
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
