import random
import json
import pickle
import numpy as np


import nltk
from nltk.stem import WordNetLemmatizer
from tensorflow.keras.models import load_model
from fastapi import FastAPI,Body
from fastapi.middleware.cors import CORSMiddleware

lemmatizer = WordNetLemmatizer()

intents = json.loads(open('intents.json').read())
words=pickle.load(open("words.pkl","rb"))
classes=pickle.load(open("classes.pkl","rb"))
model=load_model("chatbot_model.h5")


def clean_up_sentence(sentence):
    sentence_words=nltk.word_tokenize(sentence)
    sentence_words=[lemmatizer.lemmatize(word) for word in sentence_words]
    return sentence_words
def bag_of_words(sentence):
    sentence_words=clean_up_sentence(sentence)
    bag=[0]*len(words)
    for w in sentence_words:
        for i,word in enumerate(words):
            if word==w:
                bag[i]=1
    return np.array(bag)

def predict_class(sentence):
    bow=bag_of_words(sentence)
    res=model.predict(np.array([bow]))[0]
    ERROR_THRESHOLD = 0.25
    results =[[i,r] for i,r in enumerate(res) if r > ERROR_THRESHOLD]
    results.sort(key=lambda x:x[1],reverse=True)
    return_list=[]
    for r in results:
        return_list.append({"intent":classes[r[0]],"probability":str(r[1])})
    return return_list

def get_response(intent_list,intent_json):
    tag=intent_list[0]["intent"]
    list_of_intents=intent_json['intents']
    # print(intent_list)
    for i in list_of_intents:
        if i['tag'] ==tag: 
            result=random.choice(i['responses'])
            break
    return result

done = False

# while not done:
#     message = input("Enter a message: ")
#     if message == "STOP":
#         done = True
#     else:
        # init=predict_class(message)
        # print("======>",init,"<=====")
        # print(get_response(init,intents))
        

app = FastAPI()
origins = [
   "http://localhost:3200",
]

app.add_middleware(
   CORSMiddleware,
   allow_origins=origins,
   allow_credentials=True,
   allow_methods=["*"],
   allow_headers=["*"],
)
@app.post("/chat")
def chat_bot(body=Body(question="hi?", default="default_value")):
    print(body)
    init=predict_class(body["question"])
    print(init)
    res=get_response(init,intents)
    return {"error": "false","message":"got response successful","result":res,"init":init}

@app.get("/")
def server_check():

    return {"error": "false","message":"server working"}

