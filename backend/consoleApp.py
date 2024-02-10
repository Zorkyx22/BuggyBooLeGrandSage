import requests
from Body import Body
from config import (BACKEND_URL)

def CreateUserMessage(message):
    return {"role":"user","content":message}

def CreateAssistantMessage(message):
    return {"role":"assistant","content":message}

if __name__ == "__main__":
    print("-=[ Pour quitter, appuyez sur CTRL+C ]=-")
    clientConversation = []
    askPath = f"{BACKEND_URL}/ask"
    try:
        while(True):
            user=input(f"\n{('*' * 50)}\n\nVotre question pour le chatbot : ")
            clientConversation.append(CreateUserMessage(user))
            assistant = requests.post(askPath, json=Body(conversation=clientConversation).model_dump(), headers={"Content-Type": "application/json; charset=utf-8"})
            if assistant.status_code == 200:
                textResponse = assistant.json()['response']
                print(f"\nRéponse : {textResponse}")
                clientConversation.append(CreateAssistantMessage(textResponse))
            else:
                print("-=[ Une erreur est survenue ]=-")
    except KeyboardInterrupt:
        print("\n" + ("*" * 25) + "\n-=[ Au revoir! ]=-")