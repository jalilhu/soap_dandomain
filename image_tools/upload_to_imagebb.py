from imgbbpy import SyncClient
from dotenv import load_dotenv
import os


load_dotenv()

client = SyncClient(os.getenv("IMAGEBB_API_KEY")) 

def upload_image_to_imgbb(image_path):

    response = client.upload(file = image_path)
    print(f"Response from imgbb: {response}")
    return response.url 


