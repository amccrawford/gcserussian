import sounddevice as sd
import soundfile as sf
import numpy as np
import os
import threading
import time

class AudioRecorder:
    def __init__(self, sample_rate=44100, channels=1, dtype='int16', chunk_size=1024):
        self.sample_rate = sample_rate
        self.channels = channels
        self.dtype = dtype
        self.chunk_size = chunk_size
        self._recording = False
        self._frames = []
        self._stream = None

    def _callback(self, indata, frames, time_info, status):
        """Callback function for the sounddevice stream."""
        if status:
            print(status, flush=True)
        if self._recording:
            self._frames.append(indata.copy())

    def record_audio_fixed(self, output_filename, duration=5):
        """
        Records audio for a fixed duration (in seconds) without user interaction.
        """
        self._frames = []
        self._recording = True
        print(f"Recording for {duration} seconds...")
        
        try:
            with sd.InputStream(samplerate=self.sample_rate, channels=self.channels, 
                                dtype=self.dtype, blocksize=self.chunk_size, 
                                callback=self._callback):
                sd.sleep(duration * 1000)

        except Exception as e:
            print(f"Error during recording: {e}")
        finally:
            self._recording = False
            self._save_recording(output_filename)
            print("Recording stopped.")

    def record_audio_manual(self, output_filename):
        """
        Records audio from the microphone, controlled by user pressing Enter to start and stop.
        Saves the recording to the specified output_filename.
        """
        self._frames = []
        self._recording = True
        
        print("\nPress Enter to START recording...")
        input() # Wait for user to press Enter to start

        print("Recording... Press Enter to STOP recording.")
        
        # Use a non-blocking input check for the stop signal
        stop_event = threading.Event()
        input_thread = threading.Thread(target=lambda: (input(), stop_event.set()))
        input_thread.daemon = True
        input_thread.start()

        try:
            with sd.InputStream(samplerate=self.sample_rate, channels=self.channels, 
                                dtype=self.dtype, blocksize=self.chunk_size, 
                                callback=self._callback):
                while self._recording and not stop_event.is_set():
                    sd.sleep(100) # Small sleep to avoid busy-waiting

        except Exception as e:
            print(f"Error during recording: {e}")
        finally:
            self._recording = False # Ensure recording flag is set to False
            self._save_recording(output_filename)
            print("Recording stopped.")


    def _save_recording(self, output_filename):
        """Saves the recorded frames to a WAV file."""
        if not self._frames:
            print("No audio recorded.")
            return

        recorded_audio = np.concatenate(self._frames, axis=0)
        sf.write(file=output_filename, data=recorded_audio, samplerate=self.sample_rate)
        print(f"Audio saved to {output_filename}")

if __name__ == "__main__":
    recorder = AudioRecorder()
    output_file = "user_response.wav"
    recorder.record_audio_manual(output_file)
