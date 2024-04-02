import os
import base64
from time import perf_counter
from PIL import Image
from transformers import BlipProcessor, BlipForQuestionAnswering
# from image_optimization.bg_remover import utilities
# from image_optimization.bg_remover.bg import remove
from dotenv import load_dotenv
from image_optimization.DIS.IS_Net.white_bg import white_bg_generate

load_dotenv('.env')

question_list = ["Is the complete background white?",
                 "Is the object clearly visible?",
                 "Is the image of good quality?",
                 "Is there any shadow or reflection in the image?",
                 "Is the object boundary merging with the background?",
                 "Is there any other thing than main object present in image?",
                 "Is the object boundary shredded"]

correct_ans = ["yes","yes","yes","no","no","no","no"]
reasons = ["bg","visible","quality","shadow and reflection","boundary","other object","shredded"]


processor = BlipProcessor.from_pretrained("Salesforce/blip-vqa-capfilt-large")
model = BlipForQuestionAnswering.from_pretrained("Salesforce/blip-vqa-capfilt-large")

# def remove_image_background(input_path, output_path, debugger=False):
#     default_parameters = {
#         'model': 'u2net',
#         'alpha_matting': False,
#         'alpha_matting_foreground_threshold': 240,
#         'alpha_matting_background_threshold': 10,
#         'alpha_matting_erode_size': 10,
#         'alpha_matting_base_size': 1000,
#     }

#     input_path, output_path = os.path.abspath(input_path), os.path.abspath(output_path)

#     with open(input_path, 'rb') as file:
#         image = file.read()
#     t1 = perf_counter()
#     img_removed_bg_bytes = remove(image, model_name=default_parameters['model'],alpha_matting=default_parameters['alpha_matting'], alpha_matting_foreground_threshold=default_parameters['alpha_matting_foreground_threshold'],alpha_matting_background_threshold=default_parameters['alpha_matting_background_threshold'],alpha_matting_erode_structure_size=default_parameters['alpha_matting_erode_size'],alpha_matting_base_size=default_parameters['alpha_matting_base_size'])
#     if debugger: print(f"{output_path} done. Took {(perf_counter()-t1):003} seconds.")
#     with open(output_path, 'wb') as file:
#         file.write(img_removed_bg_bytes)

def remove_image_background(input_path, output_path):
    white_bg_generate(input_path,output_path)

def convert_to_number(score):
    word_to_number = {
        'zero': 0,
        'one': 1,
        'two': 2,
        'three': 3,
        'four': 4,
        'five': 5,
        'six': 6,
        'seven': 7,
        'eight': 8,
        'nine': 9,
        'ten': 10
    }

    if isinstance(score, str):
        lower_case_score = score.lower()
        return word_to_number.get(lower_case_score, None)
    else:
        return score

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def qualitycheck(image_path):
    raw_image = Image.open(image_path)
    for i in range(len(question_list)):
        inputs = processor(raw_image, question_list[i], return_tensors="pt")
        out = model.generate(**inputs)
        print(processor.decode(out[0], skip_special_tokens=True))
        res = processor.decode(out[0], skip_special_tokens=True)
        if res!=correct_ans[i]:
            print("reason to fail:",reasons[i])
            return False
    return True