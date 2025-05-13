import json
import os
import pandas as pd
import requests
from app import app
from flask import render_template, request, redirect, url_for # type: ignore

def list_to_html(l):
    return "<ul>"+"".join([f"<li>{e}</li>" for e in l])+"</ul>" if l else ""

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/extract', methods=["GET", "POST"])
def extract():
    if request.method == "POST":
        product_id = request.form.get("product_id")
        url = f"https://www.ceneo.pl/{product_id}#tab=reviews"
        response = requests.get(url)
        print(response.status_code)

        return redirect(url_for("product", product_id=product_id))
    return render_template("extract.html")


@app.route('/products')
def products():
    products = []
    try:
        for filename in os.listdir("./app/data/products"):
            with open(f"./app/data/products/{filename}", "r", encoding="UTF-8") as jf:
                try:
                    products.append(json.load(jf))
                except json.JSONDecodeError:
                    continue  
        if not products:
            error = "Nie pobrano jeszcze żadnych danych"
            return render_template("products.html", error=error)
        return render_template("products.html", products=products)
    except FileNotFoundError:
        error = "Nie znaleziono folderu z produktami"
        return render_template("products.html", error=error)


@app.route('/author')
def author():
    return render_template("author.html")

@app.route('/product/<int:product_id>')
def product(product_id: int):
    with open(f"./app/data/opinions/{product_id}.json", "r", encoding="UTF-8") as jf:
        try:
            opinions = json.load(jf)
        except json.JSONDecodeError:
            error = "Dla produktu o podanym id nie pobrano jeszcze opinii"
            return render_template("product.html", error=error)
    opinions = pd.DataFrame.from_dict(opinions)
    opinions.pros = opinions.pros.apply(list_to_html)
    opinions.cons = opinions.cons.apply(list_to_html)
    return render_template("product.html", opinions=opinions.to_html(classes="table table-hover"))