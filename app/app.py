import tensorflow as tf
import cv2
import tensorflow_hub as hub
import numpy as np
from flask import Flask,request,jsonify,current_app
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
from security import api_required
import shutil

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
#from models import predict
app = Flask(__name__)
CORS(app)
UF = "./images"

if os.path.isdir(UF):
    print(UF, "already exists.")
else:
    os.mkdir(UF)
    print(UF, "is created.")

app.config['UPLOAD_FOLDER'] = UF


@app.before_first_request
def before_first_request():
	app.logger.info("Initialising AI Model for the Prediction")
	with app.app_context():
		current_app.model = tf.keras.models.load_model("model_inceptionnet_v2.h5",custom_objects={'KerasLayer':hub.KerasLayer})


def test_image(rawimage):
	classes = ['Bacterial_leaf_blight', 'blast', 'brownspot', 'tungro']
	app.logger.info("Model is predicting")
	new_model = current_app.model
	image = cv2.imread(rawimage)
	img = cv2.resize(image, (299, 299))
	img = img / 255
	output = new_model.predict(np.asarray([img]))[0]
	class_idx = np.argmax(output)
	return_value = classes[class_idx]
	confidence = output[class_idx]
	return(return_value,confidence)

def allowed_file(filename):
	return '.' in filename and \
		filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/',methods=['POST'])
@api_required
def upload_file():
	if request.method == 'POST':
		if 'file' not in request.files:
			app.logger.error("No File Found")
			return "No File Found"
		file = request.files['file']
		if file.filename == '':
			app.logger.error("No File Found")
			return "No File Found"
		if file and allowed_file(file.filename):
			app.logger.info("Image Recieved successfully")
			filename = secure_filename(file.filename)
			file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
			print("./images/"+filename,file.filename)
			diseasewithid = {"Bacterial_leaf_blight":"613c73940757c728104e9a23","blast":"6137c0d973dd001324bc2539","brownspot":"613c77b00757c728104e9a26","tungro":"61386a0473dd001324bc25b7","healthy":"h1e2a3l4t5h6y7"}
			output_class,confidence = test_image("./images/"+filename)
			out = diseasewithid[output_class]
			app.logger.info("Contructing the API response")
			outputformat = {"success": True,"message": "result found successfully","data": {"_id":out,"opinion":output_class,"efficiency":str(confidence*100)}}
		else:
			outputformat = {"Error": "File Format Not Supported. PNG, JPEG, JPG Format Only"}

		send_response = jsonify(outputformat)
		send_response.headers.add('Access-Control-Allow-Origin', '*')
		return send_response#  out #labels[np.argmax(out)]

@app.route('/clear',methods=['POST'])
@api_required
def clear_cache():
	try:
		shutil.rmtree(app.config['UPLOAD_FOLDER'])
		os.mkdir(UF)
		outputformat = {"success": True,"message": "Cached Image is cleared"}
		return jsonify(outputformat)
	except:
		app.logger.error("Can't clear cache")
		outputformat = {"success": False,"message": "Can't clear cache. Error Encountered"}
		return jsonify(outputformat)

