import random
from spacy.util import minibatch, compounding


# Set the random seed for reproducibility
random.seed(42)

# Shuffle the dataset
random.shuffle(dataset)

# Define the split ratios
train_ratio = 0.8  # 80% for training
val_ratio = 0.1  # 10% for validation
test_ratio = 0.1  # 10% for testing

# Calculate the sizes of each split
total_size = len(dataset)
train_size = int(train_ratio * total_size)
val_size = int(val_ratio * total_size)

# Split the dataset into train, validation, and test sets
train_data = dataset[:train_size]
val_data = dataset[train_size:train_size + val_size]
test_data = dataset[train_size + val_size:]

# Print the sizes of each split
print(f"Training set size: {len(train_data)}")
print(f"Validation set size: {len(val_data)}")
print(f"Test set size: {len(test_data)}")
