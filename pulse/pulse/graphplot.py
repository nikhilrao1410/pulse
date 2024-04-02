from flask import Flask, render_template, Response, send_file
import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
from scipy.signal import butter, lfilter

app = Flask(__name__)

@app.route('/plot')
def plot():
    arr_red = []
    arr_green = []
    arr_blue = []

    # Read file signal.dat
    with open("signal.dat") as f:
        lines = f.readlines()
        for line in lines:
            r, g, b = line.split("%")
            arr_red.append(float(r))
            arr_green.append(float(g))
            arr_blue.append(float(b))

    # Signal processing
    green_detrended = signal.detrend(arr_blue)
    L = len(arr_red)
    bpf = butter_bandpass_filter(green_detrended, 0.8, 3, fs=30, order=3)
    even_times = np.linspace(0, L, L)
    interpolated = np.interp(even_times, even_times, bpf)
    interpolated = np.hamming(L) * interpolated
    norm = interpolated / np.linalg.norm(interpolated)
    raw = np.fft.rfft(norm * 30)
    freq = np.fft.rfftfreq(L, 1 / 30) * 60
    fft = np.abs(raw) ** 2

    # Plotting
    plt.figure()
    plt.plot(freq, fft, color="blue")
    plt.title("Band Pass Filter")
    plt.xlabel("Frequency (BPM)")
    plt.ylabel("Magnitude")
    plt.grid(True)

    # Save the plot as a temporary file
    plt_path = "temp_plot.png"
    plt.savefig(plt_path)
    plt.close()

    # Return the plot as an image
    return send_file(plt_path, mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True)
