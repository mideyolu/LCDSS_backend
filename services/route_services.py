from fastapi import HTTPException, UploadFile
import tensorflow as tf
from PIL import Image
from io import BytesIO
import numpy as np

# Load the pre-trained TensorFlow model once
model_path = 'models/Ismail-Lung-Model.tflite'
interpreter = tf.lite.Interpreter(model_path=model_path)
interpreter.allocate_tensors()

# Get input and output tensor details
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# Categories for model predictions
categories = ['Benign cases', 'Malignant cases', 'Normal cases']
unit_size = 256


# Image Detection Service
async def detect_service(file: UploadFile, provider_id: int):
    if not provider_id:
        raise HTTPException(status_code=401, detail="Invalid provider")

    try:
        content = await file.read()
        image = Image.open(BytesIO(content)).convert('L').resize((unit_size, unit_size))
        input_data = np.expand_dims(np.array(image) / 255.0, axis=(0, -1)).astype(np.float32)

        interpreter.set_tensor(input_details[0]['index'], input_data)
        interpreter.invoke()
        output_data = interpreter.get_tensor(output_details[0]['index'])
        prediction = np.argmax(output_data, axis=-1)[0]

        return {"predicted_category": categories[prediction]}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image or predicting: {str(e)}")

