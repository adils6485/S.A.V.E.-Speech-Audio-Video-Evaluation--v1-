import cv2
import numpy as np
import os
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

class SimpleEmotionDetector:
    def __init__(self):
        # Load face detector
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        # Load eye detector
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        
        # Load smile detector
        self.smile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_smile.xml')
        
        # Define emotion states
        self.emotions = ['Neutral', 'Happy', 'Sad', 'Surprised']
        
        # Create directory for saving detected concerning emotions
        self.save_dir = 'emotion_detections'
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)

    def detect_faces(self, frame):
        """Detect faces in the frame"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )
        return gray, faces
    
    def analyze_face(self, gray, x, y, w, h):
        """Analyze facial features to determine emotion"""
        face_roi = gray[y:y+h, x:x+w]
        
        # Detect eyes
        eyes = self.eye_cascade.detectMultiScale(face_roi)
        
        # Detect smile
        smile = self.smile_cascade.detectMultiScale(
            face_roi,
            scaleFactor=1.7,
            minNeighbors=22,
            minSize=(25, 25)
        )
        
        # Compute face histogram features
        hist = cv2.calcHist([face_roi], [0], None, [8], [0, 256])
        hist_norm = hist.flatten() / sum(hist.flatten())
        
        # Calculate brightness and contrast
        brightness = np.mean(face_roi)
        contrast = np.std(face_roi)
        
        # Detect edges for feature detection
        edges = cv2.Canny(face_roi, 100, 200)
        edge_intensity = np.mean(edges)
        
        # Analyze eye region size relative to face
        eye_size_ratio = 0
        if len(eyes) > 0:
            eye_size_ratio = sum(eye[2] * eye[3] for eye in eyes) / (w * h)
        
        # Analyze emotion based on features
        if len(smile) > 0:
            # Smile detected - likely happy
            # Verify it's a genuine smile by checking other features
            smile_size = sum(s[2] * s[3] for s in smile) / (w * h)
            if smile_size > 0.05 and brightness > 100:
                emotion = 'Happy'
                confidence = min(0.85, 0.5 + smile_size * 2)
            else:
                emotion = 'Neutral'
                confidence = 0.7
        elif brightness < 90 and contrast < 50:
            # Darker face with low contrast often indicates sadness
            emotion = 'Sad'
            confidence = 0.7
        elif edge_intensity > 30 and eye_size_ratio > 0.05:
            # High edge intensity and wide eyes can indicate surprise
            emotion = 'Surprised' 
            confidence = 0.65
        else:
            # Default to neutral
            emotion = 'Neutral'
            confidence = 0.6
        
        return emotion, confidence
    
    def run_image_detection(self, image_path):
        """Detect emotions from uploaded image"""
        image = cv2.imread(image_path)
        gray, faces = self.detect_faces(image)
        
        emotions = []
        confidence = []
        
        for (x, y, w, h) in faces:
            emotion, conf = self.analyze_face(gray, x, y, w, h)
            emotions.append(emotion)
            confidence.append(conf)
            
            # Draw bounding box around face (for visual purposes)
            color = (255, 0, 0)  # Default to blue (neutral)
            if emotion == 'Happy':
                color = (0, 255, 0)  # Green
            elif emotion == 'Sad':
                color = (0, 0, 255)  # Red
            elif emotion == 'Surprised':
                color = (255, 255, 0)  # Yellow
                
            cv2.rectangle(image, (x, y), (x+w, y+h), color, 2)
        
        # Convert image for displaying in Tkinter
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(image_rgb)
        return pil_image, emotions, confidence
    
    def run_webcam_detection(self):
        """Run emotion detection on webcam feed"""
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("Error: Could not open webcam")
            return
        
        print("Starting simple emotion detection...")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to grab frame")
                break
            
            # Create a copy of the frame for emotion overlay
            display_frame = frame.copy()
            
            # Detect faces
            gray, faces = self.detect_faces(frame)
            
            for (x, y, w, h) in faces:
                # Analyze emotion
                emotion, confidence = self.analyze_face(gray, x, y, w, h)
                
                # Draw rectangle around face
                color = (255, 0, 0)  # Default blue (neutral)
                if emotion == 'Happy':
                    color = (0, 255, 0)  # Green
                elif emotion == 'Sad':
                    color = (0, 0, 255)  # Red
                elif emotion == 'Surprised':
                    color = (255, 255, 0)  # Yellow
                
                cv2.rectangle(display_frame, (x, y), (x+w, y+h), color, 2)
                
                # Display emotion text
                text = f"{emotion}: {confidence*100:.1f}%"
                cv2.putText(display_frame, text, (x, y-10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            
            cv2.imshow('Emotion Detection', display_frame)
            
            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
        
        # Release resources
        cap.release()
        cv2.destroyAllWindows()

class EmotionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Emotion Detection")
        self.root.geometry("800x600")
        self.root.config(bg="#f4f4f9")

        self.detector = SimpleEmotionDetector()
        
        # Image Display Section
        self.image_label = tk.Label(self.root, text="Upload an Image to Analyze", font=("Arial", 16), bg="#f4f4f9")
        self.image_label.pack(pady=20)
        
        self.image_canvas = tk.Canvas(self.root, width=500, height=300, bg="#e0e0e0")
        self.image_canvas.pack(pady=10)
        
        # Emotion Analysis Result Section
        self.result_label = tk.Label(self.root, text="Emotion Analysis Results will appear here", font=("Arial", 12), bg="#f4f4f9")
        self.result_label.pack(pady=10)
        
        # Buttons
        self.upload_button = tk.Button(self.root, text="Upload Image", font=("Arial", 14), bg="#4CAF50", fg="white", command=self.upload_image)
        self.upload_button.pack(pady=20, side="left", padx=30)
        
        self.webcam_button = tk.Button(self.root, text="Start Webcam", font=("Arial", 14), bg="#2196F3", fg="white", command=self.start_webcam)
        self.webcam_button.pack(pady=20, side="right", padx=30)
        
    def upload_image(self):
        """Allow user to upload an image for emotion detection"""
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.png;*.jpeg")])
        if not file_path:
            return
        
        pil_image, emotions, confidence = self.detector.run_image_detection(file_path)
        
        # Convert to Tkinter Image format
        self.display_image(pil_image)
        
        # Show the results below the image
        emotion_text = "\n".join([f"{emotions[i]}: {confidence[i]*100:.1f}%" for i in range(len(emotions))])
        self.result_label.config(text=f"Detected Emotions:\n{emotion_text}")
    
    def display_image(self, pil_image):
        """Display the uploaded image on the Tkinter canvas"""
        self.image_tk = ImageTk.PhotoImage(pil_image)
        self.image_canvas.create_image(0, 0, anchor="nw", image=self.image_tk)

    def start_webcam(self):
        """Start webcam for real-time emotion detection"""
        self.detector.run_webcam_detection()

if __name__ == "__main__":
    root = tk.Tk()
    app = EmotionApp(root)
    root.mainloop()
