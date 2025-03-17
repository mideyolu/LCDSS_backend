# model_loader.py
import os
import tensorflow as tf
import numpy as np

# Disable OneDNN optimizations
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

# Singleton Cache for Model
model_cache = {}


async def load_model():
    """Load and cache the TensorFlow Lite model during startup."""
    model_path = "models/Ismail-Lung-Model.tflite"
    interpreter = tf.lite.Interpreter(model_path=model_path)
    interpreter.allocate_tensors()

    # Cache interpreter and details
    model_cache["interpreter"] = interpreter
    model_cache["input_details"] = interpreter.get_input_details()
    model_cache["output_details"] = interpreter.get_output_details()

    # 🔥 Run a dummy inference for warm-up
    input_shape = model_cache["input_details"][0]["shape"]
    dummy_input = np.zeros(input_shape, dtype=np.float32)
    interpreter.set_tensor(model_cache["input_details"][0]["index"], dummy_input)
    interpreter.invoke()  # Warm-up the model
