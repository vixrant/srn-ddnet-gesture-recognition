from flask import Flask, request, jsonify, send_file
import pickle
import configparser
import os

from srn import config, HandPose
from ddnet.sampling import sampling_frame
from ddnet import Predictor

#################
# Configuration #

C = configparser.ConfigParser()
C.read(['server.cfg', 'server.local.cfg'])

app = Flask(
        __name__,
        static_folder=C['dataset']['path'],
        static_url_path='/data'
        )
app.url_map.strict_slashes = False

####################
# Machine Learning #

pose_predictor = HandPose(config)
gesture_recognizer = Predictor()

@app.route('/', methods=['POST'])
def run_networks():
    """
    Receive request and provide response
    """
    data = request.get_json(force=True)
    data_dir = data['data_dir']
    data_dir = '/'.join(data_dir.split('/')[-4:])
    poses, gif_path = pose_predictor.run(C['dataset']['path'] + '/' + data_dir)
    model_input = sampling_frame(poses)
    label = gesture_recognizer.predict(model_input)
    return {
        'label': label,
        'gif': '/' + gif_path
    }

@app.route('/srn/results/<gesture>/<finger>/<subject>/<essai>/action.gif', methods=['GET'])
def get_gif(gesture, finger, subject, essai):
    return send_file(f'srn/results/{gesture}/{finger}/{subject}/{essai}/action.gif', mimetype='image/gif')

#######
# Run #

if __name__ == '__main__':
    print(C['server'])
    app.run(debug=True, port=C['server']['port'])

