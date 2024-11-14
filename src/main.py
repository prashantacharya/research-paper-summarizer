import glob
from pathlib import Path
from claude import build_batch_request_object, make_batch_request, process_batch_response, track_batch_requests
from util import load_existing_log
from constants import LOG_OUTPUT_FILE


def main():
    home = Path.home()
    all_files = glob.glob(f"{home}/Zotero/storage/*/*.pdf")

    output_log = load_existing_log(LOG_OUTPUT_FILE)

    already_summarized_files = [entry["file"] for entry in output_log]
    not_already_summarized_files = [file for file in all_files if Path(file).name not in already_summarized_files]

    print(f"Following files have already been summarized:\n{("\n").join(already_summarized_files)}")
    print(f"Following files need to be summarized:\n{("\n").join(not_already_summarized_files)}")

    # Sending the batches of 5 at a time
    # To avoid hiting the limit of 32 MB per batch
    files_to_batch = not_already_summarized_files[:15]

    batch_request, request_tracker = build_batch_request_object(files_to_batch)
    batch_request_response = make_batch_request(batch_request)

    track_batch_requests(batch_request_response)
    process_batch_response(batch_request_response.id, request_tracker)

if __name__ == "__main__":
    main()

