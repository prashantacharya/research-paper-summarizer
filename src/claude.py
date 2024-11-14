import os
import json
import time
import dotenv
from pathlib import Path
from anthropic import Anthropic

from constants import LOG_OUTPUT_FILE, MARKDOWN_DIR
from util import get_id, load_existing_log, save_log
from base64_encoder import encode_pdf_to_base64

dotenv.load_dotenv()

client = Anthropic(default_headers={
        "anthropic-beta": "pdfs-2024-09-25",
    },
    api_key=os.environ.get("ANTHROPIC_API_KEY")
)

MODEL_NAME = "claude-3-5-sonnet-20241022"
prompt = """
    Please do the following:
        1. Read the research paper.
        2. Summarize the research paper and extract the key findings.
        3. Give me a markdown text in the following format:
            ## <TITLE>
            ### Tags
                <comma saperated tags>
            ### Summary
                <summary>
            ### Research Questions
                <research questions>
            ### Key Findings
                <key findings>
    """


def build_batch_request_object(pdf_files):
    requests = []
    request_tracker = {}

    for file in pdf_files:
        file_name = Path(file).name

        encoded_pdf_string = encode_pdf_to_base64(file)
        id = get_id()
        
        request_tracker[id] = file_name

        requests.append({
            "custom_id": id,
            "params": {
                "model": MODEL_NAME,
                "max_tokens": 5000,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "document",
                                "source": {
                                    "type": "base64",
                                    "media_type": "application/pdf",
                                    "data": encoded_pdf_string
                                }
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ]
                    }
                ]
            }
        })

    
    save_batch_requests(request_tracker)
    return requests, request_tracker


# write a function to save a log file that tracks batch reqeusts
def save_batch_requests(requests):
    log_file = "batch_requests.json"
    with open(log_file, "w") as f:
        json.dump(requests, f, indent=4)


def make_batch_request(requests):
    return client.beta.messages.batches.create(
        betas=["pdfs-2024-09-25", "message-batches-2024-09-24"],
        requests=requests
    )

def track_batch_requests(batch_request):
    message_batch = None
    while True:
        message_batch = client.beta.messages.batches.retrieve(
            batch_request.id
        )
        if message_batch.processing_status == "ended":
            break
                  
        print(f"Batch {batch_request.id} is still processing...")
        time.sleep(60)
    print(f"Batch {batch_request.id} is complete.")

def process_batch_response(batch_id, request_tracker):
    for result in client.beta.messages.batches.results(
        batch_id
    ):
        log_data = load_existing_log(LOG_OUTPUT_FILE)

        for result in client.beta.messages.batches.results(batch_id):
            try:
                custom_id = result.custom_id
                
                # Retrieve filename from request_tracker based on custom_id
                filename = request_tracker.get(custom_id)
                if not filename:
                    print(f"No filename found for custom_id {custom_id}")
                    continue

                filename = filename.replace(".pdf", "")
                markdown_filename = f"{filename}.md"
                markdown_path = f"{MARKDOWN_DIR}/{markdown_filename}"

                # Extract and format content to write to Markdown
                content = result.result.message.content[0].text  # Assuming the text content is here
                with open(markdown_path, "w") as md_file:
                    md_file.write(content)
                    print(f"Markdown exported to {markdown_path}")

                # Append to log
                log_data.append({
                    "file": filename,
                    "exportedMd": markdown_filename
                })
            except Exception as e:
                print(f"Error processing batch response: {e}")
                continue

        # Save the updated log data

    save_log(log_data, LOG_OUTPUT_FILE)
