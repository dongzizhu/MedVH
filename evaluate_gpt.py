import openai
import json
import base64
from tqdm import tqdm
import time
import requests

openai.api_key = '' # Your OpenAI key

# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


if __name__ == '__main__':
    eval_data = json.load(open("multi_choices/test_wrongful_image.json", 'r'))
    all_answer = []
    # gpt-4V
    for qdata in tqdm(eval_data):
        image_path = "multi_choices/wrongful_image/{}".format(qdata['img_name'])
        prompt = "Please respond with the correct answer letter. No explanation is needed. Question: {} Choices: {}".format(qdata['question'], qdata['choices'])
        base64_image = encode_image(image_path)
        # Sometime it fails due to internet or some other reason. Just retry it.
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {openai.api_key}"
        }
        payload = {
        "model": "gpt-4-vision-preview",
        "messages": [
            { "role": "system", "content": "You are a well-trained radiologist being asked a multi-choice question regarding an image. " },
            {
            "role": "user",
            "content": [
                {
                "type": "text",
                "text": prompt
                },
                {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"
                }
                }
            ]
            }
        ],
        "max_tokens": 500
        }
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        

        all_answer.append(response.json()['choices'][0]['message']['content'])
        time.sleep(2) # Need to pause for some time because the tokens is limited through Azure API 


    count = 0
    for r, vqa in zip(all_answer, eval_data):
        if r[0] == vqa['gt']:
            count += 1
    print('Accuracy: {}'.format(count/len(eval_data)))