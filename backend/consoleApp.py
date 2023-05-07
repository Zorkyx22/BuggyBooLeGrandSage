import json
from typing import List
from Body import Body
import requests
from config import BACKEND

def user(message):
    return {"role":"user","content":message}

def assistant(message):
    return {"role":"assistant","content":message}

if __name__ == "__main__":
    print("-=|===== Pour quitter, appuyez sur CTRL+C =====|=-")
    session = Body(question="", history=[])
    askPath = BACKEND + "/ask"
    try:
        while(True):
            userQuestion=input(f"\n{('*' * 50)}\n\nVotre question pour le chatbot : ")
            session.question = userQuestion
            session.history.append(user(userQuestion))
            response = requests.post(askPath, data=session.json(), headers={"Content-Type": "application/json; charset=utf-8"})
            if response.status_code == 200:
                response = response.json()['response']
                print(f"\nRéponse : {response}")
                session.history.append(assistant(response))
            elif response.status_code == 500:
                print("Erreur du serveur. Avez-vous excédé votre limite de demandes par minute?")
            else:
                print("Erreur -- réessayez plus tard")
    except KeyboardInterrupt:
        print("\n" + ("*" * 25) + "\nInterrupted question asking process...")
    print("Exiting...")