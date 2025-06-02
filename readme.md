# AI-Powered Telegram Audio Report Generation System

## Project Overview
This project is an application designed to process audio recordings uploaded via Telegram, utilize a Large Language Model (LLM) to extract specific information, and generate a downloadable CSV report. The primary goal is to automate the extraction of structured data from unstructured audio inputs, specifically targeting information like names, addresses, and quantities of items purchased.

## Target Output
The system aims to produce a CSV file with the following columns for each processed audio entry:

- Nama (Name)

- Alamat (Address)

- Jumlah minuman yang di beli (Number of drinks purchased)

## System Architecture
The application is composed of several key components that work together to achieve the desired functionality:

### Telegram Bot Interface:

Serves as the primary user interface for file uploads, status updates, and report delivery.

Handles interactions like /start commands and signals for upload completion (e.g., /done).

Supports various audio file formats (e.g., .mp3, .wav, .m4a, .ogg).

Technologies: Python with python-telegram-bot, Node.js with Telegraf.js.

### Backend Application Server:

The central engine that orchestrates the entire process.

Receives files and commands from the Telegram bot via an API.

Manages a job queue for handling concurrent requests (up to 30 files per user).

Interfaces with audio processing, LLM, and report generation modules.

Handles temporary file storage.

Technologies: Python (Flask, Django, FastAPI), Node.js (Express.js), Java (Spring Boot).

### Audio Processing Module (within Backend):

Converts spoken audio into text (Speech-to-Text - STT).

Technologies: Google Cloud Speech-to-Text, AWS Transcribe, Azure Cognitive Speech Services, OpenAI Whisper, Mozilla DeepSpeech.

### LLM Integration Module (within Backend):

Extracts structured information (Nama, Alamat, Jumlah minuman) from the transcribed text using an LLM.

Involves careful prompt engineering to guide the LLM.

Technologies: OpenAI API (GPT-3.5-turbo, GPT-4), Google Gemini API.

### Report Generation Module (within Backend):

Collects extracted data and formats it into a CSV file with the specified headers.

Technologies: Standard CSV libraries (e.g., Python csv module, Node.js fast-csv).

### Temporary File Storage:

Securely stores uploaded audio files and generated CSV reports during processing.

Technologies: AWS S3, Google Cloud Storage, Azure Blob Storage, Local Server Storage.

### Job Queue System (Recommended):

Manages asynchronous processing of audio files, enhancing scalability and resilience.

Decouples file reception from processing and allows for retries.

Technologies: Redis with Celery (Python), RabbitMQ, Apache Kafka.

# Workflow
```mermaid
graph TD
    A["<div style='font-weight:bold; font-size:1.1em;'>👤 User</div>Uploads Audio Files via Telegram"] --> B["<div style='font-weight:bold; font-size:1.1em;'>🤖 Telegram Bot</div>Receives Files & User Info"];
    B --> C["<div style='font-weight:bold; font-size:1.1em;'>🌐 Flask API</div>POST /api/v1/audio/upload<br/>(User ID, Files, Report ID)"];
    C --> D["<div style='font-weight:bold; font-size:1.1em;'>⚙️ Backend Logic (API)</div>Validates Request<br/>Saves Files Temporarily<br/>Creates Main Report Job"];
    D --> E["<div style='font-weight:bold; font-size:1.1em;'>🔄 Backend Logic (API)</div>Dispatches Individual Audio Processing Tasks<br/>(e.g., to Celery Queue)"];

    subgraph Asynchronous Processing (Parallel for each audio file)
        direction LR
        F["<div style='font-weight:bold; font-size:1em;'>👷 Task Worker (e.g., Celery)</div>Picks up a single audio task"] --> G["Speech-to-Text (STT)<br/>Audio ➔ Text"];
        G -- Transcribed Text --> H["Large Language Model (LLM)<br/>Text ➔ Structured Data<br/>(Nama, Alamat, Jumlah Minuman)"];
        H -- Extracted Data / Error --> I["Task Worker Reports Result<br/>(Success or Failure for this file)"];
    end
    E -.-> F;

    I --> J["<div style='font-weight:bold; font-size:1.1em;'>🌐 Flask API</div>POST /api/v1/internal/task_complete<br/>(Task ID, Report ID, Status, Data/Error)"];
    J --> K["<div style='font-weight:bold; font-size:1.1em;'>⚙️ Backend Logic (API)</div>Updates Individual Task Status<br/>Aggregates Results for the Report ID"];

    K -- All Tasks for Report ID Processed --> L["<div style='font-weight:bold; font-size:1.1em;'>⚙️ Backend Logic (API)</div>Checks Overall Report Status"];
    L -- All/Sufficient Tasks Successful --> M["Generates Final CSV Report<br/>Saves CSV to Storage"];
    M --> N["<div style='font-weight:bold; font-size:1.1em;'>⚙️ Backend Logic (API)</div>Updates Report Status: COMPLETED<br/>Notifies Telegram Bot (or Bot Polls Status)"];
    
    L -- Some/All Tasks Failed --> O["Updates Report Status: FAILED/PARTIALLY_COMPLETED<br/>(May still generate partial CSV if applicable)"];
    O --> N;

    N --> P["<div style='font-weight:bold; font-size:1.1em;'>🤖 Telegram Bot</div>Receives Report Status & URL (if successful)"];
    P --> Q["<div style='font-weight:bold; font-size:1.1em;'>👤 User</div>Receives CSV Report/Download Link or Failure Notification via Telegram"];

    style A fill:#e0f2fe,stroke:#0ea5e9,stroke-width:2px
    style Q fill:#e0f2fe,stroke:#0ea5e9,stroke-width:2px
    style B fill:#dcfce7,stroke:#22c55e,stroke-width:2px
    style P fill:#dcfce7,stroke:#22c55e,stroke-width:2px
    style C fill:#ffedd5,stroke:#f97316,stroke-width:2px
    style J fill:#ffedd5,stroke:#f97316,stroke-width:2px
    style D fill:#ede9fe,stroke:#8b5cf6,stroke-width:2px
    style E fill:#ede9fe,stroke:#8b5cf6,stroke-width:2px
    style K fill:#ede9fe,stroke:#8b5cf6,stroke-width:2px
    style L fill:#ede9fe,stroke:#8b5cf6,stroke-width:2px
    style M fill:#ede9fe,stroke:#8b5cf6,stroke-width:2px
    style N fill:#ede9fe,stroke:#8b5cf6,stroke-width:2px
    style O fill:#fee2e2,stroke:#ef4444,stroke-width:2px
    style F fill:#fef3c7,stroke:#eab308,stroke-width:2px
    style G fill:#fef3c7,stroke:#eab308,stroke-width:2px
    style H fill:#fef3c7,stroke:#eab308,stroke-width:2px
    style I fill:#fef3c7,stroke:#eab308,stroke-width:2px
```
1. User Upload: User uploads audio files (up to 30) via the Telegram bot and signals completion.

2. Bot to Backend: The bot forwards files and user ID to the backend server.

# Backend Processing (Asynchronous):

- Queuing: Files are added to a job queue.

- Audio-to-Text: Audio is transcribed.

- LLM Extraction: LLM extracts "Nama," "Alamat," and "Jumlah minuman" from the text.

- Data Aggregation: Extracted records are collected.

- Report Generation: A CSV report is created from the aggregated data.

- Notification & Download: The backend notifies the bot, which then sends the CSV file or download link to the user.

- Cleanup (Optional): Old files are deleted from temporary storage.

# Key Considerations
1. LLM Prompt Engineering: Critical for accurate data extraction.

2. Handling Multiple Mentions: Logic to parse multiple entries from a single audio file.

3. Error Handling: Robust mechanisms for all potential failure points.

4. Security: Secure APIs, API key management, and file handling.

5. Scalability: Job queue and cloud services are key.

6. Cost Management: Monitor usage of cloud STT/LLM services.

7. Rate Limiting: Adherence to API limits of Telegram and other services.

8. User Experience (UX): Clear status updates and handling of processing times.

# Getting Started
(This section would typically include instructions on how to set up, configure, and run the project, including dependencies, API key setup, and deployment steps. This will depend on the specific technologies chosen for implementation.)

# Example setup steps (placeholder)
### 1. Clone the repository
git clone [repository-url]
cd [repository-name]

### 2. Install dependencies For Python backend (example)
pip install -r requirements.txt

### 3. Configure environment variables (e.g., TELEGRAM_BOT_TOKEN, LLM_API_KEY, CLOUD_STORAGE_CREDENTIALS)
- cp .env.example .env
- Edit .env with your credentials

### 4. Run the application (e.g., python app.py or docker-compose up)


# Contributing
(This section would outline how others can contribute to the project, including coding standards, pull request processes, and issue reporting.)

License
(Specify the license under which the project is released, e.g., MIT, Apache 2.0.)