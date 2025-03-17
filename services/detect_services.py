# import cv2
# import numpy as np
# from fastapi import HTTPException, UploadFile
# import tensorflow as tf


# # Load the pre-trained TensorFlow model once
# model_path = "models/Ismail-Lung-Model.tflite"
# interpreter = tf.lite.Interpreter(model_path=model_path)
# interpreter.allocate_tensors()

# # Get input and output tensor details
# input_details = interpreter.get_input_details()
# output_details = interpreter.get_output_details()

# # Categories for model predictions
# categories = ["Benign cases", "Malignant cases", "Normal cases"]
# unit_size = 256


# # Image Detection Service
# async def detect_service(file: UploadFile, provider_id: int):
#     if not provider_id:
#         raise HTTPException(status_code=401, detail="Invalid provider")

#     try:
#         # Read file and convert to NumPy array
#         content = await file.read()
#         np_img = np.frombuffer(content, np.uint8)

#         # Decode image using OpenCV
#         image = cv2.imdecode(np_img, cv2.IMREAD_GRAYSCALE)  # Read as grayscale
#         if image is None:
#             raise HTTPException(status_code=400, detail="Invalid image format")

#         # Resize image to match model input size
#         image = cv2.resize(image, (unit_size, unit_size))

#         # Normalize and reshape for model input
#         input_data = np.expand_dims(image / 255.0, axis=(0, -1)).astype(np.float32)

#         # Perform inference
#         interpreter.set_tensor(input_details[0]["index"], input_data)
#         interpreter.invoke()
#         output_data = interpreter.get_tensor(output_details[0]["index"])
#         prediction = np.argmax(output_data, axis=-1)[0]

#         return {"predicted_category": categories[prediction]}

#     except Exception as e:
#         raise HTTPException(
#             status_code=500, detail=f"Error processing image or predicting: {str(e)}"
#         )


import cv2
import numpy as np
from fastapi import HTTPException, UploadFile
from model_loader import model_cache

# Categories for model predictions
categories = ["Benign cases", "Malignant cases", "Normal cases"]
unit_size = 256


# Image Detection Service
async def detect_service(file: UploadFile, provider_id: int):
    if not provider_id:
        raise HTTPException(status_code=401, detail="Invalid provider")

    # Ensure the model is loaded
    if "interpreter" not in model_cache:
        raise HTTPException(status_code=500, detail="Model not loaded")

    try:
        interpreter = model_cache["interpreter"]
        input_details = model_cache["input_details"]
        output_details = model_cache["output_details"]

        # Read file and convert to NumPy array
        content = await file.read()
        np_img = np.frombuffer(content, np.uint8)

        # Decode image using OpenCV
        image = cv2.imdecode(np_img, cv2.IMREAD_GRAYSCALE)
        if image is None:
            raise HTTPException(status_code=400, detail="Invalid image format")

        # Resize and normalize image
        image = cv2.resize(image, (unit_size, unit_size))
        input_data = np.expand_dims(image / 255.0, axis=(0, -1)).astype(np.float32)

        # Perform inference
        interpreter.set_tensor(input_details[0]["index"], input_data)
        interpreter.invoke()
        output_data = interpreter.get_tensor(output_details[0]["index"])
        prediction = np.argmax(output_data, axis=-1)[0]

        return {"predicted_category": categories[prediction]}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")
