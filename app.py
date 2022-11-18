import pymongo
import os
import certifi
from datetime import datetime
import static.notepolis as np
import static.youtubedl as yt
from flask import Flask, render_template, jsonify, request, redirect, url_for

app = Flask(__name__)
# 1l8l6s8l4IXFrZHE
# tlsCAFile=certifi.where()

client = pymongo.MongoClient(
    "mongodb+srv://notepolisadmin:notepolisadmin@notepolis.r1hsy.mongodb.net/?retryWrites=true&w=majority",
    tlsCAFile=certifi.where())
db = client.notepolis


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/transnote')
def trans():
    vn = request.args.get('vidiname') # 동영상 이름
    pn = request.args.get('name') # PDF 이름
    np.notepolis(pn, vn)
    mydata = list(db.impVidi.find({'vidiname': vn}, {'_id': False}))
    print(mydata)
    return jsonify({'all_diary': mydata})


@app.route('/impVidi', methods=['POST'])
def importvideo():
    if request.method == "POST":

        name_receive = request.form['name_give']
        mode_receive = request.form['mode_give']
        url_receive = request.form['url_give']
        today = datetime.now()
        mytime = today.strftime('%Y-%m-%d-%H-%M-%S')
        filename = f'{name_receive}-{mytime}'
        # url mode or download mode
        # url mode
        if url_receive != '-':
            yt.downYT(url_receive, filename)
        # download mode
        else:
            file = request.files["file_give"]
            extension = file.filename.split('.')[-1]
            save_to = f'static/{filename}.{extension}'
            file.save(save_to)

        doc = {
            'url': url_receive,
            'name': name_receive,
            'mode': mode_receive,
            'file': f'{filename}.mp4',
            'vidiname': filename,
            'time': today.strftime('%Y.%m.%d')
        }
        db.impVidi.insert_one(doc)
        return redirect(url_for("trans", vidiname=filename, name=name_receive))


@app.route('/intro')
def intro():
    return render_template('intro.html')


@app.route('/FAQ')
def faq():
    return render_template('faq.html')


@app.route('/bug_report')
def bug():
    return render_template('bug_report.html')


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/patch')
def patch():
    return render_template('patch.html')


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
