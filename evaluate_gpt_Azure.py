import openai
import json
import base64
from tqdm import tqdm
import time

openai.api_key = ""
openai.api_base = "" # your endpoint should look like the following https://YOUR_RESOURCE_NAME.openai.azure.com/
openai.api_type = 'azure'
openai.api_version = '' # this might change in the future

deployment_name='' #This will correspond to the custom name you chose for your deployment when you deployed a model. 



# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


if __name__ == '__main__':
    eval_data = json.load(open("multi_choices/test_cli.json", 'r'))
    all_answer = []
    # gpt-4V
    for qdata in tqdm(eval_data):
        image_path = "multi_choices/cli/{}".format(qdata['img_name'])
        prompt = "Please respond with the correct answer letter. No explanation is needed. Question: {} Choices: {}".format(qdata['question'], qdata['choices'])
        base64_image = encode_image(image_path)
        # Sometime it fails due to internet or some other reason. Just retry it.
        try: 
            response = openai.ChatCompletion.create(
            engine=deployment_name, # The deployment name you chose when you deployed the GPT-3.5-Turbo or GPT-4 model.
            messages=[
                { "role": "system", "content": "You are a well-trained radiologist being asked a multi-choice question regarding an image. " },
                { "role": "user", "content": [  
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
                ] } 
            ],
            max_tokens=30
            )
        except:
            response = openai.ChatCompletion.create(
            engine=deployment_name, # The deployment name you chose when you deployed the GPT-3.5-Turbo or GPT-4 model.
            messages=[
                { "role": "system", "content": "You are a well-trained radiologist being asked a multi-choice question regarding an image. " },
                { "role": "user", "content": [  
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
                ] } 
            ],
            max_tokens=30
            )

        all_answer.append(response['choices'][0]['message']['content'])
        time.sleep(30) # Need to pause for some time because the tokens is limited through Azure API 


    count = 0
    for r, vqa in zip(all_answer, eval_data):
        if r[0] == vqa['gt']:
            count += 1
    print('Accuracy: {}'.format(count/len(eval_data)))