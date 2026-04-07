# Whisper 2.0 Code

## Overview
This repository contains the code for WhisperTranscriber. A small GUI program build upon the original Whisper project, providing improved accuracy and features for transcription and translation tasks.

## Features
- High-accuracy speech-to-text transcription
- Multi-language support
- Real-time processing capabilities
- Easy integration with Python applications

## Build
1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/Whisper2.0_code.git
    ```
2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
    ## Packaging with auto-py-to-exe
    To build a standalone executable locally:

    1. Install auto-py-to-exe:
        ```bash
        pip install auto-py-to-exe
        ```

    2. Run auto-py-to-exe and load the configuration:
        - Launch the GUI: `auto-py-to-exe`
        - Load the `auto-py-to-exe_settings.json` file
        - Click "Convert .py to .exe"

    3. Find the packaged application in:
        ```bash
        dist/
        ```

    ### Notes
    - The settings file includes special handling for tkinter and customtkinter, as they need to be bundled properly for the GUI to work.
    - The entry point is `WhisperTranscriber.py`.
    - Additional assets like WT_assets, customtkinter, whisper assets, and settings.json are included via the configuration.


## Contributing
Contributions are welcome! Please fork the repository and submit a pull request.

## License
This project is licensed under the MIT License.