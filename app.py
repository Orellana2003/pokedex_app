from flask import Flask, render_template, request, url_for, redirect
import requests


from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///pokedex.sqlite"

db = SQLAlchemy(app)

class Pokemon(db.Model):
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True,autoincrement=True)
    name: Mapped[str] = mapped_column(db.String, nullable=False)
    height: Mapped[float] = mapped_column(db.Float, nullable=False)
    weight: Mapped[float] = mapped_column(db.Float, nullable=False)
    order: Mapped[int] = mapped_column(db.Integer, nullable=False)
    type: Mapped[str] = mapped_column(db.String, nullable=False)

with app.app_context():
    db.create_all()


def get_pokemon_data(pokemon):
    url = f'https://pokeapi.co/api/v2/pokemon/{pokemon}'
    r = requests.get(url).json()
    return r

#que es un decorador y q la funcion retorna el html---examen
@app.route("/", methods=['GET', 'POST'])
def home():
    pokemon = None
    pokemon_types = []
    if request.method == 'POST':
        name_pokemon = request.form.get('name')
        if name_pokemon:
            data = get_pokemon_data(name_pokemon.lower())
            types_data = data.get("types")
            for item in types_data:
                pokemon_types.append(item.get("type")["name"])
            if len(pokemon_types) == 1:
                pokemon_types.append("")
            pokemon = {
                "id": data.get("id"),
                "name": data.get("name").upper(),
                "height": data.get("height"),
                "weight": data.get("weight"),
                "order": data.get("order"),
                "type": ", ".join(pokemon_types),
                "photo": data.get("sprites").get("other").get("official-artwork").get("front_default"),
            }
            new_pokemon = Pokemon(id=pokemon["id"], name=pokemon["name"], height=pokemon["height"], weight=pokemon["weight"], order=pokemon["order"], type=pokemon["type"])
            db.session.add(new_pokemon)
            db.session.commit()
    return render_template("pokemon.html", pokemon=pokemon)


@app.route("/detalle/<id>")
def detalle(id):
    data = get_pokemon_data(id)
    pokemon = {
        "photo": data.get("sprites").get("other").get("official-artwork").get("front_default"),
        "name": data.get("name").upper(),
        "HP": data.get("stats")[0].get("base_stat"),
        "attack": data.get("stats")[1].get("base_stat"),
        "defense": data.get("stats")[2].get("base_stat"),
        "speed": data.get("stats")[5].get("base_stat"),
    }
    return render_template("detalle.html", pokemon=pokemon)


#pruebas de base de datos
@app.route("/insert_pokemon/<pokemon>")
def insert(pokemon):
    new_pokemon=pokemon
    if new_pokemon:
            obj = Pokemon(pokemon)
            db.session.add(obj)
            db.session.commit()
    return "Pokemon Agregado"


@app.route("/select/<nombre>")
def selectbyname(nombre):
    poke=Pokemon.query.filter_by(name=nombre).first()
    return str(poke.id)

@app.route("/selectbyid/<id>")
def selectbyid(id):
    poke=Pokemon.query.filter_by(id=id).first()
    return str(poke.id) + str(poke.name)

@app.route("/deletebyid/<id>")
def deletebyid(id):
    pokemon_eliminar=Pokemon.query.filter_by(id=id).first()
    db.session.delete(pokemon_eliminar)
    db.session.commit()
    return "Pokemon eliminado"


if __name__ == '__main__':
    app.run(debug=True)