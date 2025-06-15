import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import subprocess
import os
import sys
import threading
from PIL import Image, ImageTk

class ModernSuicideRiskDetectionSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Suicide Risk Detection System")
        self.root.geometry("1100x700")
        self.root.minsize(900, 600)

        # Set theme colors
        self.bg_color = "#FFFFFF"
        self.secondary_bg = "#F5F6FA"
        self.accent_color = "#0078D7"
        self.accent_hover = "#106EBE"
        self.text_color = "#252525"
        self.secondary_text = "#666666"
        self.success_color = "#107C10"
        self.warning_color = "#D83B01"
        self.card_bg = "#FFFFFF"
        self.border_color = "#E1E1E1"

        # Configure the root window
        self.root.configure(bg=self.bg_color)

        # Font configuration
        self.title_font = ("Arial", 22, "bold")
        self.subtitle_font = ("Arial", 16, "bold")
        self.body_font = ("Arial", 11)
        self.small_font = ("Arial", 10)
        self.button_font = ("Arial", 11)

        # Configure styles
        self.configure_styles()

        # Initialize animations and effects
        self.hover_effects = {}
        self.active_module = None

        # Create main layout
        self.create_layout()

        # Running flag
        self.process_running = False
        self.current_process = None

        # Start with system ready
        self.update_status("System ready", "normal")


    def configure_styles(self):
        """Configure the ttk styles for the application"""
        self.style = ttk.Style()
        
        # Configure frame styles
        self.style.configure('Main.TFrame', background=self.bg_color)
        self.style.configure('Sidebar.TFrame', background=self.secondary_bg)
        self.style.configure('Content.TFrame', background=self.bg_color)
        self.style.configure('Card.TFrame', background=self.card_bg)
        
        # Configure label styles
        self.style.configure('Title.TLabel', 
                             background=self.bg_color, 
                             foreground=self.text_color, 
                             font=self.title_font)
        
        self.style.configure('Subtitle.TLabel', 
                             background=self.bg_color, 
                             foreground=self.text_color, 
                             font=self.subtitle_font)
        
        self.style.configure('Body.TLabel', 
                             background=self.bg_color, 
                             foreground=self.text_color, 
                             font=self.body_font)
        
        self.style.configure('Small.TLabel', 
                             background=self.bg_color, 
                             foreground=self.secondary_text, 
                             font=self.small_font)
        
        self.style.configure('Card.TLabel', 
                             background=self.card_bg, 
                             foreground=self.text_color, 
                             font=self.body_font)
        
        # Configure button styles - make them look more modern
        self.button_active_bg = "#106EBE"
        self.style.configure('TButton', 
                             font=self.button_font,
                             borderwidth=0)
        
        self.style.map('TButton',
                      background=[('active', self.button_active_bg)])
        
        # Primary button style (blue)
        self.style.configure('Primary.TButton', 
                             background=self.accent_color,
                             foreground="white")
        
        self.style.map('Primary.TButton',
                     background=[('active', self.accent_hover)],
                     foreground=[('active', 'white')])
        
        # Configure progress bar
        self.style.configure("Horizontal.TProgressbar", 
                             troughcolor=self.secondary_bg,
                             background=self.accent_color,
                             thickness=6)
    
    def create_layout(self):
        """Create the main application layout"""
        # Main container
        self.main_container = ttk.Frame(self.root, style='Main.TFrame')
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Create the two main sections
        self.create_sidebar()
        self.create_content_area()
        
        # Status bar at the bottom
        self.create_status_bar()
    
    def create_sidebar(self):
        """Create the sidebar navigation"""
        # Sidebar container with subtle shadow effect
        self.sidebar_container = tk.Frame(self.main_container, bg=self.secondary_bg, bd=0)
        self.sidebar_container.pack(side=tk.LEFT, fill=tk.Y)
        
        # Create shadow effect (right edge of sidebar)
        shadow_frame = tk.Frame(self.sidebar_container, width=1, bg="#D0D0D0")
        shadow_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Main sidebar content
        self.sidebar = ttk.Frame(self.sidebar_container, style='Sidebar.TFrame', width=250)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y, expand=False, padx=0, pady=0)
        self.sidebar.pack_propagate(False)  # Prevent sidebar from shrinking
        
        # Logo and app name
        logo_frame = ttk.Frame(self.sidebar, style='Sidebar.TFrame')
        logo_frame.pack(fill=tk.X, padx=20, pady=30)
        
        # Create a simple logo as a colored square
        logo_canvas = tk.Canvas(logo_frame, width=30, height=30, 
                               bg=self.secondary_bg, highlightthickness=0)
        logo_canvas.create_rectangle(0, 0, 30, 30, fill=self.accent_color, outline="")
        logo_canvas.pack(side=tk.LEFT, padx=(0, 10))
        
        app_title = ttk.Label(logo_frame, 
                              text="SRD System", 
                              font=self.title_font,
                              background=self.secondary_bg)
        app_title.pack(side=tk.LEFT)
        
        # Navigation menu
        nav_frame = ttk.Frame(self.sidebar, style='Sidebar.TFrame')
        nav_frame.pack(fill=tk.X, expand=False, padx=0, pady=10)
        
        # Create module buttons
        self.create_nav_button(nav_frame, "Dashboard", 
                               lambda: self.show_dashboard())
        
        # Separator with padding
        sep_frame = ttk.Frame(self.sidebar, style='Sidebar.TFrame', height=20)
        sep_frame.pack(fill=tk.X)
        
        # Modules section label
        modules_label = ttk.Label(self.sidebar, 
                                 text="DETECTION MODULES", 
                                 style='Small.TLabel',
                                 background=self.secondary_bg)
        modules_label.pack(anchor=tk.W, padx=25, pady=(0, 10))
        
        # Module buttons
        self.create_nav_button(nav_frame, "Text Analysis", 
                               lambda: self.run_module("text"),
                               color="#0078D7")
        
        self.create_nav_button(nav_frame, "Speech Analysis", 
                               lambda: self.run_module("speech"),
                               color="#107C10")
        
        self.create_nav_button(nav_frame, "Video Analysis", 
                               lambda: self.run_module("video"),
                               color="#D83B01")
        
        # Push settings to bottom with a spacer
        spacer = ttk.Frame(self.sidebar, style='Sidebar.TFrame')
        spacer.pack(fill=tk.BOTH, expand=True)
        
        # Settings at bottom
        settings_frame = ttk.Frame(self.sidebar, style='Sidebar.TFrame')
        settings_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=5, pady=5)
        
        self.create_nav_button(settings_frame, "Settings", 
                               lambda: self.show_settings(),
                               color="#767676")
        
        # Version info at the very bottom
        version_frame = ttk.Frame(self.sidebar, style='Sidebar.TFrame')
        version_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=20, pady=15)
        
        version_label = ttk.Label(version_frame, 
                                 text="v2.0.0", 
                                 style='Small.TLabel',
                                 background=self.secondary_bg)
        version_label.pack(side=tk.LEFT)
    
    def create_nav_button(self, parent, text, command=None, color=None):
        """Create a modern sidebar navigation button"""
        # Button container frame
        btn_frame = tk.Frame(parent, bg=self.secondary_bg, height=40)
        btn_frame.pack(fill=tk.X, pady=3)
        
        # Selection indicator (left blue bar)
        if color is None:
            color = self.accent_color
            
        indicator = tk.Frame(btn_frame, width=4, bg=self.secondary_bg)
        indicator.pack(side=tk.LEFT, fill=tk.Y)
        
        # Button content frame
        content_frame = tk.Frame(btn_frame, bg=self.secondary_bg)
        content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(15, 10), pady=10)
        
        # Create a simple colorful icon
        icon_size = 16
        icon_canvas = tk.Canvas(content_frame, width=icon_size, height=icon_size, 
                              bg=self.secondary_bg, highlightthickness=0)
        icon_canvas.create_rectangle(0, 0, icon_size, icon_size, fill=color, outline="")
        icon_canvas.pack(side=tk.LEFT, padx=(0, 10))
        
        # Button text
        btn_text = tk.Label(content_frame, 
                           text=text, 
                           font=self.body_font,
                           bg=self.secondary_bg,
                           fg=self.text_color)
        btn_text.pack(side=tk.LEFT, fill=tk.Y)
        
        # Store references for hover effects
        button_elements = {
            'frame': btn_frame,
            'indicator': indicator,
            'text': btn_text,
            'icon': icon_canvas,
            'color': color
        }
        
        # Bind events
        btn_frame.bind("<Enter>", lambda e, b=button_elements: self.on_nav_hover(b, True))
        btn_frame.bind("<Leave>", lambda e, b=button_elements: self.on_nav_hover(b, False))
        btn_frame.bind("<Button-1>", lambda e, c=command, b=button_elements, t=text: self.on_nav_click(c, b, t))
        btn_text.bind("<Button-1>", lambda e, c=command, b=button_elements, t=text: self.on_nav_click(c, b, t))
        icon_canvas.bind("<Button-1>", lambda e, c=command, b=button_elements, t=text: self.on_nav_click(c, b, t))
        
        # Store in hover effects dictionary
        self.hover_effects[text] = button_elements
    
    def on_nav_hover(self, elements, is_hover):
        """Handle navigation button hover effect"""
        if is_hover:
            elements['frame'].config(bg="#E6E6E6")
            elements['text'].config(bg="#E6E6E6")
            elements['icon'].config(bg="#E6E6E6")
        else:
            # Only restore normal style if not the active button
            if self.active_module != elements:
                elements['frame'].config(bg=self.secondary_bg)
                elements['text'].config(bg=self.secondary_bg)
                elements['icon'].config(bg=self.secondary_bg)
                elements['indicator'].config(bg=self.secondary_bg)
    
    def on_nav_click(self, command, elements, button_name):
        """Handle navigation button click"""
        # Reset all buttons to inactive state
        for name, btn_elements in self.hover_effects.items():
            btn_elements['frame'].config(bg=self.secondary_bg)
            btn_elements['text'].config(bg=self.secondary_bg, fg=self.text_color)
            btn_elements['indicator'].config(bg=self.secondary_bg)
            if 'icon' in btn_elements:
                btn_elements['icon'].config(bg=self.secondary_bg)
        
        # Set this button as active
        elements['frame'].config(bg="#E6E6E6")
        elements['text'].config(bg="#E6E6E6", fg=elements['color'])
        elements['indicator'].config(bg=elements['color'])
        elements['icon'].config(bg="#E6E6E6")
        
        # Store as active button
        self.active_module = elements
        
        # Execute command
        if command:
            command()
    
    def create_content_area(self):
        """Create the main content area"""
        self.content_area = ttk.Frame(self.main_container, style='Content.TFrame')
        self.content_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Show dashboard by default
        self.show_dashboard()
    
    def create_status_bar(self):
        """Create the status bar at the bottom"""
        self.status_bar = tk.Frame(self.root, bg=self.bg_color, height=32)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Status bar separator
        separator = ttk.Separator(self.status_bar, orient=tk.HORIZONTAL)
        separator.pack(fill=tk.X, side=tk.TOP)
        
        # Status message
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(self.status_bar, 
                                     textvariable=self.status_var,
                                     style='Small.TLabel')
        self.status_label.pack(side=tk.LEFT, padx=15, pady=5)
        
        # Help link
        help_label = ttk.Label(self.status_bar, 
                              text="Help & Resources", 
                              foreground=self.accent_color,
                              style='Small.TLabel',
                              cursor="hand2")
        help_label.pack(side=tk.RIGHT, padx=15, pady=5)
        help_label.bind("<Button-1>", lambda e: self.open_help())
    
    def update_status(self, message, status_type="normal"):
        """Update the status bar message with color coding"""
        self.status_var.set(message)
        
        if status_type == "normal":
            self.status_label.config(foreground=self.secondary_text)
        elif status_type == "success":
            self.status_label.config(foreground=self.success_color)
        elif status_type == "warning":
            self.status_label.config(foreground=self.warning_color)
        elif status_type == "error":
            self.status_label.config(foreground="#C42B1C")
    
    def clear_content(self):
        """Clear all widgets from the content area"""
        for widget in self.content_area.winfo_children():
            widget.destroy()
    
    def show_dashboard(self):
        """Display the dashboard view"""
        self.clear_content()
        
        # Header
        header = ttk.Frame(self.content_area, style='Content.TFrame')
        header.pack(fill=tk.X, padx=40, pady=(40, 20))
        
        title = ttk.Label(header, 
                         text="Dashboard", 
                         style='Title.TLabel')
        title.pack(side=tk.LEFT)
        
        # Main dashboard content
        dashboard = ttk.Frame(self.content_area, style='Content.TFrame')
        dashboard.pack(fill=tk.BOTH, expand=True, padx=40, pady=0)
        
        # Welcome card
        welcome_card = self.create_card(dashboard, full_width=True)
        
        welcome_title = ttk.Label(welcome_card, 
                                 text="Welcome to Suicide Risk Detection System", 
                                 style='Subtitle.TLabel',
                                 background=self.card_bg)
        welcome_title.pack(anchor=tk.W, pady=(0, 15))
        
        welcome_text = (
            "This advanced system provides tools to help identify potential suicide risk indicators "
            "through multiple modalities including text, speech, and video analysis."
            "Currently, the app supports:\n\n"
            "✓ Text-based suicide risk detection\n"
            "✓ Realtime Speech input analysis\n"
            "✓ Realtime Video emotional monitoring\n\n"
            "If a message is classified as suicidal, the system can be extended to notify an authorized contact "
            "via email for timely intervention.\n\n"
            "IMPORTANT: This system is designed for educational and research purposes only. "
            "It is not a substitute for professional mental health assessment. Always consult "
            "qualified mental health professionals for concerns about suicide risk."
        )

        
        description = ttk.Label(welcome_card, 
                              text=welcome_text,
                              style='Card.TLabel',
                              background=self.card_bg,
                              wraplength=800,
                              justify=tk.LEFT)
        description.pack(anchor=tk.W)
        
        # Create card grid layout
        cards_frame = ttk.Frame(dashboard, style='Content.TFrame')
        cards_frame.pack(fill=tk.BOTH, expand=True, pady=20)
        
        # Configure grid layout (2x2)
        cards_frame.columnconfigure(0, weight=1)
        cards_frame.columnconfigure(1, weight=1)
        
        # Module cards - Row 1
        text_card = self.create_card(cards_frame)
        text_card.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self.create_module_card_content(text_card, 
                                      "Text Analysis", 
                                      "Analyze written content for suicide risk markers.",
                                      "#0078D7",
                                      lambda: self.run_module("text"))
        
        speech_card = self.create_card(cards_frame)
        speech_card.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        self.create_module_card_content(speech_card, 
                                      "Speech Analysis", 
                                      "Identify concerning patterns in spoken language.",
                                      "#107C10",
                                      lambda: self.run_module("speech"))
        
        # Module cards - Row 2
        video_card = self.create_card(cards_frame)
        video_card.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        self.create_module_card_content(video_card, 
                                      "Video Analysis", 
                                      "Detect behavioral indicators through video.",
                                      "#D83B01",
                                      lambda: self.run_module("video"))
        
        resources_card = self.create_card(cards_frame)
        resources_card.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")
        
        # Future Scope card
        future_scope_card = self.create_card(dashboard, full_width=True)
        future_scope_title = ttk.Label(future_scope_card,
                                       text="Future Scope",
                                       style='Subtitle.TLabel',
                                       background=self.card_bg)
        future_scope_title.pack(anchor=tk.W, pady=(0, 15))

        future_scope_text = (
            "In the future, this system will integrate with social media platforms such as Twitter, Instagram, "
            "and messaging services to monitor real-time user activity. This integration will allow for early detection "
            "of concerning language and provide immediate support or escalate to professionals when needed."
        )

        future_scope_label = ttk.Label(future_scope_card,
                                       text=future_scope_text,
                                       style='Card.TLabel',
                                       background=self.card_bg,
                                       wraplength=800,
                                       justify=tk.LEFT)
        future_scope_label.pack(anchor=tk.W)


        self.create_resource_card_content(resources_card)
    
    def create_card(self, parent, full_width=False):
        """Create a modern card with subtle shadow effect"""
        # Card container for shadow effect
        card_container = tk.Frame(parent, bg=self.bg_color, bd=0)
        if full_width:
            card_container.pack(fill=tk.X, pady=10)
        
        # The actual card
        card = tk.Frame(card_container, bg=self.card_bg, bd=1, relief=tk.SOLID)
        card.config(highlightbackground=self.border_color, highlightthickness=1)
        card.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Card content padding
        content_padding = ttk.Frame(card, style='Card.TFrame')
        content_padding.pack(fill=tk.BOTH, expand=True, padx=25, pady=25)
        
        return content_padding
    
    def create_module_card_content(self, card, title, description, color, command):
        """Create content for a module card"""
        # Card title with colored indicator
        title_frame = ttk.Frame(card, style='Card.TFrame')
        title_frame.pack(fill=tk.X, anchor=tk.W, pady=(0, 15))
        
        color_indicator = tk.Frame(title_frame, width=4, bg=color, height=24)
        color_indicator.pack(side=tk.LEFT, padx=(0, 10))
        
        title_label = ttk.Label(title_frame, 
                              text=title, 
                              font=self.subtitle_font,
                              background=self.card_bg,
                              foreground=self.text_color)
        title_label.pack(side=tk.LEFT)
        
        # Description
        desc_label = ttk.Label(card, 
                             text=description,
                             style='Card.TLabel',
                             background=self.card_bg,
                             wraplength=300)
        desc_label.pack(anchor=tk.W, pady=(0, 20))
        
        # Launch button - custom styled
        launch_btn = tk.Button(card, 
                             text=f"Launch {title}",
                             bg=color,
                             fg="white",
                             font=self.button_font,
                             relief=tk.FLAT,
                             padx=15,
                             pady=8,
                             cursor="hand2",
                             activebackground=self.accent_hover,
                             activeforeground="white",
                             command=command)
        launch_btn.pack(anchor=tk.W)
    
    def create_resource_card_content(self, card):
        """Create content for the resources card"""
        # Card title
        title_frame = ttk.Frame(card, style='Card.TFrame')
        title_frame.pack(fill=tk.X, anchor=tk.W, pady=(0, 15))
        
        color_indicator = tk.Frame(title_frame, width=4, bg="#5C2D91", height=24)  # Purple
        color_indicator.pack(side=tk.LEFT, padx=(0, 10))
        
        title_label = ttk.Label(title_frame, 
                              text="Resources", 
                              font=self.subtitle_font,
                              background=self.card_bg,
                              foreground=self.text_color)
        title_label.pack(side=tk.LEFT)
        
        # Resources list
        resources_frame = ttk.Frame(card, style='Card.TFrame')
        resources_frame.pack(fill=tk.BOTH, expand=True)
        
        resources = [
            ("Crisis Text Line", "Text HOME to 741741"),
            ("National Suicide Prevention Lifeline", "1-800-273-8255"),
            ("International Association for Suicide Prevention", "iasp.info"),
            ("Documentation & User Guide", "View documentation")
        ]
        
        for name, info in resources:
            res_frame = ttk.Frame(resources_frame, style='Card.TFrame')
            res_frame.pack(fill=tk.X, pady=3)
            
            res_name = ttk.Label(res_frame, 
                               text=name,
                               style='Card.TLabel',
                               background=self.card_bg)
            res_name.pack(side=tk.LEFT)
            
            res_info = ttk.Label(res_frame, 
                               text=info,
                               style='Small.TLabel',
                               foreground=self.accent_color,
                               background=self.card_bg,
                               cursor="hand2")
            res_info.pack(side=tk.RIGHT)
            res_info.bind("<Button-1>", lambda e, n=name: self.open_resource(n))
    
    def open_resource(self, resource_name):
        """Handle opening resource links"""
        messagebox.showinfo("Resource", f"Opening resource: {resource_name}")
        
    def open_help(self):
        """Open help documentation"""
        messagebox.showinfo("Help", "Opening help and resources documentation")
    
    def show_settings(self):
        """Show settings screen"""
        self.clear_content()
        
        # Header
        header = ttk.Frame(self.content_area, style='Content.TFrame')
        header.pack(fill=tk.X, padx=40, pady=(40, 20))
        
        title = ttk.Label(header, 
                         text="Settings", 
                         style='Title.TLabel')
        title.pack(side=tk.LEFT)
        
        # Settings content
        settings_area = ttk.Frame(self.content_area, style='Content.TFrame')
        settings_area.pack(fill=tk.BOTH, expand=True, padx=40, pady=0)
        
        # Settings card
        settings_card = self.create_card(settings_area, full_width=True)
        
        # Settings options
        options_frame = ttk.Frame(settings_card, style='Card.TFrame')
        options_frame.pack(fill=tk.X, pady=10)
        
        # Settings will be added here in a real application
        settings_label = ttk.Label(options_frame, 
                                 text="Settings options will be displayed here.",
                                 style='Card.TLabel',
                                 background=self.card_bg)
        settings_label.pack(anchor=tk.W)
        
        self.update_status("Settings loaded", "normal")
    
    def run_module(self, module_type):
        """Handle module selection and display"""
        if self.process_running:
            messagebox.showinfo("Module Running", 
                              "A module is already running. Please close it before launching another.")
            return
        
        # Clear content area
        self.clear_content()
        
        # Create module view
        self.create_module_view(module_type)
    
    def create_module_view(self, module_type):
        """Create the module-specific view"""
        # Header with breadcrumb
        header = ttk.Frame(self.content_area, style='Content.TFrame')
        header.pack(fill=tk.X, padx=40, pady=(40, 20))
        
        # Breadcrumb
        breadcrumb = ttk.Frame(header, style='Content.TFrame')
        breadcrumb.pack(fill=tk.X, side=tk.TOP, pady=(0, 10))
        
        home_link = ttk.Label(breadcrumb, 
                            text="Dashboard", 
                            foreground=self.accent_color,
                            style='Small.TLabel',
                            cursor="hand2")
        home_link.pack(side=tk.LEFT)
        home_link.bind("<Button-1>", lambda e: self.show_dashboard())
        
        separator = ttk.Label(breadcrumb, 
                            text=" > ", 
                            style='Small.TLabel')
        separator.pack(side=tk.LEFT)
        
        # Set module info based on type
        if module_type == "text":
            module_title = "Text Analysis"
            module_description = "Analyze written content for indicators of suicide risk."
            module_color = "#0078D7"
            script = "./textGUI.py"
        elif module_type == "speech":
            module_title = "Speech Analysis"
            module_description = "Process audio to detect signs of suicide risk in spoken language."
            module_color = "#107C10"
            script = "./speech.py"
        elif module_type == "video":
            module_title = "Video Analysis"
            module_description = "Analyze video content for potential suicide risk indicators."
            module_color = "#D83B01"
            script = "./testing.py"
        
        current_page = ttk.Label(breadcrumb, 
                               text=module_title, 
                               style='Small.TLabel')
        current_page.pack(side=tk.LEFT)
        
        # Module title
        title_frame = ttk.Frame(header, style='Content.TFrame')
        title_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        color_bar = tk.Frame(title_frame, width=6, bg=module_color, height=36)
        color_bar.pack(side=tk.LEFT, padx=(0, 15))
        
        title = ttk.Label(title_frame, 
                         text=module_title, 
                         style='Title.TLabel')
        title.pack(side=tk.LEFT)
        
        # Main module content area
        module_content = ttk.Frame(self.content_area, style='Content.TFrame')
        module_content.pack(fill=tk.BOTH, expand=True, padx=40, pady=0)
        
        # Module info card
        info_card = self.create_card(module_content, full_width=True)
        
        # Module description
        desc_label = ttk.Label(info_card, 
                             text=module_description,
                             style='Card.TLabel',
                             background=self.card_bg,
                             wraplength=800)
        desc_label.pack(anchor=tk.W, pady=(0, 25))
        
        # Features section
        features_title = ttk.Label(info_card, 
                                 text="Key Features", 
                                 font=("Arial", 14, "bold"),
                                 background=self.card_bg)
        features_title.pack(anchor=tk.W, pady=(0, 15))
        
        # Feature list
        features_frame = ttk.Frame(info_card, style='Card.TFrame')
        features_frame.pack(fill=tk.X, pady=(0, 25))
        
        # Create bulleted feature list with checkmarks
        features = [
            "Advanced AI-powered risk assessment",
            "Detailed analysis reporting",
            "Privacy-focused data handling",
            "Research-backed detection algorithms"
        ]
        
        for feature in features:
            feature_item = ttk.Frame(features_frame, style='Card.TFrame')
            feature_item.pack(fill=tk.X, pady=3)
            
            # Create a checkmark symbol as text
            check_label = ttk.Label(feature_item, 
                                  text="✓", 
                                  foreground=module_color,
                                  background=self.card_bg,
                                  font=("Arial", 14, "bold"))
            check_label.pack(side=tk.LEFT, padx=(0, 10))
            
            # Feature text
            feature_text = ttk.Label(feature_item, 
                                   text=feature,
                                   style='Card.TLabel',
                                   background=self.card_bg)
            feature_text.pack(side=tk.LEFT)
            
        # Launch section
        launch_frame = ttk.Frame(info_card, style='Card.TFrame')
        launch_frame.pack(fill=tk.X, pady=10)
        
        # Launch button with the module's color
        launch_btn = tk.Button(launch_frame, 
                             text=f"Launch {module_title}",
                             bg=module_color,
                             fg="white",
                             font=self.button_font,
                             relief=tk.FLAT,
                             padx=20,
                             pady=10,
                             cursor="hand2",
                             activebackground=self.button_active_bg,
                             activeforeground="white",
                             command=lambda: self.launch_module_script(script, module_title))
        launch_btn.pack(side=tk.LEFT)
        
        # Status display that will update during module execution
        self.module_status_frame = ttk.Frame(module_content, style='Content.TFrame')
        self.module_status_frame.pack(fill=tk.X, pady=20)
        
        self.status_title = ttk.Label(self.module_status_frame,
                                    text="Module Status:",
                                    style='Subtitle.TLabel')
        self.status_title.pack(anchor=tk.W, pady=(0, 10))
        
        self.status_message = ttk.Label(self.module_status_frame,
                                      text="Ready to launch",
                                      style='Body.TLabel')
        self.status_message.pack(anchor=tk.W)
        
        # Progress bar (initially hidden)
        self.progress_frame = ttk.Frame(self.module_status_frame, style='Content.TFrame')
        self.progress = ttk.Progressbar(self.progress_frame, 
                                      orient="horizontal", 
                                      length=400, 
                                      mode="indeterminate",
                                      style="Horizontal.TProgressbar")
        
        # Update status
        self.update_status(f"{module_title} module ready", "normal")
    
    def launch_module_script(self, script_path, module_name):
        """Launch the specified Python script as a subprocess"""
        if self.process_running:
            messagebox.showinfo("Module Running", 
                              "This module is already running.")
            return
        
        # Check if script exists
        if not os.path.exists(script_path):
            error_msg = f"Module script not found: {script_path}"
            messagebox.showerror("Error", error_msg)
            self.update_status(error_msg, "error")
            return
        
        # Set running flag
        self.process_running = True
        
        # Show progress bar
        self.progress_frame.pack(anchor=tk.W, pady=20)
        self.progress.pack(fill=tk.X)
        self.progress.start(10)
        
        # Update status
        self.status_message.config(text=f"Running {module_name}...")
        self.update_status(f"Launched {module_name} module", "success")
        
        # Run script in a separate thread to avoid freezing the GUI
        threading.Thread(target=self.run_script, 
                       args=(script_path, module_name)).start()
    
    def run_script(self, script_path, module_name):
        """Run the script in a separate process"""
        try:
            # Get the python executable path
            python_exe = sys.executable
            
            # Launch the script
            self.current_process = subprocess.Popen(
                [python_exe, script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            # Wait for completion
            stdout, stderr = self.current_process.communicate()
            
            # Check if successful
            if self.current_process.returncode == 0:
                self.root.after(0, lambda: self.on_script_complete(module_name, True))
            else:
                error_msg = f"Error in {module_name}: {stderr}"
                self.root.after(0, lambda: self.on_script_complete(module_name, False, error_msg))
        
        except Exception as e:
            error_msg = f"Failed to run {module_name}: {str(e)}"
            self.root.after(0, lambda: self.on_script_complete(module_name, False, error_msg))
    
    def on_script_complete(self, module_name, success, error_msg=None):
        """Handle script completion"""
        # Stop progress bar
        self.progress.stop()
        self.progress_frame.pack_forget()
        
        # Update status
        if success:
            self.status_message.config(text=f"{module_name} completed successfully")
            self.update_status(f"{module_name} completed", "success")
            messagebox.showinfo("Complete", f"{module_name} analysis completed successfully.")
        else:
            self.status_message.config(text=error_msg)
            self.update_status(f"{module_name} failed", "error")
            messagebox.showerror("Error", error_msg)
        
        # Reset running flag
        self.process_running = False
        self.current_process = None

def main():
    root = tk.Tk()
    app = ModernSuicideRiskDetectionSystem(root)
    
    # Set window icon if available
    try:
        icon_path = os.path.join(os.path.dirname(__file__), "icon.ico")
        if os.path.exists(icon_path):
            root.iconbitmap(icon_path)
    except:
        pass  # Icon not critical, continue without it
    
    # Center window on screen
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'+{x}+{y}')
    
    root.mainloop()

if __name__ == "__main__":
    main()