import tensorflow as tf

# Load the model
model_path = 'Ismail-Lung-Model.tflite'
interpreter = tf.lite.Interpreter(model_path=model_path)

# Get model details
details = interpreter.get_input_details()
print("Model is already quantized" if details[0]['dtype'] == 'int8' else "Model is not quantized")
