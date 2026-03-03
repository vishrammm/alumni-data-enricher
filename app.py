import os
import io
import uuid
import pandas as pd
from flask import Flask, request, render_template, send_file, jsonify
from config import *
from processor import process_alumni_row

app = Flask(__name__)

ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'ods', 'csv'}

# Output columns
OUTPUT_COLUMNS = [
    COL_NAME,
    COL_LINKEDIN_STATUS,
    COL_LINKEDIN_URL,
    COL_WEB_SEARCH_URL
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

    try:
        ext = file.filename.rsplit('.', 1)[1].lower()

        # Read the uploaded file directly from memory
        if ext == 'csv':
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)

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
                results.append(enriched)
            except Exception as e:
                print(f"Error processing row {idx}: {e}")
                name = str(row[COL_NAME]).strip() if pd.notna(row[COL_NAME]) else ""
                results.append({
                    COL_NAME: name,
                    COL_LINKEDIN_STATUS: f"Error: {str(e)[:100]}",
                    COL_LINKEDIN_URL: "",
                    COL_WEB_SEARCH_URL: ""
                })

        # Write only the 4 output columns to Excel
        result_df = pd.DataFrame(results)[OUTPUT_COLUMNS]
        output_buffer = io.BytesIO()
        result_df.to_excel(output_buffer, index=False, engine='openpyxl')
        output_buffer.seek(0)

        # Send the file directly in the response — no temp files needed
        return send_file(
            output_buffer,
            as_attachment=True,
            download_name='enriched_alumni.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    except Exception as e:
        return jsonify({'error': f'Processing failed: {str(e)}'}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
