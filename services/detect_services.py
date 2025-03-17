# import cv2
# import numpy as np
# from fastapi import HTTPException, UploadFile
# from model_loader import model_cache

# # Categories for model predictions
# categories = ["Benign cases", "Malignant cases", "Normal cases"]
# unit_size = 256  # Image size required by the model


# # Image Detection Service
# async def detect_service(file: UploadFile, provider_id: int):
#     if not provider_id:
#         raise HTTPException(status_code=401, detail="Invalid provider")

#     # Ensure the model is loaded
#     if "interpreter" not in model_cache:
#         raise HTTPException(status_code=500, detail="Model not loaded")

#     try:
#         interpreter = model_cache["interpreter"]
#         input_details = model_cache["input_details"]
#         output_details = model_cache["output_details"]

#         # Efficiently read and decode image in one step
#         image = cv2.imdecode(
#             np.frombuffer(await file.read(), np.uint8), cv2.IMREAD_GRAYSCALE
#         )
#         if image is None:
#             raise HTTPException(status_code=400, detail="Invalid image format")

#         # Resize and normalize image
#         image = cv2.resize(image, (unit_size, unit_size))
#         input_data = np.expand_dims(image / 255.0, axis=(0, -1)).astype(np.float32)

#         # Perform inference
#         interpreter.set_tensor(input_details[0]["index"], input_data)
#         interpreter.invoke()
#         output_data = interpreter.get_tensor(output_details[0]["index"])
#         prediction = np.argmax(output_data, axis=-1)[0]

#         return {"predicted_category": categories[prediction]}

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")


import time
import cv2
import numpy as np
from fastapi import HTTPException, UploadFile
from model_loader import model_cache

# Categories for model predictions
categories = ["Benign cases", "Malignant cases", "Normal cases"]
unit_size = 256  # Image size required by the model


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

        # Efficiently read and decode image in one step
        image = cv2.imdecode(
            np.frombuffer(await file.read(), np.uint8), cv2.IMREAD_GRAYSCALE
        )
        if image is None:
            raise HTTPException(status_code=400, detail="Invalid image format")

        # Resize and normalize image
        image = cv2.resize(image, (unit_size, unit_size))
        input_data = np.expand_dims(image / 255.0, axis=(0, -1)).astype(np.float32)

        # Measure inference time
        start_time = time.time()

        # Perform inference
        interpreter.set_tensor(input_details[0]["index"], input_data)
        interpreter.invoke()
        output_data = interpreter.get_tensor(output_details[0]["index"])
        prediction = np.argmax(output_data, axis=-1)[0]

        end_time = time.time()
        inference_time_ms = (end_time - start_time) * 1000  # Convert to milliseconds

        return {
            "predicted_category": categories[prediction],
            "inference_time_ms": round(inference_time_ms, 2),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")
