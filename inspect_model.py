import pickle

# Open the binary file
with open('classifier.pkl', 'rb') as file:
    model = pickle.load(file)

# Print the model's configuration
print("Model Type:", type(model))
print("Model Parameters:", model.get_params())