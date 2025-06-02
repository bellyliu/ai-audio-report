import os
import uuid
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename

# Initialize Flask App
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'temp_audio_uploads' # Define a folder for temporary uploads
app.config['MAX_CONTENT_LENGTH'] = 300 * 1024 * 1024  # Max upload size: 300MB for up to 30 files (approx 10MB each)

# Create upload folder if it doesn't exist
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# In-memory storage for demonstration purposes
# In a real application, use a database (e.g., PostgreSQL, MongoDB) and a proper task queue (Celery with Redis/RabbitMQ)
reports_db = {} # Stores overall report status and associated task IDs
# Example: reports_db['report_id_1'] = {'user_id': 'user123', 'status': 'PENDING', 'task_ids': ['task_id_a'], 'results': [], 'report_url': None, 'file_count': 1}

tasks_db = {}   # Stores individual task status and data
# Example: tasks_db['task_id_a'] = {'report_id': 'report_id_1', 'status': 'PENDING', 'audio_file_path': 'path/to/file.mp3', 'extracted_data': None, 'error_message': None}

# --- Helper Functions (Placeholders for real implementations) ---

def dispatch_celery_task(audio_file_path, user_id, audio_task_id, report_id):
    """
    Placeholder for dispatching a task to a Celery worker.
    In a real app, this would use Celery's send_task or .delay()
    """
    print(f"CELERY_DISPATCH: Task {audio_task_id} for report {report_id} (file: {audio_file_path}, user: {user_id}) sent to Celery.")
    # Simulate Celery worker processing by directly calling a mock processing function
    # This is NOT how it would work with actual Celery, but helps demonstrate the flow for this example.
    mock_celery_worker_process(audio_file_path, user_id, audio_task_id, report_id)
    return True

def mock_celery_worker_process(audio_file_path, user_id, audio_task_id, report_id):
    """
    Simulates the processing done by a Celery worker.
    In a real app, this logic would be in a Celery task function.
    """
    print(f"MOCK_CELERY_WORKER: Processing task {audio_task_id} for file {audio_file_path}")
    try:
        # 1. Simulate Speech-to-Text (STT)
        # transcribed_text = perform_stt(audio_file_path) # Real STT call
        transcribed_text = f"This is a simulated transcription for {os.path.basename(audio_file_path)}."
        print(f"MOCK_CELERY_WORKER: STT successful for {audio_task_id}")

        # 2. Simulate LLM Information Extraction
        # extracted_info = call_llm_service(transcribed_text) # Real LLM call
        extracted_info = {
            "Nama": f"Nama {str(uuid.uuid4())[:4]}",
            "Alamat": f"Alamat {str(uuid.uuid4())[:6]}",
            "Jumlah minuman yang di beli": int(str(uuid.uuid4().int)[:1]) % 10 + 1 # Random number 1-10
        }
        print(f"MOCK_CELERY_WORKER: LLM extraction successful for {audio_task_id}")

        # 3. Call the internal task_complete endpoint (simulated direct call for this example)
        # In a real Celery setup, the worker would make an HTTP request to this endpoint
        # or use another method to update the main application's database.
        task_completion_payload = {
            "task_id": audio_task_id,
            "report_id": report_id,
            "status": "completed",
            "extracted_data": extracted_info,
            "error_message": None
        }
        with app.test_request_context(): # Allows calling app routes internally for simulation
             response = app.test_client().post('/api/v1/internal/task_complete', json=task_completion_payload)
             if response.status_code != 200:
                 print(f"MOCK_CELERY_WORKER_ERROR: Failed to update task_complete for {audio_task_id}. Status: {response.status_code}")


    except Exception as e:
        print(f"MOCK_CELERY_WORKER_ERROR: Error processing task {audio_task_id}: {str(e)}")
        task_completion_payload = {
            "task_id": audio_task_id,
            "report_id": report_id,
            "status": "failed",
            "extracted_data": None,
            "error_message": f"Simulated processing error: {str(e)}"
        }
        with app.test_request_context():
             response = app.test_client().post('/api/v1/internal/task_complete', json=task_completion_payload)
             if response.status_code != 200:
                 print(f"MOCK_CELERY_WORKER_ERROR: Failed to update task_complete (failure) for {audio_task_id}. Status: {response.status_code}")


def generate_csv_report_url(report_id, all_extracted_data):
    """
    Placeholder for generating a CSV report and returning its URL.
    In a real app, this would create a CSV, save it to cloud storage, and return a public/signed URL.
    """
    if not all_extracted_data:
        return None
        
    filename = f"report_{report_id}.csv"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename) # Save in the same temp folder for simplicity
    
    # Basic CSV generation
    try:
        import csv
        headers = ["Nama", "Alamat", "Jumlah minuman yang di beli"]
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            for data_item in all_extracted_data:
                if isinstance(data_item, dict): # Ensure it's a dictionary
                    writer.writerow({k: data_item.get(k, "") for k in headers}) # Handle missing keys
        print(f"CSV_GENERATION: Report {filename} created with {len(all_extracted_data)} entries.")
        # For this example, we'll just return a dummy local path.
        # In a real app, upload to S3/GCS and return the URL.
        return f"/downloads/{filename}" # A conceptual download path
    except Exception as e:
        print(f"CSV_GENERATION_ERROR: Could not generate CSV for report {report_id}: {e}")
        return None

# --- API Endpoints ---

@app.route('/api/v1/audio/upload', methods=['POST'])
def upload_audio_files():
    """
    Receives audio files from the Telegram bot and initiates processing.
    """
    if 'files' not in request.files:
        return jsonify({"status": "error", "message": "No files part in the request."}), 400

    files = request.files.getlist('files')
    user_id = request.form.get('user_id')
    report_id_from_request = request.form.get('report_id')

    if not user_id:
        return jsonify({"status": "error", "message": "User ID is required."}), 400
    
    if not files or all(f.filename == '' for f in files):
        return jsonify({"status": "error", "message": "No selected files."}), 400

    if len(files) > 30:
        return jsonify({"status": "error", "message": "Cannot upload more than 30 files at once."}), 400

    report_id = report_id_from_request if report_id_from_request else str(uuid.uuid4())
    
    current_report_task_ids = []
    reports_db[report_id] = {
        'user_id': user_id,
        'status': 'PENDING', # Initial status
        'task_ids': current_report_task_ids,
        'results': [], # To store extracted data from each successful task
        'report_url': None,
        'file_count': len(files),
        'completed_task_count': 0,
        'failed_task_count': 0
    }

    for audio_file in files:
        if audio_file: # Ensure file is present
            filename = secure_filename(audio_file.filename) # Sanitize filename
            # In a real app, consider more robust unique naming for stored files
            temp_file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{report_id}_{uuid.uuid4()}_{filename}")
            try:
                audio_file.save(temp_file_path)
            except Exception as e:
                print(f"FILE_SAVE_ERROR: Could not save file {filename}: {e}")
                # Optionally, handle this more gracefully, maybe skip this file or fail the report
                continue 

            task_id = str(uuid.uuid4())
            current_report_task_ids.append(task_id)
            tasks_db[task_id] = {
                'report_id': report_id,
                'status': 'QUEUED', # Task is queued for processing
                'audio_file_path': temp_file_path,
                'extracted_data': None,
                'error_message': None
            }
            # Dispatch to Celery (simulated by direct call here)
            dispatch_celery_task(temp_file_path, user_id, task_id, report_id)

    if not current_report_task_ids: # If all file saves failed or no valid files
         del reports_db[report_id] # Clean up
         return jsonify({"status": "error", "message": "No valid files were processed."}), 400


    return jsonify({
        "status": "success",
        "message": "Audio files received and queued for processing.",
        "report_id": report_id,
        "task_ids": current_report_task_ids
    }), 202


@app.route('/api/v1/report/status/<report_id>', methods=['GET'])
def get_report_status(report_id):
    """
    Allows polling for the status of a batch report.
    """
    report = reports_db.get(report_id)
    if not report:
        return jsonify({"status": "error", "message": "Report ID not found."}), 404

    # Update overall status based on individual tasks if not already finalized
    if report['status'] not in ['COMPLETED', 'FAILED', 'PARTIALLY_COMPLETED']:
        all_tasks_done = True
        any_processing = False
        
        for task_id in report['task_ids']:
            task = tasks_db.get(task_id)
            if not task or task['status'] in ['QUEUED', 'PROCESSING']:
                all_tasks_done = False
                if task and task['status'] == 'PROCESSING':
                    any_processing = True
                break 
        
        if all_tasks_done:
            if report['failed_task_count'] == 0 and report['completed_task_count'] == report['file_count']:
                report['status'] = 'COMPLETED'
                # Report URL should have been set by task_complete logic
            elif report['failed_task_count'] > 0 and report['completed_task_count'] + report['failed_task_count'] == report['file_count']:
                if report['completed_task_count'] > 0:
                    report['status'] = 'PARTIALLY_COMPLETED'
                else:
                    report['status'] = 'FAILED'
                # Generate report even for partial completion if some data exists
                if report['results'] and not report['report_url']:
                     report['report_url'] = generate_csv_report_url(report_id, report['results'])

            elif report['failed_task_count'] == report['file_count']:
                 report['status'] = 'FAILED'
            else:
                # This case might indicate an issue or tasks still pending in an unexpected way
                report['status'] = 'PROCESSING' # Or some other intermediate state
        elif any_processing:
            report['status'] = 'PROCESSING'
        else:
            report['status'] = 'PENDING' # Still waiting for tasks to start or finish


    task_details = []
    for task_id in report['task_ids']:
        task = tasks_db.get(task_id, {})
        task_details.append({
            "task_id": task_id,
            "status": task.get('status', 'UNKNOWN'),
            "extracted_data_summary": "Data available" if task.get('extracted_data') else None, # Simplified summary
            "error": task.get('error_message')
        })

    return jsonify({
        "status": "success",
        "report_id": report_id,
        "overall_status": report['status'],
        "details": task_details,
        "report_url": report.get('report_url') # Will be None if not completed or failed to generate
    }), 200


@app.route('/api/v1/internal/task_complete', methods=['POST'])
def task_complete_webhook():
    """
    Internal webhook called by Celery workers upon task completion/failure.
    """
    data = request.json
    task_id = data.get('task_id')
    report_id = data.get('report_id')
    task_status = data.get('status') # "completed" or "failed"
    extracted_data = data.get('extracted_data')
    error_message = data.get('error_message')

    if not all([task_id, report_id, task_status]):
        return jsonify({"status": "error", "message": "Missing required fields (task_id, report_id, status)."}), 400

    task = tasks_db.get(task_id)
    report = reports_db.get(report_id)

    if not task or not report:
        return jsonify({"status": "error", "message": "Invalid task_id or report_id."}), 404

    # Update task status
    task['status'] = task_status
    if task_status == 'completed' and extracted_data:
        task['extracted_data'] = extracted_data
        report['results'].append(extracted_data) # Add to report's aggregated results
        report['completed_task_count'] += 1
    elif task_status == 'failed':
        task['error_message'] = error_message
        report['failed_task_count'] += 1
    
    print(f"TASK_UPDATE: Task {task_id} for report {report_id} marked as {task_status}. Completed: {report['completed_task_count']}, Failed: {report['failed_task_count']}, Total: {report['file_count']}")


    # Check if all tasks for this report are done
    if (report['completed_task_count'] + report['failed_task_count']) == report['file_count']:
        print(f"REPORT_FINALIZE_CHECK: Report {report_id} all tasks accounted for.")
        if report['completed_task_count'] > 0 : # Generate report if at least one task succeeded
            report['report_url'] = generate_csv_report_url(report_id, report['results'])
            if report['failed_task_count'] > 0:
                report['status'] = 'PARTIALLY_COMPLETED'
            else:
                report['status'] = 'COMPLETED'
            print(f"REPORT_FINALIZE: Report {report_id} status set to {report['status']}, URL: {report['report_url']}")
        else: # All tasks failed
            report['status'] = 'FAILED'
            print(f"REPORT_FINALIZE: Report {report_id} status set to FAILED.")
        
        # TODO: In a real app, trigger notification to Telegram bot here
        # e.g., send_telegram_notification(report['user_id'], report_id, report['status'], report['report_url'])
        print(f"NOTIFICATION_STUB: Notify user {report['user_id']} about report {report_id} status: {report['status']}")

    return jsonify({"status": "success", "message": "Task status updated."}), 200

@app.route('/downloads/<filename>', methods=['GET'])
def download_file(filename):
    """
    A conceptual endpoint to serve generated CSV files.
    In a real production app, files would be served from cloud storage or a dedicated file server.
    """
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
    except FileNotFoundError:
        return jsonify({"status": "error", "message": "File not found."}), 404


if __name__ == '__main__':
    # For development, Flask's built-in server is fine.
    # For production, use a WSGI server like Gunicorn or uWSGI.
    app.run(debug=True, port=5001) # Running on a different port to avoid conflict if other apps use 5000