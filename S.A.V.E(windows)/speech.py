import os
import sys
import numpy as np
import threading
import sounddevice as sd
import queue
import tkinter as tk
from tkinter import ttk, filedialog
from tkinter import scrolledtext
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import speech_recognition as sr
import requests
import json
import wave
import tempfile

class SuicideRiskDetector:
    def __init__(self):
        # Initialize the speech recognizer
        self.recognizer = sr.Recognizer()
        
        # Audio processing parameters
        self.sample_rate = 16000
        self.audio_buffer = queue.Queue()
        self.streaming_active = False
        
        # Groq API settings
        self.groq_api_key = "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"
        self.groq_endpoint = "https://api.groq.com/openai/v1/chat/completions"
        
        print("Suicide risk detector initialized.")

    def transcribe_audio(self, audio_data=None, audio_path=None):
        """Convert speech to text using SpeechRecognition library"""
        try:
            if audio_path:
                # Load audio file
                with sr.AudioFile(audio_path) as source:
                    audio = self.recognizer.record(source)
            elif audio_data is not None:
                # Use provided audio data
                audio = audio_data
            else:
                return ""
                
            # Use Google's speech recognition (free and reliable)
            text = self.recognizer.recognize_google(audio)
            return text
        except sr.UnknownValueError:
            print("Speech recognition could not understand audio")
            return ""
        except sr.RequestError as e:
            print(f"Could not request results from service; {e}")
            return ""
        except Exception as e:
            print(f"Transcription error: {e}")
            return ""

    def analyze_text_with_groq(self, text):
        """Send text to Groq API for suicide risk analysis"""
        if not text.strip():
            return {"risk_level": "unknown", "confidence": 0.0, "transcription": ""}
            
        headers = {
            "Authorization": f"Bearer {self.groq_api_key}",
            "Content-Type": "application/json"
        }
        
        system_prompt = (
            "You are a mental health risk detection assistant. Analyze the following text and determine whether "
            "it indicates suicidal thoughts or intentions. Return only a JSON with two keys: 'risk_level' (one of "
            "'suicide', 'medium_risk', 'low_risk', or 'non_suicide') and 'confidence' (a float between 0 and 1 "
            "indicating likelihood of suicide risk). Be nuanced in your assessment."
        )
        
        payload = {
            "model": "llama3-70b-8192",  # Using a model available on Groq
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            "response_format": {"type": "json_object"}  # Ensure proper JSON formatting
        }
        
        try:
            response = requests.post(self.groq_endpoint, json=payload, headers=headers, timeout=15)
            response.raise_for_status()
            output = response.json()['choices'][0]['message']['content']
            
            # Parse the JSON response
            result = json.loads(output)
            
            # Map the risk levels to our application's format
            risk_mapping = {
                "suicide": "high",
                "medium_risk": "medium",
                "low_risk": "low",
                "non_suicide": "minimal"
            }
            
            # Convert to our standard format
            return {
                "risk_level": risk_mapping.get(result["risk_level"], "unknown"),
                "confidence": result["confidence"],
                "transcription": text
            }
            
        except requests.exceptions.RequestException as e:
            print(f"API request error: {e}")
            return {"risk_level": "error", "confidence": 0.0, "transcription": text}
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            return {"risk_level": "error", "confidence": 0.0, "transcription": text}
        except Exception as e:
            print(f"Error analyzing text: {e}")
            return {"risk_level": "error", "confidence": 0.0, "transcription": text}

    def process_audio_file(self, file_path):
        """Process an audio file and return the risk assessment."""
        # Convert file to WAV if needed (for compatibility with speech_recognition)
        if not file_path.lower().endswith('.wav'):
            # Create a temporary WAV file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_wav:
                temp_path = temp_wav.name
            
            # This is a simplified approach - in a real application, 
            # you'd want proper audio format conversion
            try:
                # For this example, we'll just assume the file is compatible
                # In a real app, use pydub or another library to convert formats properly
                temp_path = file_path
            except Exception as e:
                print(f"Error converting audio format: {e}")
                return {"risk_level": "error", "confidence": 0.0, "transcription": ""}
        else:
            temp_path = file_path
            
        # Transcribe the audio
        text = self.transcribe_audio(audio_path=temp_path)
        
        # Send the text to Groq for analysis
        return self.analyze_text_with_groq(text)

    def start_streaming(self, callback):
        """Start streaming audio for real-time processing."""
        self.streaming_active = True
        
        def audio_callback(indata, frames, time, status):
            if status:
                print(f"Stream error: {status}")
            # Add the audio data to the buffer
            self.audio_buffer.put(indata.copy())
        
        def processing_thread():
            # Create a recognizer for this thread
            thread_recognizer = sr.Recognizer()
            
            # Buffer for accumulating audio segments
            audio_frames = []
            chunk_duration = 0
            required_duration = 3  # Process in 3-second chunks
            
            while self.streaming_active:
                try:
                    # Get audio chunk from the buffer
                    audio_chunk = self.audio_buffer.get(timeout=1)
                    audio_frames.append(audio_chunk)
                    chunk_duration += len(audio_chunk) / self.sample_rate
                    
                    if chunk_duration >= required_duration:
                        # Combine all audio frames
                        combined_audio = np.vstack(audio_frames)
                        
                        # Save as temporary WAV file
                        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_wav:
                            temp_path = temp_wav.name
                            
                        with wave.open(temp_path, 'wb') as wf:
                            wf.setnchannels(1)
                            wf.setsampwidth(2)  # 16-bit audio
                            wf.setframerate(self.sample_rate)
                            wf.writeframes((combined_audio * 32767).astype(np.int16).tobytes())
                        
                        # Now use speech_recognition with the file
                        with sr.AudioFile(temp_path) as source:
                            audio_data = thread_recognizer.record(source)
                            
                        # Try to transcribe
                        try:
                            text = thread_recognizer.recognize_google(audio_data)
                            if text:
                                # Analyze with Groq
                                result = self.analyze_text_with_groq(text)
                                callback(result)
                        except sr.UnknownValueError:
                            print("Could not understand audio")
                        except Exception as e:
                            print(f"Error processing audio: {e}")
                        
                        # Clean up temp file
                        try:
                            os.unlink(temp_path)
                        except:
                            pass
                        
                        # Reset accumulation
                        audio_frames = []
                        chunk_duration = 0
                        
                except queue.Empty:
                    continue
                except Exception as e:
                    print(f"Processing error: {e}")
            
            print("Streaming thread stopped")
        
        # Start audio capture
        self.stream = sd.InputStream(
            callback=audio_callback,
            channels=1,
            samplerate=self.sample_rate,
            blocksize=int(self.sample_rate * 0.5)  # 0.5 second blocks
        )
        self.stream.start()
        
        # Start processing thread
        self.process_thread = threading.Thread(target=processing_thread)
        self.process_thread.daemon = True
        self.process_thread.start()

    def stop_streaming(self):
        """Stop streaming audio."""
        self.streaming_active = False
        if hasattr(self, 'stream'):
            self.stream.stop()
            self.stream.close()

class SuicideDetectionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Suicide Risk Speech Detection")
        self.root.geometry("900x700")
        self.root.configure(bg="#f0f0f0")
        
        # Initialize the detector
        self.detector = SuicideRiskDetector()
        
        # Create GUI elements
        self.create_widgets()
        
        # Status flag
        self.is_streaming = False

    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(
            main_frame, 
            text="Suicide Risk Speech Detection System", 
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=10)
        
        # Tab control
        self.tab_control = ttk.Notebook(main_frame)
        
        # File tab
        file_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(file_tab, text="File Analysis")
        
        # Real-time tab
        realtime_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(realtime_tab, text="Real-time Analysis")
        
        self.tab_control.pack(expand=True, fill=tk.BOTH)
        
        # File tab contents
        file_frame = ttk.Frame(file_tab, padding="10")
        file_frame.pack(fill=tk.BOTH, expand=True)
        
        # File selection
        file_select_frame = ttk.Frame(file_frame)
        file_select_frame.pack(fill=tk.X, pady=10)
        
        self.file_path_var = tk.StringVar()
        file_entry = ttk.Entry(file_select_frame, textvariable=self.file_path_var, width=60)
        file_entry.pack(side=tk.LEFT, padx=5)
        
        browse_btn = ttk.Button(file_select_frame, text="Browse", command=self.browse_file)
        browse_btn.pack(side=tk.LEFT, padx=5)
        
        analyze_btn = ttk.Button(file_select_frame, text="Analyze", command=self.analyze_file)
        analyze_btn.pack(side=tk.LEFT, padx=5)
        
        # Results display for file analysis
        results_frame = ttk.LabelFrame(file_frame, text="Analysis Results", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Transcription display
        transcription_label = ttk.Label(results_frame, text="Transcription:")
        transcription_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.transcription_text = scrolledtext.ScrolledText(results_frame, height=6, wrap=tk.WORD)
        self.transcription_text.pack(fill=tk.X, expand=True, pady=(0, 10))
        
        # Risk assessment display
        risk_frame = ttk.Frame(results_frame)
        risk_frame.pack(fill=tk.X, pady=10)
        
        self.risk_level_var = tk.StringVar(value="Not analyzed")
        risk_level_label = ttk.Label(risk_frame, text="Risk Level:")
        risk_level_label.grid(row=0, column=0, sticky=tk.W, padx=5)
        risk_level_value = ttk.Label(risk_frame, textvariable=self.risk_level_var, font=("Arial", 12, "bold"))
        risk_level_value.grid(row=0, column=1, sticky=tk.W, padx=5)
        
        self.confidence_var = tk.StringVar(value="")
        confidence_label = ttk.Label(risk_frame, text="Confidence:")
        confidence_label.grid(row=1, column=0, sticky=tk.W, padx=5)
        confidence_value = ttk.Label(risk_frame, textvariable=self.confidence_var)
        confidence_value.grid(row=1, column=1, sticky=tk.W, padx=5)
        
        # Create risk meter for file analysis
        self.file_risk_figure = plt.Figure(figsize=(6, 2), dpi=100)
        self.file_risk_ax = self.file_risk_figure.add_subplot(111)
        self.file_risk_canvas = FigureCanvasTkAgg(self.file_risk_figure, results_frame)
        self.file_risk_canvas.get_tk_widget().pack(fill=tk.X, expand=True)
        self.setup_risk_meter(self.file_risk_ax)
        self.file_risk_canvas.draw()
        
        # Real-time tab contents
        realtime_frame = ttk.Frame(realtime_tab, padding="10")
        realtime_frame.pack(fill=tk.BOTH, expand=True)
        
        # Control buttons
        control_frame = ttk.Frame(realtime_frame)
        control_frame.pack(fill=tk.X, pady=10)
        
        self.start_btn = ttk.Button(control_frame, text="Start Listening", command=self.toggle_streaming)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        # Live results display
        live_results_frame = ttk.LabelFrame(realtime_frame, text="Live Analysis", padding="10")
        live_results_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Live transcription
        live_transcription_label = ttk.Label(live_results_frame, text="Live Transcription:")
        live_transcription_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.live_transcription_text = scrolledtext.ScrolledText(live_results_frame, height=6, wrap=tk.WORD)
        self.live_transcription_text.pack(fill=tk.X, expand=True, pady=(0, 10))
        
        # Live risk assessment
        live_risk_frame = ttk.Frame(live_results_frame)
        live_risk_frame.pack(fill=tk.X, pady=10)
        
        self.live_risk_level_var = tk.StringVar(value="Not streaming")
        live_risk_level_label = ttk.Label(live_risk_frame, text="Current Risk Level:")
        live_risk_level_label.grid(row=0, column=0, sticky=tk.W, padx=5)
        live_risk_level_value = ttk.Label(live_risk_frame, textvariable=self.live_risk_level_var, font=("Arial", 12, "bold"))
        live_risk_level_value.grid(row=0, column=1, sticky=tk.W, padx=5)
        
        self.live_confidence_var = tk.StringVar(value="")
        live_confidence_label = ttk.Label(live_risk_frame, text="Confidence:")
        live_confidence_label.grid(row=1, column=0, sticky=tk.W, padx=5)
        live_confidence_value = ttk.Label(live_risk_frame, textvariable=self.live_confidence_var)
        live_confidence_value.grid(row=1, column=1, sticky=tk.W, padx=5)
        
        # Create risk meter for real-time analysis
        self.rt_risk_figure = plt.Figure(figsize=(6, 2), dpi=100)
        self.rt_risk_ax = self.rt_risk_figure.add_subplot(111)
        self.rt_risk_canvas = FigureCanvasTkAgg(self.rt_risk_figure, live_results_frame)
        self.rt_risk_canvas.get_tk_widget().pack(fill=tk.X, expand=True)
        self.setup_risk_meter(self.rt_risk_ax)
        self.rt_risk_canvas.draw()
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready. Select a file or start real-time analysis.")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X, pady=(5, 0))
        
        # Disclaimer
        disclaimer_text = (
            "DISCLAIMER: This tool is for educational purposes only and is not a substitute for "
            "professional mental health assessment. Always seek help from qualified mental health "
            "professionals for concerns about suicide risk."
        )
        disclaimer_label = ttk.Label(main_frame, text=disclaimer_text, wraplength=800, foreground="red")
        disclaimer_label.pack(side=tk.BOTTOM, fill=tk.X, pady=5)

    def setup_risk_meter(self, ax):
        """Set up a visual risk meter."""
        ax.clear()
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_title("Risk Assessment Meter")
        ax.set_xticks([0.0, 0.25, 0.5, 0.75, 1.0])
        ax.set_xticklabels(["No Risk", "Low", "Medium", "High", "Severe"])
        ax.set_yticks([])
        
        # Add color gradient background
        gradient = np.linspace(0, 1, 100).reshape(1, -1)
        ax.imshow(gradient, aspect='auto', extent=[0, 1, 0, 1], cmap='RdYlGn_r')
        
        # Add marker for current risk
        self.risk_marker = ax.axvline(x=0, color='blue', linestyle='-', linewidth=3)
        
    def update_risk_meter(self, ax, canvas, risk_score):
        """Update the risk meter with a new score."""
        # Remove previous marker if exists
        if hasattr(self, 'risk_marker'):
            self.risk_marker.remove()
            
        # Add new marker
        self.risk_marker = ax.axvline(x=risk_score, color='blue', linestyle='-', linewidth=3)
        canvas.draw()

    def browse_file(self):
        """Browse for an audio file."""
        filetypes = (
            ("Audio files", "*.wav *.mp3 *.ogg *.flac"),
            ("All files", "*.*")
        )
        file_path = filedialog.askopenfilename(filetypes=filetypes)
        if file_path:
            self.file_path_var.set(file_path)

    def analyze_file(self):
        """Analyze the selected audio file."""
        file_path = self.file_path_var.get()
        if not file_path:
            self.status_var.set("Error: No file selected.")
            return
        
        if not os.path.exists(file_path):
            self.status_var.set(f"Error: File not found: {file_path}")
            return
            
        self.status_var.set(f"Analyzing file: {os.path.basename(file_path)}...")
        self.root.update()
        
        try:
            # Process audio file
            result = self.detector.process_audio_file(file_path)
            
            # Update UI with results
            self.transcription_text.delete(1.0, tk.END)
            self.transcription_text.insert(tk.END, result.get("transcription", ""))
            
            self.risk_level_var.set(result["risk_level"].upper())
            self.confidence_var.set(f"{result['confidence']:.2%}")
            
            # Update risk meter
            self.file_risk_ax.clear()
            self.setup_risk_meter(self.file_risk_ax)
            self.update_risk_meter(self.file_risk_ax, self.file_risk_canvas, result["confidence"])
            
            # Color coding based on risk level
            risk_colors = {
                "minimal": "green",
                "low": "yellow",
                "medium": "orange",
                "high": "red",
                "unknown": "gray",
                "error": "gray"
            }
            
            color = risk_colors.get(result["risk_level"], "black")
            self.transcription_text.tag_configure("risk_color", foreground=color)
            self.transcription_text.tag_add("risk_color", "1.0", "end")
            
            self.status_var.set(f"Analysis complete: {result['risk_level'].upper()} risk detected")
            
        except Exception as e:
            self.status_var.set(f"Error during analysis: {str(e)}")
    
    def toggle_streaming(self):
        """Toggle real-time audio streaming."""
        if not self.is_streaming:
            # Start streaming
            try:
                self.detector.start_streaming(self.update_live_results)
                self.is_streaming = True
                self.start_btn.config(text="Stop Listening")
                self.status_var.set("Listening for speech...")
                
            except Exception as e:
                self.status_var.set(f"Error starting stream: {str(e)}")
        else:
            # Stop streaming
            try:
                self.detector.stop_streaming()
                self.is_streaming = False
                self.start_btn.config(text="Start Listening")
                self.status_var.set("Listening stopped.")
                
            except Exception as e:
                self.status_var.set(f"Error stopping stream: {str(e)}")
    
    def update_live_results(self, result):
        """Update the UI with live analysis results."""
        # Using tkinter's after method to update from the main thread
        self.root.after(0, lambda: self._update_live_results_ui(result))
    
    def _update_live_results_ui(self, result):
        # Update transcription
        self.live_transcription_text.delete(1.0, tk.END)
        self.live_transcription_text.insert(tk.END, result.get("transcription", ""))
        
        # Update risk assessment
        self.live_risk_level_var.set(result["risk_level"].upper())
        self.live_confidence_var.set(f"{result['confidence']:.2%}")
        
        # Update risk meter
        self.rt_risk_ax.clear()
        self.setup_risk_meter(self.rt_risk_ax)
        self.update_risk_meter(self.rt_risk_ax, self.rt_risk_canvas, result["confidence"])
        
        # Color coding based on risk level
        risk_colors = {
            "minimal": "green",
            "low": "yellow",
            "medium": "orange",
            "high": "red",
            "unknown": "gray",
            "error": "gray"
        }
        
        color = risk_colors.get(result["risk_level"], "black")
        self.live_transcription_text.tag_configure("risk_color", foreground=color)
        self.live_transcription_text.tag_add("risk_color", "1.0", "end")

def main():
    root = tk.Tk()
    app = SuicideDetectionApp(root)
    
    def on_closing():
        if hasattr(app, 'detector') and app.is_streaming:
            app.detector.stop_streaming()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()