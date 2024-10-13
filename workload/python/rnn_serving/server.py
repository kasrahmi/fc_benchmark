import psutil
import os
import pickle
import torch
import rnn
import io
import string
import boto3

# Track memory usage
pid = os.getpid()
python_process = psutil.Process(pid)
memory_use_old = 0
memory_use = python_process.memory_info()[0] / 2.**20  # memory use in MB

# S3 setup
BUCKET_NAME = 'kasrahmi-benchmark'
s3_client = boto3.client('s3')

# Print memory usage
print("--- RNN SERVING ---")
print('Memory use 1:', memory_use - memory_use_old)

# Download model parameters from S3
def download_s3_file(bucket, object_name, local_filename):
    try:
        s3_client.download_file(bucket, object_name, local_filename)
        print(f"Successfully downloaded {object_name} from {bucket}.")
        return True
    except Exception as e:
        print(f"Error downloading {object_name} from S3: {e}")
        return False

# Download the model parameters and other required files
download_s3_file(BUCKET_NAME, 'rnn_params.pkl', 'rnn_params.pkl')
download_s3_file(BUCKET_NAME, 'rnn_model.pth', 'rnn_model.pth')

# Load RNN parameters
with open('rnn_params.pkl', 'rb') as f:
    params = pickle.load(f)

# Load RNN model
all_categories = ['French', 'Czech', 'Dutch', 'Polish', 'Scottish', 'Chinese', 'English', 'Italian', 'Portuguese', 
                  'Japanese', 'German', 'Russian', 'Korean', 'Arabic', 'Greek', 'Vietnamese', 'Spanish', 'Irish']
n_categories = len(all_categories)
all_letters = string.ascii_letters + " .,;'-"
n_letters = len(all_letters) + 1

# Initialize the RNN model
rnn_model = rnn.RNN(n_letters, 128, n_letters, all_categories, n_categories, all_letters, n_letters)
rnn_model.load_state_dict(torch.load('rnn_model.pth', map_location=torch.device('cpu')))
rnn_model.eval()

memory_use_old = memory_use
memory_use = python_process.memory_info()[0] / 2.**20  # memory use in MB
print('Memory use 2:', memory_use - memory_use_old)

# Function to generate text using RNN
def generate_text(language, start_letters):
    output_names = list(rnn_model.samples(language, start_letters))
    return output_names

# Main function to handle the S3 input and output
def main():
    # Download input file from S3
    input_filename = 'in.txt'
    download_s3_file(BUCKET_NAME, input_filename, input_filename)
    
    # Read input file (assumed to contain a language and a starting letter string)
    with open(input_filename, 'r') as f:
        input_data = f.read().strip().split('\n')
    
    # Extract the language and start letters from the input file
    if len(input_data) < 2:
        print("Invalid input file format. Expected two lines: language and start_letters.")
        return
    
    language = input_data[0]  # First line is the language
    start_letters = input_data[1]  # Second line is the start letters
    
    print(f"Input Language: {language}, Start Letters: {start_letters}")
    
    # Perform the RNN serving
    output_names = generate_text(language, start_letters)

    # Save the output to a string and upload it to S3
    output_str = str(output_names)
    output_filename = 'out.txt'

    # Upload output file to S3
    s3_client.put_object(Body=output_str, Bucket=BUCKET_NAME, Key=output_filename)
    print(f"Output uploaded to {output_filename} in S3.")

    return {"Prediction": "correct"}

# Execute the main function
if __name__ == '__main__':
    main()

# Track memory usage again
memory_use_old = memory_use
memory_use = python_process.memory_info()[0] / 2.**20  # memory use in MB
print('Memory use 3:', memory_use - memory_use_old)
