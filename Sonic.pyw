import sys
import numpy as np
import pyaudio
from PyQt5.QtWidgets import QApplication, QMainWindow, QSlider, QLabel, QVBoxLayout, QWidget, QPushButton, QHBoxLayout, QLineEdit
from PyQt5.QtCore import Qt, QTimer

class UltrasonicEmitter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sonic")

        # Frequency Slider
        self.frequency_slider = QSlider(Qt.Horizontal)
        self.frequency_slider.setRange(0, 100000)  # Adjusted frequency range to 0 to 100,000 Hz
        self.frequency_slider.setValue(20000)
        self.frequency_slider.valueChanged.connect(self.slider_changed)

        # Frequency Input
        self.frequency_input = QLineEdit("20000")
        self.frequency_input.returnPressed.connect(self.input_changed)

        # Volume Slider
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        self.volume_slider.valueChanged.connect(self.update_volume)

        # Labels
        self.frequency_label = QLabel("Frequency: 20000 Hz")
        self.volume_label = QLabel("Volume: 50%")

        # Play/Stop Button
        self.play_button = QPushButton("Play")
        self.play_button.clicked.connect(self.toggle_play)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.frequency_label)
        layout.addWidget(self.frequency_input)
        layout.addWidget(self.frequency_slider)
        layout.addWidget(self.volume_label)
        layout.addWidget(self.volume_slider)
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.play_button)
        layout.addLayout(button_layout)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Sound generation variables
        self.is_playing = False
        self.p = pyaudio.PyAudio()
        self.stream = None
        self.frequency = 20000
        self.volume = 0.5
        self.timer = QTimer()
        self.timer.timeout.connect(self.generate_sound)

    def slider_changed(self):
        self.frequency = self.frequency_slider.value()
        self.frequency_label.setText(f"Frequency: {self.frequency} Hz")
        self.frequency_input.setText(str(self.frequency))

    def input_changed(self):
        text = self.frequency_input.text()
        try:
            frequency = int(text)
            if 0 <= frequency <= 100000:
                self.frequency_slider.setValue(frequency)
                self.frequency = frequency
                self.frequency_label.setText(f"Frequency: {self.frequency} Hz")
            else:
                raise ValueError("Frequency out of range")
        except ValueError:
            self.frequency_input.setText(str(self.frequency))  # Reset to the previous valid value

    def update_volume(self):
        self.volume = self.volume_slider.value() / 100.0
        self.volume_label.setText(f"Volume: {self.volume * 100:.0f}%")

    def toggle_play(self):
        if self.is_playing:
            self.stop_playing()
        else:
            self.start_playing()

    def start_playing(self):
        self.is_playing = True
        self.play_button.setText("Stop")
        self.stream = self.p.open(format=pyaudio.paFloat32,
                                  channels=1,
                                  rate=44100,
                                  output=True)
        self.timer.start(100)  # Timer to periodically generate sound

    def stop_playing(self):
        self.is_playing = False
        self.play_button.setText("Play")
        self.timer.stop()
        self.stream.stop_stream()
        self.stream.close()

    def generate_sound(self):
        sample_rate = 44100
        duration = 0.1  # seconds
        samples = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
        waveform = (np.sin(2 * np.pi * self.frequency * samples) * self.volume).astype(np.float32)
        if self.stream.is_active():
            self.stream.write(waveform.tobytes())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = UltrasonicEmitter()
    window.show()
    sys.exit(app.exec_())
