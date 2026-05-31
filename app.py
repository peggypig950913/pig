from flask import Flask, render_template, jsonify
from game import Game

app = Flask(__name__)
game = Game()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/status")
def status():
    # 回傳遊戲狀態給前端
    return jsonify({
        "player_hp": game.player_hp,
        "boss_hp": game.boss_hp,
        "calories": game.calories,
        "score": game.score
    })

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
