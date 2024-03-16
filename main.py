import requests, json
import json
import tkinter as tk
import predictions
import jaro_similarity
import cv2
from tkinter import ttk

def capture():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Unable to access webcam")
        return
    ret, frame = cap.read()
    if not ret:
        print("Error: Unable to capturee frame")
        return

    cv2.imwrite(str(len(pics))+".jpg", frame)
    pics.append(str(len(pics))+".jpg")

def analyze():
    ingredients = []
    outs = []
    if len(pics) == 0:
        igs = entry.get().split(', ')
        for i in igs:
            ingredients.append(i)
    else:
        for pic in pics:
            outs.append(predictions.predict_food(pic))
        for out in outs:
            highest_rating = -1
            ig = 'fff'
            for ingredient in open("ingredients.cfg").read().split('\n'):
                rating = jaro_similarity.jaro_distance(ingredient, out)
                if rating > highest_rating:
                    ig = ingredient
                    highest_rating = rating
            ingredients.append(ig)
    print(ingredients)
    meals = get_meals(ingredients)
    for meal in meals:
        tk.Label(text=meal[0],background="gray", foreground="white").pack()


def get_meals(ingredients):
    # example to ensure we can connect to the DB
    r = requests.get('https://www.themealdb.com/api/json/v1/1/filter.php?i=chicken_breast')
    if not r:
        raise Exception(f"Non-success status code: {r.status_code}")

    baseRequest = "https://www.themealdb.com/api/json/v1/1/filter.php?i="

    #get each recipe for an individual ingredient
    mRequests = []
    for ingredient in ingredients:
        mRequests.append(json.loads(requests.get(baseRequest + ingredient).content)["meals"])

    print(mRequests)

    # overlapping temp meals
    t_meals = []
    # actual meals containing all ingredients listed
    meals = []

    for i, request in enumerate(mRequests):
        for recipe in request:
            n = recipe["strMeal"]
            id = recipe["idMeal"]
            if i == 0:
                if (len(mRequests) > 1):
                    t_meals.append((n,id))
                else:
                    meals.append((n,id))
            else:
                if (n, id) in t_meals: meals.append((n, id))
        print("\n\n")

    return meals

window = tk.Tk()
window.configure(bg='gray')

pics = []

intro = tk.Label(text="Foodipie!",background="gray", foreground="white").pack()
start = tk.Button(text="Take Picture", background="darkgray", foreground="white", command=capture).pack()
entry= ttk.Entry(window,font=('Century 12'))
entry.pack(pady= 30)
start = tk.Button(text="Submit", background="darkgray", foreground="white", command=analyze).pack()

window.mainloop()