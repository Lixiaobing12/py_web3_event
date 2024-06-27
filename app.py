from flask import Flask
from dotenv import load_dotenv
from threading import Thread
from services.scan import init

load_dotenv()
app = Flask(__name__)

if __name__ == "__main__":
    print("Starting scan service...")
    Thread(target=init).start()
    app.run(debug=False, host="0.0.0.0", port=34555)
