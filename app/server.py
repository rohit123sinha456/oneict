#from matplotlib.pyplot import imread
import tensorflow as tf
import cv2
import numpy as np
from flask import Flask,request,jsonify
import os
from werkzeug.utils import secure_filename
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
#from models import predict
from app import app,current_app

def test_image(rawimage):
	classes = ['Bacterial_leaf_blight', 'blast', 'brownspot', 'tungro']
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

def upload_file():
	if request.method == 'POST':
		if 'file' not in request.files:
			return "No File Found"
		file = request.files['file']
		if file.filename == '':
			return "No File Found"
		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
			print("./images/"+filename,file.filename)
			diseasewithid = {"Bacterial_leaf_blight":"6137c0d973dd001324bc2539","blast":"613c77b00757c728104e9a26","brownspot":"61386ab373dd001324bc25ba","tungro":"6188a7b250a9d516548d0ac4","healthy":"h1e2a3l4t5h6y7"}
			output_class,confidence = test_image("./images/"+filename)
			out = diseasewithid[output_class]
			outputformat = {"success": True,"message": "result found successfully","data": {"_id":out,"opinion":"IDK","efficiency":str(confidence*100)}}
		return jsonify(outputformat)#  out #labels[np.argmax(out)]

#if __name__ == '__main__':
#	with app.app_context():
#		current_app.model = tf.keras.models.load_model("model_with_tungro.h5",custom_objects={'KerasLayer':hub.KerasLayer})
#	app.run()



#git add . && git commit -m "v1.1" && git push heroku master --> for pushing to heroku
