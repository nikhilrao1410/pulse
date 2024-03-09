from flask_cors import CORS
from flask import jsonify
from flask import Flask, render_template, Response, jsonify
import cv2
import numpy as np
import sys

app = Flask(__name__)
CORS(app)

# Webcam Parameters
webcam = None
if len(sys.argv) == 2:
    webcam = cv2.VideoCapture(sys.argv[1])
else:
    webcam = cv2.VideoCapture(0)
realWidth = 640*2
realHeight = 480*2
videoWidth = 320*2
videoHeight = 240*2
videoChannels = 3
videoFrameRate = 15
webcam.set(3, realWidth)
webcam.set(4, realHeight)

# Color Magnification Parameters
levels = 3
alpha = 170
minFrequency = 1.0
maxFrequency = 2.0
bufferSize = 150
bufferIndex = 0

# Output Display Parameters
font = cv2.FONT_HERSHEY_SIMPLEX
loadingTextLocation = (20, 30)
bpmTextLocation = (videoWidth // 2 + 5, 30)
fontScale = 1
fontColor = (255, 255, 255)
lineType = 2
boxColor = (0, 255, 0)
boxWeight = 3

# Initialize Gaussian Pyramid
firstFrame = np.zeros((videoHeight, videoWidth, videoChannels))
firstGauss = cv2.pyrDown(firstFrame)
for _ in range(levels - 1):
    firstGauss = cv2.pyrDown(firstGauss)

videoGauss = np.zeros((bufferSize, firstGauss.shape[0], firstGauss.shape[1], videoChannels))
fourierTransformAvg = np.zeros((bufferSize))

# Bandpass Filter for Specified Frequencies
frequencies = (1.0 * videoFrameRate) * np.arange(bufferSize) / (1.0 * bufferSize)
mask = (frequencies >= minFrequency) & (frequencies <= maxFrequency)

# Heart Rate Calculation Variables
bpmCalculationFrequency = 15
bpmBufferIndex = 0
bpmBufferSize = 10
bpmBuffer = np.zeros((bpmBufferSize))

def build_gauss(frame, levels):
    pyramid = [frame]
    for level in range(levels):
        frame = cv2.pyrDown(frame)
        pyramid.append(frame)
    return pyramid

def reconstruct_frame(pyramid, index, levels):
    filtered_frame = pyramid[index]
    for level in range(levels):
        filtered_frame = cv2.pyrUp(filtered_frame)
    filtered_frame = filtered_frame[:videoHeight, :videoWidth]
    return filtered_frame

def generate_frames():
    global bufferIndex, bpmBufferIndex, bpmBuffer
    while True:
        ret, frame = webcam.read()
        if not ret:
            break

        detection_frame = frame[videoHeight // 2:realHeight - videoHeight // 2,
                                videoWidth // 2:realWidth - videoWidth // 2, :]

        # Construct Gaussian Pyramid
        videoGauss[bufferIndex] = build_gauss(detection_frame, levels + 1)[levels]
        fourier_transform = np.fft.fft(videoGauss, axis=0)

        # Bandpass Filter
        fourier_transform[mask == False] = 0

        # Grab a Pulse
        if bufferIndex % bpmCalculationFrequency == 0:
            for buf in range(bufferSize):
                fourierTransformAvg[buf] = np.real(fourier_transform[buf]).mean()
            hz = frequencies[np.argmax(fourierTransformAvg)]
            bpm = 60.0 * hz
            bpmBuffer[bpmBufferIndex] = bpm
            bpmBufferIndex = (bpmBufferIndex + 1) % bpmBufferSize

        # Amplify
        filtered = np.real(np.fft.ifft(fourier_transform, axis=0))
        filtered = filtered * alpha

        # Reconstruct Resulting Frame
        filtered_frame = reconstruct_frame(filtered, bufferIndex, levels)
        output_frame = detection_frame + filtered_frame
        output_frame = cv2.convertScaleAbs(output_frame)

        bufferIndex = (bufferIndex + 1) % bufferSize

        _, jpeg = cv2.imencode('.jpg', output_frame)
        frame = jpeg.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/get_heart_rate')
def get_heart_rate():
    global bpmBuffer
    avg_heart_rate = np.mean(bpmBuffer)
    return jsonify({"bpm": avg_heart_rate})

if __name__ == '__main__':
    app.run(debug=True)
