import tkinter as tk
from tkinter import ttk, scrolledtext
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from emotion_detections.zeye_tracking import text_based_scan ,send_alert_email

class SuicideDetectionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Suicide Risk Text Detection")
        self.root.geometry("800x700")
        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        title_label = ttk.Label(main_frame, text="Suicide Risk Text Detection", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)

        input_frame = ttk.LabelFrame(main_frame, text="Enter Text to Analyze", padding="10")
        input_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        self.text_input = scrolledtext.ScrolledText(input_frame, height=10, wrap=tk.WORD)
        self.text_input.pack(fill=tk.BOTH, expand=True, pady=5)

        samples_frame = ttk.Frame(input_frame)
        samples_frame.pack(fill=tk.X, pady=5)

        ttk.Button(samples_frame, text="Load Sample 1 (Neutral)", command=lambda: self.load_sample(1)).pack(side=tk.LEFT, padx=5)
        ttk.Button(samples_frame, text="Load Sample 2 (Concerning)", command=lambda: self.load_sample(2)).pack(side=tk.LEFT, padx=5)
        # Suicide status label (above Analyze button)
        self.status_var = tk.StringVar(value="Status: Not analyzed yet")
        self.status_label = ttk.Label(input_frame, textvariable=self.status_var, font=("Arial", 12, "italic"), foreground="blue")
        self.status_label.pack(pady=5)


        analyze_button = ttk.Button(input_frame, text="Analyze Text", command=self.analyze_text)
        analyze_button.pack(pady=10)

        results_frame = ttk.LabelFrame(main_frame, text="Analysis Results", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        self.figure = plt.Figure(figsize=(5, 3), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, results_frame)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.setup_plot()

        result_text_frame = ttk.Frame(results_frame)
        result_text_frame.pack(fill=tk.X, pady=5)

        ttk.Label(result_text_frame, text="Result:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.result_var = tk.StringVar(value="Not analyzed yet")
        ttk.Label(result_text_frame, textvariable=self.result_var, font=("Arial", 12, "bold")).grid(row=0, column=1, sticky=tk.W, padx=5)

        ttk.Label(result_text_frame, text="Confidence:").grid(row=1, column=0, sticky=tk.W, padx=5)

        self.confidence_var = tk.StringVar(value="")
        ttk.Label(result_text_frame, textvariable=self.confidence_var).grid(row=1, column=1, sticky=tk.W, padx=5)

        disclaimer = ("DISCLAIMER: This tool is for educational purposes only and is not a substitute for "
                      "professional mental health assessment. Always seek help from qualified mental health "
                      "professionals for concerns about suicide risk.")
        ttk.Label(main_frame, text=disclaimer, wraplength=700, foreground="red").pack(side=tk.BOTTOM, fill=tk.X, pady=5)

    def setup_plot(self):
        self.ax.clear()
        self.ax.set_xlim(0, 1)
        self.ax.set_ylim(0, 1)
        self.ax.set_title("Risk Probability")
        self.ax.set_xticks([0.0, 0.25, 0.5, 0.75, 1.0])
        self.ax.set_xticklabels(["0%", "25%", "50%", "75%", "100%"])
        self.ax.set_yticks([])
        gradient = np.linspace(0, 1, 100).reshape(1, -1)
        self.ax.imshow(gradient, aspect='auto', extent=[0, 1, 0, 1], cmap='RdYlGn_r')
        self.risk_marker = self.ax.axvline(x=0, color='blue', linestyle='-', linewidth=3)
        self.canvas.draw()

    def update_plot(self, risk_prob):
        self.setup_plot()
        self.risk_marker = self.ax.axvline(x=risk_prob, color='blue', linestyle='-', linewidth=3)
        self.canvas.draw()

    def load_sample(self, sample_num):
        samples = {
            1: "I've been feeling down lately but trying to stay positive and take breaks.",
            2: "I can't take it anymore. I want to end it all. Nothing makes sense."
        }
        self.text_input.delete(1.0, tk.END)
        self.text_input.insert(tk.END, samples.get(sample_num, ""))

    def analyze_text(self):
        text = self.text_input.get(1.0, tk.END).strip()
        if not text:
            self.result_var.set("Please enter some text")
            self.confidence_var.set("")
            return
        
        # Update status to show processing
        self.status_var.set("Analyzing... Please wait")
        self.root.update_idletasks()
        
        try:
            result = text_based_scan(text)
            risk_label = result.get("risk_level", "error")
            confidence = result.get("confidence", 0.0)

            if risk_label == "suicide":
                self.result_var.set("SUICIDE RISK DETECTED")
            elif risk_label == "non-suicide":
                self.result_var.set("NO SUICIDE RISK DETECTED")
            else:
                self.result_var.set("Invalid or Unknown Response")

            # Set risk status based on confidence
            if confidence >= 0.85:
                status = "Highly suicidal thought"
                send_alert_email(text, confidence)
            elif confidence >= 0.65:
                status = "Possibly suicidal thought"
            elif confidence >= 0.45:
                status = "Slightly suicidal"
            elif confidence >= 0.25:
                status = "Mild emotional distress"
            else:
                status = "No suicidal indicators"

            self.confidence_var.set(f"{confidence:.2%}")
            self.update_plot(confidence)
            self.status_var.set(f"Status: {status}")
        except Exception as e:
            print(f"Analysis error: {e}")
            self.result_var.set("Analysis error")
            self.confidence_var.set("")
            self.status_var.set(f"Error: {str(e)[:50]}...")


def main():
    root = tk.Tk()
    app = SuicideDetectionApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()