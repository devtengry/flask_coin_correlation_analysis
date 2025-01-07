from flask import Flask, render_template, request, jsonify, Response
from functions import download_data, create_correlation_chart, find_top_correlated
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')  # Ana sayfa (templates/index.html)


@app.route('/download', methods=['POST'])
def download():
    try:
        # Kullanıcıdan gelen form verilerini al
        day = int(request.form['day'])
        period = request.form['period']

        # Veri indirme işlemi
        download_data(day, period)

        # Başarılı mesajı JSON olarak döndür
        return jsonify({"message": "Data downloaded and cached successfully!"})
    except Exception as e:
        # Hata durumunda mesaj döndür
        return jsonify({"error": str(e)}), 500


@app.route('/correlation', methods=['POST'])
def correlation():
    # Kullanıcıdan coin bilgisini al
    coin = request.form['coin']

    try:
        # En yüksek korelasyonlu coinleri bul
        top_coins = find_top_correlated(coin)
        return jsonify({"coin": coin, "top_correlations": top_coins})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@app.route('/plot', methods=['POST'])
def plot():
    coin1 = request.form['coin1']
    coin2 = request.form['coin2']

    try:
        # Normalize coins to Binance symbol format in the function
        output_path = create_correlation_chart(coin1, coin2)
        return jsonify({"plot_url": output_path})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    app.run(debug=True)
