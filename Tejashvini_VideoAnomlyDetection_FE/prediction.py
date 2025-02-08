from tensorflow.keras.models import model_from_json
from pathlib import Path
from tensorflow.keras.preprocessing import image
import numpy as np
import matplotlib.pyplot as plt
import cv2
import os
from glob import glob
from lib_file import lib_path

class_names = class_names = {
       
    0:'Abnormal',
    1:'Normal',
  
}

f = Path("model/model_structure.json")

model_structure = f.read_text()

model = model_from_json(model_structure)

# loading the trained weights
model.load_weights("model/model_weights.h5")


def modelPrediction(user_input):
    path = os.path.join(user_input)
    print("Processing video at:", path)

    # Removing all files from the temp folder
    os.makedirs('static/temp', exist_ok=True)
    files = glob('static/temp/*')
    for f in files:
        os.remove(f)   

    cap = cv2.VideoCapture(path)   
    count = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if ret:
            if count % 30 == 0:
                filename = f'static/temp/frame_{count}.jpg'
                cv2.imwrite(filename, frame)
            count += 1
        else:
            break
    cap.release()

    # Loading frames
    images = glob("static/temp/*.jpg")
    if not images:
        print("Error: No frames extracted.")
        return "Error: No frames"

    print("Extracted Frames:", images)

    # Preprocessing frames
    prediction_images = []
    for img_path in images:
        img = image.load_img(img_path, target_size=(128, 128, 3))
        img = image.img_to_array(img) / 255.0
        prediction_images.append(img)

    prediction_images = np.array(prediction_images)
    print("Shape of prediction_images:", prediction_images.shape)

    if prediction_images.shape[0] == 0:
        print("Error: prediction_images is empty.")
        return "Error: No valid frames"

    # Prediction
    y_pred = model.predict(prediction_images, batch_size=1, verbose=0)
    y_predict = [int(np.argmax(pred)) for pred in y_pred]

    print("Predictions:", y_predict)

    from statistics import mode
    class_label = class_names[mode(y_predict)]
    print("This video is classified as:", class_label)

    return class_label