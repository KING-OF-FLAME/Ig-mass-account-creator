
import requests

def download_profile_image():
    image_url = "https://thispersondoesnotexist.com/"
    response = requests.get(image_url)
    
    if response.status_code == 200:
        image_path = "profile_picture.jpg"
        with open(image_path, 'wb') as file:
            file.write(response.content)
        
        print(f"Profile image downloaded successfully: {image_path}")
        return image_path
    else:
        print(f"Failed to download profile image. Status code: {response.status_code}")
        return None
