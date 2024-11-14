import json
import argparse

from claude import process_batch_response

def main():
    parser = argparse.ArgumentParser(description="Process a completed batch by batch request ID.")
    parser.add_argument("batch_request_id", type=str, help="The batch request ID to process")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Call the function with the provided batch request ID
    if not args.batch_request_id or len(args.batch_request_id) == 0:
        print("Error: No batch request ID provided.")
        return

    try:
        with open("batch_requests.json", "r") as file:
            batch_requests = json.load(file)
    except FileNotFoundError:
        print("Error: batch_requests.json file not found.")
        return
    except json.JSONDecodeError:
        print("Error: batch_requests.json is not a valid JSON file.")
        return


    process_batch_response(args.batch_request_id, batch_requests)

if __name__ == "__main__":
    main()
