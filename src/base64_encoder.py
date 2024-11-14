import base64

def encode_pdf_to_base64(file_path):
    # Open the PDF file in binary read mode
    with open(file_path, "rb") as pdf_file:
        # Read the binary content of the file
        pdf_data = pdf_file.read()
        # Encode the binary content to Base64
        encoded_pdf = base64.b64encode(pdf_data).decode("utf-8")
    return encoded_pdf
