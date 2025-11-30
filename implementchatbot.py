import json
import pickle
import random
import nltk
from nltk.stem import WordNetLemmatizer
from tensorflow.keras.models import load_model 
import numpy as np
import re
import wikipedia

# Load resources
lemmatizer = WordNetLemmatizer()
with open('intents.json') as f:
    intents_data = json.load(f)
words = pickle.load(open('words.pkl', 'rb'))
classes = pickle.load(open('classes.pkl', 'rb'))
model = load_model('chatbotmodel.h5')

# Updated clean_up_sentence to handle numbers
def clean_up_sentence(sentence):
    sentence = re.sub(r"[^a-zA-Z0-9\s]", "", sentence)
    sentence = sentence.lower().strip()
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word) for word in sentence_words]
    return sentence_words

def bag_of_word(sentence, vocabulary, show_details=False):
    sentence_words = clean_up_sentence(sentence)
    bag = [0] * len(vocabulary)
    for s in sentence_words:
        for i, w in enumerate(vocabulary):
            if w == s:
                bag[i] = 1
                if show_details:
                    print("found in bag: %s" % w)
    return np.array(bag)

def predict_class(sentence, model):
    p = bag_of_word(sentence, words, show_details=False)
    res = model.predict(np.array([p]))[0]
    ERROR_THRESHOLD = 0.75
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]
    results.sort(key=lambda x: x[1], reverse=True)
    print("DEBUG - Prediction results:", results)
    return [{"intent": classes[r[0]], "probability": str(r[1])} for r in results]

def get_wikipedia_summary(query):
    try:
        summary = wikipedia.summary(query, sentences=2)
        return summary
    except wikipedia.exceptions.PageError:
        return "Sorry, I couldn't find a Wikipedia page on that topic."
    except wikipedia.exceptions.DisambiguationError as e:
        return f"Your query is ambiguous. Can you be more specific? Perhaps you meant one of these: {e.options}"

# Updated get_response to accept 'user_message' and handle new intents
def get_response(intents_list, intents_json, user_message):
    if not intents_list:
        return "Sorry, I didn't understand that. Can you please rephrase?"

    tag = intents_list[0]['intent']

    # Handle general knowledge queries
    if tag == 'general_knowledge':
        response = get_wikipedia_summary(user_message)
        return response

    # Handle specific number queries
    if tag == 'specific_number_query':
        match = re.search(r'\d+', user_message)
        if match:
            number = match.group(0)
            return f"The number you mentioned is {number}. What would you like to know about it?"
        else:
            return "I recognize you're asking about a number, but I couldn't find one in your question."

    # Existing logic for other intents
    for intent in intents_json['intents']:
        if intent['tag'] == tag:
            return random.choice(intent['responses'])

    return "Sorry, I didn't find a response for that."

# Chat loop
print("Start chatting with the bot!")
while True:
    message = input("You: ")
    if message.lower() in ['quit', 'exit']:
        print("Bot: Goodbye!")
        break

    intents_list = predict_class(message, model)
    # Corrected function call: pass the 'message' variable
    response = get_response(intents_list, intents_data, message)
    print(f"Bot: {response}")

# jahid - 01988899815   ,avp union capital
# https://www.google.com/search?q=build+a+chatbot+from+scratch+in+python+step+by+step+in+tensorflow+code+sample+&client=ms-google-coop&sca_esv=684e68df3968da6d&cx=005305742766141300566%3Ajc9gtvxee8o&biw=1366&bih=641&sxsrf=AE3TifNWwStjxFhd7-JQ-5Ly_YP09iqsQA%3A1756012196715&ei=pJ6qaJS0K6KP4-EPnuae6Qw&ved=0ahUKEwiUltOZ16KPAxWixzgGHR6zJ80Q4dUDCBA&uact=5&oq=build+a+chatbot+from+scratch+in+python+step+by+step+in+tensorflow+code+sample+&gs_lp=Egxnd3Mtd2l6LXNlcnAiTmJ1aWxkIGEgY2hhdGJvdCBmcm9tIHNjcmF0Y2ggaW4gcHl0aG9uIHN0ZXAgYnkgc3RlcCBpbiB0ZW5zb3JmbG93IGNvZGUgc2FtcGxlIEiQiAFQwE5Y6YYBcAF4AZABAJgBswKgAZUTqgEHMC43LjQuMbgBA8gBAPgBAZgCAaACCMICChAAGLADGNYEGEeYAwCIBgGQBgiSBwExoAfQC7IHALgHAMIHAzItMcgHBg&sclient=gws-wiz-serp





