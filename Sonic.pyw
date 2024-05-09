import sys
import numpy as np
import pyaudio
from PyQt5.QtWidgets import (QApplication, QMainWindow, QSlider, QLabel, QVBoxLayout,
                             QWidget, QPushButton, QHBoxLayout, QLineEdit, QStatusBar, QMessageBox)
from PyQt5.QtCore import Qt, QThread
from PyQt5.QtGui import QPixmap

class SoundThread(QThread):
    def __init__(self, get_audio_data):
        super(SoundThread, self).__init__()
        self.get_audio_data = get_audio_data
        self.running = True

    def run(self):
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paFloat32, channels=1, rate=44100, output=True)
        try:
            while self.running:
                data = self.get_audio_data()
                stream.write(data)
        finally:
            stream.stop_stream()
            stream.close()
            p.terminate()

    def stop(self):
        self.running = False
        self.wait()

class UltrasonicEmitter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sonic")
        self.setupUI()
        self.sound_thread = None
        self.frequency = 20000
        self.volume = 0.5
        self.amplification_factor = 1.0
        self.amplified = False
        self.muted = False

    def setupUI(self):
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Ready")

        self.image_label = QLabel(self)
        pixmap = QPixmap('Sonic2no.png')
        self.image_label.setPixmap(pixmap.scaled(200, 200, Qt.KeepAspectRatio))

        self.frequency_slider = QSlider(Qt.Horizontal)
        self.frequency_slider.setRange(0, 100000)
        self.frequency_slider.setValue(20000)
        self.frequency_slider.valueChanged.connect(self.update_audio_settings)
        self.frequency_slider.setStyleSheet("QSlider::handle:horizontal {background-color: teal;}")

        self.frequency_input = QLineEdit("20000")
        self.frequency_input.returnPressed.connect(lambda: self.frequency_slider.setValue(int(self.frequency_input.text())))
        self.frequency_input.setStyleSheet("QLineEdit {background-color: white; color: black;}")

        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        self.volume_slider.valueChanged.connect(self.update_audio_settings)
        self.volume_slider.setStyleSheet("QSlider::handle:horizontal {background-color: teal;}")

        self.amplification_slider = QSlider(Qt.Horizontal)
        self.amplification_slider.setRange(100, 500)
        self.amplification_slider.setValue(100)
        self.amplification_slider.valueChanged.connect(self.update_amplification)
        self.amplification_slider.setStyleSheet("QSlider::handle:horizontal {background-color: teal;}")

        self.amplify_button = QPushButton("Toggle Amplification")
        self.amplify_button.clicked.connect(self.toggle_amplification)
        self.amplify_button.setStyleSheet("QPushButton {background-color: teal; color: white;}")

        self.mute_button = QPushButton("Mute")
        self.mute_button.clicked.connect(self.toggle_mute)
        self.mute_button.setStyleSheet("QPushButton {background-color: teal; color: white;}")

        self.play_button = QPushButton("Play")
        self.play_button.clicked.connect(self.toggle_play)
        self.play_button.setStyleSheet("QPushButton {background-color: teal; color: white;}")

        layout = QVBoxLayout()
        layout.addWidget(self.image_label)
        layout.addWidget(QLabel("Frequency (Hz):"))
        layout.addWidget(self.frequency_input)
        layout.addWidget(self.frequency_slider)
        layout.addWidget(QLabel("Volume (%):"))
        layout.addWidget(self.volume_slider)
        layout.addWidget(QLabel("Amplification Factor:"))
        layout.addWidget(self.amplification_slider)
        layout.addWidget(self.amplify_button)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.play_button)
        button_layout.addWidget(self.mute_button)
        layout.addLayout(button_layout)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def update_audio_settings(self):
        self.frequency = self.frequency_slider.value()
        self.volume = self.volume_slider.value() / 100.0
        self.frequency_input.setText(str(self.frequency))
        self.statusBar.showMessage(f"Frequency: {self.frequency} Hz, Volume: {int(self.volume * 100)}%, Amplification: {self.amplification_factor:.1f}x")

    def update_amplification(self, value):
        self.amplification_factor = value / 100.0
        self.statusBar.showMessage(f"Amplification set to: {self.amplification_factor:.1f}x")

    def toggle_amplification(self):
        if not self.amplified:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Amplifying the volume can cause damage to your hearing and speakers.")
            msg.setInformativeText("Do you want to proceed with amplifying the volume?")
            msg.setWindowTitle("Warning: Amplified Volume")
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            retval = msg.exec_()
            if retval == QMessageBox.Yes:
                self.amplified = True
                self.statusBar.showMessage(f"Amplification turned On. Factor: {self.amplification_factor:.1f}x")
            else:
                self.amplification_slider.setValue(100)
        else:
            self.amplified = False
            self.statusBar.showMessage("Amplification turned Off.")

    def get_audio_data(self):
        samples = np.linspace(0, 0.1, int(44100 * 0.1), endpoint=False)
        effective_volume = self.volume * self.amplification_factor if self.amplified else self.volume
        effective_volume = 0 if self.muted else effective_volume
        waveform = (np.sin(2 * np.pi * self.frequency * samples) * effective_volume).astype(np.float32)
        return waveform.tobytes()

    def toggle_mute(self):
        self.muted = not self.muted
        self.statusBar.showMessage("Muted" if self.muted else "Unmuted")
        self.volume_slider.setEnabled(not self.muted)

    def toggle_play(self):
        if self.sound_thread and self.sound_thread.isRunning():
            self.stop_playing()
        else:
            self.start_playing()

    def start_playing(self):
        self.sound_thread = SoundThread(self.get_audio_data)
        self.sound_thread.start()
        self.play_button.setText("Stop")
        self.statusBar.showMessage("Playing...")

    def stop_playing(self):
        if self.sound_thread:
            self.sound_thread.stop()
        self.play_button.setText("Play")
        self.statusBar.showMessage("Stopped")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = UltrasonicEmitter()
    window.show()
    sys.exit(app.exec_())
