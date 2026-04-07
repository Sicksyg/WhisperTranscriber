# GUI imports
import tkinter
import tkinter.messagebox
import customtkinter

# Helper imports
import torch
import json
from pathlib import Path
import logging

# Whisper script
import whisperClass

#setup logging: #does not work in console
logging.basicConfig(format='%(levelname)4s - %(asctime)-8s - %(message)s', datefmt='%m-%d %H:%M', level=logging.INFO)

# Paths:
MAIN_DIR = Path.cwd()
ASSETS_DIR = Path(MAIN_DIR, "WT_assets")
DRIVE_DIR = Path.home()

class Variables():
    with open(Path(ASSETS_DIR, "settings.json"), "r") as fp:
        setting = json.load(fp)
    
    modelsize = setting["modelsize"]
    devicetype = setting["device"]
    batchtrans = False
    filepath = MAIN_DIR
    filename = filepath.name
    devicetype_display = devicetype
    if torch.cuda.is_available():
        if devicetype[0:3] == "cuda":
            devicetype_display = "GPU: %s" % (torch.cuda.get_device_name(devicetype))
        else:
            devicetype_display = "CPU"
    #cursettings_txt = tkinter.StringVar(value=f"Model size: {modelsize}\nDevice: {devicetype}\nBatch transcription:{batchtrans}")
    #cursettings_txt = f"Model size: {modelsize}\nDevice: {devicetype}\nBatch transcription:{batchtrans}"
    
class Setup(customtkinter.CTkFrame, Variables):
    def __init__(self, master):
        super().__init__(master)
        
        self.grid_columnconfigure(0, weight=0)  # column 0
        self.grid_rowconfigure(0, weight=0) # title
        self.grid_rowconfigure(1, weight=1) # Advanced settings
        self.grid_rowconfigure(2, weight=1) # Current settings_title
        self.grid_rowconfigure(3, weight=1) # Current settings
        self.grid_rowconfigure(4, weight=1) # Excution
        self.grid_rowconfigure(5, weight=1) # Status
        
        px = 10
        py = (10,10)

        # title:   
        self.title = customtkinter.CTkLabel(master= self, text="SETTINGS", fg_color="transparent", font=("SF Display", 16, "bold"))
        self.title.grid(row=0, column=0, padx=px, pady=py, sticky="new")
        
        # Open advanced settings:
        self.openadvance = customtkinter.CTkButton(master=self, text="Advanced Settings", command=self.openAdvance)
        self.openadvance.grid(row=1, column=0, padx=px, pady=py, sticky="new")
        
        # Current settings:
        self.cursettings_title = customtkinter.CTkLabel(master= self, text="Current Settings", fg_color="transparent", font=("SF Display", 14, "bold"))
        self.cursettings_title.grid(row=2, column=0, padx=px, pady=py, sticky="sew")
        
        # To update the text when settings is saved, a global variable is set at the "Main()" class, as the event loop updates (Not great, not terrible)
        global cursettings_txt
        self.cursettings_label = customtkinter.CTkLabel(master= self, textvariable=cursettings_txt, fg_color="transparent")
        self.cursettings_label.grid(row=3, column=0, padx=px, pady=py, sticky="sew")

        # Execute transscription button:
        self.execute = customtkinter.CTkButton(master=self, text="Run Transcription", command=self.startTrans)
        self.execute.grid(row=4, column=0, padx=px, pady=py, sticky="sew")

        # Status of the execution:
        self.status = customtkinter.CTkTextbox(master=self, height=120, wrap=None)
        self.status.grid(row=5, column=0, padx=px, pady=py, sticky="sew")
        
    # Control toplevel is not open (openAdvanced())
        self.toplevel_window = None
        
    def openAdvance(self):
        if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
            self.toplevel_window = AdvancedSettings(self)
        else:
            self.toplevel_window.focus()
    
    def startTrans(self):
        self.statusPrint()
        modelsize = Variables.modelsize
        batchtrans = Variables.batchtrans
        if Variables.devicetype == "CPU":
            devicetype = "cpu"
        else:
            devicetype = Variables.devicetype

        if Variables.filepath != MAIN_DIR:
            if batchtrans == False:
                #logging.info("file")
                whisperClass.Trans(filepath=Variables.filepath, modelsize=modelsize, device=devicetype, batch= batchtrans)
            else:
                #logging.info("Batch")
                whisperClass.Trans(filepath=Variables.filepath, modelsize=modelsize, device=devicetype, batch= batchtrans)
        else:
            logging.warning("No file was chosen. Choose a file via the file loader.")
            if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
                self.toplevel_window = FileLoadError(self)
            else:
                self.toplevel_window.focus()
        
    def statusPrint(self):
        self.status.insert(index="0.0", text=f"Running transcription on:  {Variables.filename}\n")
        self.status.configure(state="disabled")

class ModelInfo(customtkinter.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.geometry("360x300")

        self.grid_columnconfigure(0, weight=1)  # column 0        self.label.pack(padx=20, pady=20)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        
        self.label = customtkinter.CTkLabel(master=self, text="Model Info", font=("SF Display", 16, "bold"))
        self.label.grid(row=0, column=0, sticky="new")
        
        self.textbox = customtkinter.CTkTextbox(master=self, corner_radius=0, width=350, height=370, wrap=None)
        #self.textbox.configure(state="disabled")
        self.textbox.grid(row=1, column=0, sticky="ns")
        self.textbox.insert(index="0.0", text=self.modeltext())
        
    def modeltext(self):
        with open(Path(ASSETS_DIR, "modelinfo.txt"), "r") as t:
            text = t.read()
        return text

class AdvancedSettings(customtkinter.CTkToplevel, Variables):
    def __init__(self, master):
        super().__init__(master)
        width = 400
        height = 300
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width/2) - (width/2)
        y = (screen_height/2) - (height/2)

        self.geometry('%dx%d+%d+%d' % (width, height, x, y))
        self.grab_set()
        #self.geometry("400x300")
        
        self.grid_columnconfigure(0, weight=1) # column 0
        self.grid_columnconfigure(1, weight=1) # column 1

        self.grid_rowconfigure(0, weight=1) #title
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)
        self.grid_rowconfigure(4, weight=1)
        self.grid_rowconfigure(5, weight=1)
    
        self.title = customtkinter.CTkLabel(master= self, text="ADVANCED SETTINGS", fg_color="transparent", font=("SF Display", 16, "bold"))
        self.title.grid(row=0, column=0, columnspan=2 ,sticky="n")
        
        # ----------------------- Model and device select (col 0) -----------------------
        # Model info
        self.modelinfo = customtkinter.CTkButton(master=self, text="Model/Device Info", command=self.openInfo)
        self.modelinfo.grid(row=1, column=0, sticky="n")
        
        #modelchoice
        modelsizes = ["tiny", "base", "small", "medium", "large"]
        self.modelchoice = customtkinter.CTkComboBox(master=self, values=modelsizes)
        self.modelchoice.set("Model Size")
        self.modelchoice.grid(row=2, column=0, sticky="n")
        
        #Device choice
        #cudaNum = ["cuda:" + str(i) for i in range(torch.cuda.device_count())]
        #gpuName = [name + " - " + torch.cuda.get_device_name(name) for name in cudaNum]

        devicetypes = ["CPU"] + ["cuda:" + str(i) for i in range(torch.cuda.device_count())]
        logging.info(f" The available devices on this system: {devicetypes}")
        self.devicechoice = customtkinter.CTkComboBox(master=self, values=devicetypes)
        self.devicechoice.set("Device")
        self.devicechoice.grid(row=3, column=0, sticky="n")

        # ----------------------- Format selection (col 1) ------------------------------
        px = 20
        py = (2,2)
        # Json flip
        self.json_var = customtkinter.BooleanVar(value=True)
        self.json = customtkinter.CTkCheckBox(
            master=self, text="JSON", variable=self.json_var, state=tkinter.DISABLED)
        self.json.grid(row=1, column=1, padx=px, pady=py, sticky="new")
        
        # Txt flip
        self.txt_var = customtkinter.BooleanVar(value=True)
        self.txt = customtkinter.CTkCheckBox(
            master=self, text="TXT", variable=self.txt_var, state=tkinter.DISABLED)
        self.txt.grid(row=2, column=1, padx=px, pady=py, sticky="new")
        
        # Timestamp flip
        self.ts_var = customtkinter.BooleanVar(value=True)
        self.ts = customtkinter.CTkCheckBox(
            master=self, text="TimeStamped", variable=self.ts_var, state=tkinter.DISABLED)
        self.ts.grid(row=3, column=1, padx=px, pady=py, sticky="new")
        
        # docs flip
        self.docs_var = customtkinter.BooleanVar(value=True)
        self.docs = customtkinter.CTkCheckBox(
            master=self, text="Word - 5 min", variable=self.docs_var, state=tkinter.DISABLED)
        self.docs.grid(row=4, column=1, padx=px, pady=py, sticky="new")
        
        # Errors
        self.toplevel_window = None
        
        # ----------------------- Save/close button (col 1+2) ------------------------------
        
        self.modelinfo = customtkinter.CTkButton(master=self, text="SAVE", command=self.saveSettings)
        self.modelinfo.grid(row=5, column=0, columnspan=2, sticky="sew")
        
        
    def saveSettings(self):
        Variables.modelsize = self.modelchoice.get()
        Variables.devicetype = self.devicechoice.get()
        self.destroy()
        global cursettings_txt
        cursettings_txt.set(f"Model size: {Variables.modelsize}\nDevice: {Variables.devicetype_display}\nBatch transcription:{Variables.batchtrans}")
        logging.info(f" Settings saved with:  Device: {Variables.devicetype} // Model: {Variables.modelsize}")

    def openInfo(self):
        if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
            self.toplevel_window = ModelInfo(self)
        else:
            self.toplevel_window.focus()

class FileLoadError(customtkinter.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.geometry("400x300")

        self.label = customtkinter.CTkLabel(master=self, text="FileLoadError: You need to choose a file or folder.")
        self.label.pack(padx=20, pady=20)
        
class FileFrame(customtkinter.CTkFrame, Variables):
    def __init__(self, master):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)  # column 0
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)

        px = 10
        py = (10,10)
        
        self.title = customtkinter.CTkLabel(master= self, text="LOAD FILE", fg_color="transparent", font=("SF Display", 16, "bold"))
        self.title.grid(row=0, column=0, sticky="n")

        # Open file button
        self.openfile = customtkinter.CTkButton(
            master=self, text="Open File", command=self.openFileButton)
        self.openfile.grid(row=1, column=0, padx=px, pady=py, sticky="new")

        # Open dir for batch
        self.openfolder = customtkinter.CTkButton(
            master=self, text="Open Folder", command=self.openFolderButton)
        self.openfolder.grid(row=2, column=0, padx=px, pady=py, sticky="ew")

        # List open files
        self.listfile = customtkinter.CTkTextbox(
            master=self, height=290)
        self.listfile.grid(row=3, column=0, padx=px, pady=py, sticky="ew")

    # Input the file/dir in the textbox
    def insertListfile(self):
        self.listfile.insert(index="0.0", text=Variables.filepath)
        self.listfile.configure(state="disabled")

    # File open func
    def openFileButton(self):
        self.listfile.delete("0.0", "end")
        path = tkinter.filedialog.askopenfilename(initialdir=DRIVE_DIR)
        Variables.filepath = Path(path)
        global cursettings_txt
        cursettings_txt.set(f"Model size: {Variables.modelsize}\nDevice: {Variables.devicetype_display}\nBatch transcription:{Variables.batchtrans}")
        self.insertListfile()
        
    def openFolderButton(self):
        self.listfile.delete("0.0", "end")
        #Variables.filepath = ""
        Variables.batchtrans = True
        Variables.filepath = tkinter.filedialog.askdirectory(initialdir=DRIVE_DIR)
        global cursettings_txt
        cursettings_txt.set(f"Model size: {Variables.modelsize}\nDevice: {Variables.devicetype_display}\nBatch transcription:{Variables.batchtrans}")
        self.insertListfile()

class Guide(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)  # column 0
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        
        px = 10
        py = (10,10)

        self.title = customtkinter.CTkLabel(master= self, text="GUIDE", fg_color="transparent", font=("SF Display", 16, "bold"))
        self.title.grid(row=0, column=0, sticky="n")

        self.textbox = customtkinter.CTkTextbox(master=self, wrap="word")
        self.textbox.grid(row=1, column=0, rowspan=2, padx=px, pady=py, sticky="nsew")
        self.textbox.insert(index="0.0", text=self.guidetext())
        self.textbox.configure(state="disabled")
        
    def guidetext(self):
        with open(Path(ASSETS_DIR,"guidetext.txt"), "r") as t:
            text = t.read()
        return text
    
""" class Status(customtkinter.CTkFrame, Variables):
    def __init__(self, master):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)  # column 0
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self.fileTitle = customtkinter.CTkLabel(master= self, text=Variables.filepath, fg_color="transparent")
        self.fileTitle.grid(row=0, column=0, sticky="new")

        self.status = customtkinter.CTkProgressBar(master=self)  """   

class App(customtkinter.CTk, Variables):
    def __init__(self):
        super().__init__()
        # Main setup of window
        global cursettings_txt
        cursettings_txt = tkinter.StringVar(value=f"Model size: {Variables.modelsize}\nDevice: {Variables.devicetype_display}\nBatch transcription: {Variables.batchtrans}")
        # Modes: "System" (standard), "Dark", "Light"
        customtkinter.set_appearance_mode("System")
        # Themes: "blue" (standard), "green", "dark-blue"
        #customtkinter.set_default_color_theme("green") 
        customtkinter.set_default_color_theme(Path(ASSETS_DIR, "UCPH_theme.json"))
        #my_font = customtkinter.CTkFont(family="<family name>", size=<size in px>, <optional keyword arguments>)

        width = 900
        height = 460
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width/2) - (width)
        y = (screen_height/2) - (height)

        self.geometry('%dx%d+%d+%d' % (width, height, x, y))
        #self.eval('tk::PlaceWindow . center')
        self.title("Whisper Transcriber")
        self.iconbitmap(Path(ASSETS_DIR, "App_icon.ico"))

        # Define Grid
        self.grid_columnconfigure(0, weight=0)  # column 0
        self.grid_columnconfigure(1, weight=1)  # column 1
        self.grid_columnconfigure(2, weight=1)  # column 2
        self.grid_columnconfigure(3, weight=0)  # column 2
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # File loading
        self.fileframe = FileFrame(self)
        self.fileframe.grid(row=0, column=0, rowspan=2, padx=5, pady=5, sticky="nsew")
        
        # Guide
        self.guideframe = Guide(self)
        self.guideframe.grid(row=0, column=1, columnspan= 2, rowspan=2, padx=5, pady=5, sticky="nsew")

        # Settings
        self.setup = Setup(self)
        self.setup.grid(row=0, rowspan=2, column=3, padx=5, pady=5, sticky="nsew")
        
        # status
        #self.status = Status(self)
        #self.status.grid(row=1, column=0, columnspan=4, padx=5, pady=5, sticky="sew")
    
        #print(f"Device: {Variables.devicetype} // Model: {Variables.modelsize}")

# Run loop
if __name__ == "__main__":
    app = App()
    app.mainloop()
