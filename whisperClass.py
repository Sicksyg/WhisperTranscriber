import whisper
import torch
import json
import gc
import logging
from docx import Document
from docx.shared import Cm
from datetime import timedelta
from pathlib import Path

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

MAIN_DIR = Path.cwd()
ASSETS_DIR = Path(MAIN_DIR, "WT_assets")

class Trans():
    def __init__(self, filepath, modelsize, device, batch, *args):
        # self.setup = self.setup()
        self.filePath = Path(filepath)
        self.fileName = Path(filepath).stem
        self.modelsize = modelsize
        self.device = device
        self.batch = batch

        logging.info(f"{self.filePath}   /-/    {self.modelsize}    /-/    {self.device}")

        self.json = True
        self.ts = True
        self.docx = True

        # Loads model at init
        self.model = self.loadModel()
        self.transcribe = self.transcribeAudio()

    def loadModel(self):
        if self.modelsize == "large" and "cuda" in self.device:  # change device from GPU
            tmem = torch.cuda.get_device_properties(0).total_memory / 1024**2
            if tmem < 10000:
                logging.warning(
                    f"Not enough vram at GPU to load the large model. GPU vram: {tmem} MB. Need 10000 MB ´(10GB) to run.")
                self.modelsize = "medium"
        if self.modelsize == "large":
            self.modelsize = "large-v3"

        # download_root="./assets/models"
        model = whisper.load_model(name=self.modelsize, download_root=Path(ASSETS_DIR, "models"))
        return model

    def transcribeAudio(self):  # Only for non batch
        if self.batch == True:
            for file in Path.iterdir(self.filePath):
                self.pr_file_dir = Path(self.filePath, file.stem)
                try:
                    logging.info(f"Making a dir at {self.pr_file_dir}")
                    Path.mkdir(self.pr_file_dir, exist_ok=False)
                except FileExistsError:
                    pass
                self.cur_batchfile = file
                self.results = self.model.transcribe(
                    str(self.cur_batchfile), verbose=False)
                self.fileprinter = self.file_printer()
        else:
            self.results = self.model.transcribe(
                str(self.filePath), verbose=False)
            self.fileprinter = self.file_printer()

        # Memory clearing
        torch.cuda.empty_cache()
        gc.collect()

    def file_printer(self):
        # Changing the suffix of files but keeping the name using Pathlib
        if self.batch == True:
            logging.info(f"BATCH TRANS - THE FILE IS {self.pr_file_dir}")

            output_txt = self.cur_batchfile.stem + ".txt"
            output_json = self.cur_batchfile.stem + ".json"
            output_ts = self.cur_batchfile.stem + "_TIMESTAMP.txt"
            output_docx = self.cur_batchfile.stem + ".docx"

            outputdir = self.pr_file_dir
            print(f"{outputdir}     {output_json}")

        else:
            logging.info(f"NOT BATCH - THE FILE IS {self.filePath}")

            output_txt = self.fileName + ".txt"
            output_json = self.fileName + ".json"
            output_ts = self.fileName + "_TIMESTAMP.txt"
            output_docx = self.fileName + ".docx"

            outputdir = self.filePath.parent

        if self.json:  # If -json == True
            # Writes json file
            jsonpath = outputdir / output_json
            with open(jsonpath, "x", encoding="utf-8") as fp:
                json.dump(self.results["segments"], fp, indent=4)

            # Writes txt file
            txtpath = outputdir / output_txt
            with open(txtpath, "w", encoding="utf-8") as fp:
                fp.write(self.results["text"])

        if self.ts:
            tspath = outputdir / output_ts
            res_detailed = self.results["segments"]
            with open(tspath, "w", encoding="utf-8") as tsfile:
                for res in res_detailed:
                    start = timedelta(seconds=res["start"])
                    end = res["end"]
                    txt = res["text"]
                    print(f'{start}{txt}')
                    # Ensures the format
                    tsfile.writelines(f'{str(start)[0:7]}{txt} \n')
        if self.docx:
            docxpath = outputdir / output_docx
            x = 1
            textseg = "[0:00:00]\n"
            outtext = []
            for y, i in enumerate(self.results["segments"], start=1):
                startSeg = i["start"]
                txt = i["text"].lower()
                # concats the current text segment of "i" to the last segment "i-n"
                textseg += txt
                # The logic for calc the time passed. Takes the start of the i[text] and subtract the 300*x for every 5 minutes.
                if (startSeg - (300 * x)) >= 0:
                    x += 1  # counter
                    textseg += "\n" + \
                        str([str(timedelta(seconds=startSeg))[0:7]])
                    outtext.append(textseg)
                    textseg = ""
                # Append the last line after the last timestamp. Checks if the json dict is at its end
                if y == len(self.results["segments"]):
                    outtext.append(textseg)

            # Document creator
            doc = Document()
            sections = doc.sections
            for section in sections:
                section.top_margin = Cm(3)
                section.bottom_margin = Cm(3)
                section.left_margin = Cm(2)
                section.right_margin = Cm(2)
            for seg in outtext:
                doc.add_paragraph(seg)
            doc.save(docxpath)

        else:  # Only save a txt file
            # Writes txt file
            txtpath = outputdir / output_txt
            with open(txtpath, "w", encoding="utf-8") as fp:
                fp.write(self.results["text"])

class Downloading():
    def __init__(self):
        self.models = ["tiny", "base", "small", "medium", "large-v3"]

    def _downloadModels(self):
        for model in self.models:
            whisper._download(whisper._MODELS[model], Path(ASSETS_DIR, "models"), False)

# download = Downloading()
# download._downloadModels()
