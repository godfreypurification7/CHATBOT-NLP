import json
import nltk
import numpy as np
from nltk.stem import WordNetLemmatizer
import random 

import tensorflow as tf
from tensorflow.keras.models import Sequential  # pyright: ignore[reportMissingImports]
from tensorflow.keras.layers import Dense, Dropout  # pyright: ignore[reportMissingImports]

import pickle
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')


lemmatizer = WordNetLemmatizer()
words = []
classes = []
documents = []
ignore_words = ['?', '!', '.', ',']

with open('intents.json') as file:
    intents = json.load(file)


for intent in intents['intents']:
    for pattern in intent['patterns']:
        w =nltk.word_tokenize(pattern)
        words.extend(w)
        documents.append((w,intent['tag']))
        if intent['tag'] not in classes:
            classes.append(intent['tag'])

words =[lemmatizer.lemmatize(w.lower()) for w in words if w not in ignore_words]
words=sorted(list(set(words))) 
classes = sorted(list(set(classes)))

with open('words.pkl', 'wb') as f:
    pickle.dump(words, f)
with open('classes.pkl', 'wb') as f:
    pickle.dump(classes, f)


training = []
output_empty=[0]*len(classes) 

for doc in documents:
    pattern_words = [lemmatizer.lemmatize(word.lower()) for word in doc[0]]
    bag = [1 if w in pattern_words else 0 for w in words]
    
    output_row = list(output_empty)
    output_row[classes.index(doc[1])] = 1
    training.append([bag, output_row])



random.shuffle(training)
train_x=np.array([item[0] for item in training])
train_y=np.array([item[1] for item in training])

model=Sequential()
model.add(Dense(128, input_shape=(len(train_x[0]),), activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(64, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(len(train_y[0]), activation='softmax'))

sgd=tf.keras.optimizers.SGD(learning_rate=0.01,momentum=0.9, nesterov=True)
model.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=['accuracy'])


hist = model.fit(train_x, train_y, epochs=200, batch_size=5, verbose=1)
model.save('chatbotmodel.h5')
np.save('data', train_x)
np.save('data', train_y)
model.summary()
print(f"Training samples: {len(training)}")
print(f"Number of intents: {len(classes)}")
print(f"Vocabulary size: {len(words)}")

# https://github.com/NeuralNine/youtube-tutorials/tree/main/AI%20Chatbot%20PyTorch

# {
#     "intents": [
#       {
#         "tag": "greeting",
#         "patterns": ["Hi", "Hello", "Hey", "Greetings"],
#         "responses": ["Hello!", "Hi there!", "Hey!", "Greetings!"]
#       },
#       {
#         "tag": "goodbye",
#         "patterns": ["Bye", "Goodbye", "See you later"],
#         "responses": ["Goodbye!", "See you soon!", "Bye!"]
#       }
#     ]
#   }