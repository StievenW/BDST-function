# BDST-function (Bedrock Dedicated Server Tools)

BDST-function is a Python-based tool designed to help you manage and automate tasks on your Minecraft Bedrock Dedicated Server using RCON. The tool allows you to monitor a folder for `.mcfunction` files, execute the commands within those files on your server, and adjust the command delay between executions using a simple graphical user interface (GUI).

## Features

- **Automatic Command Execution**: Automatically scans a specified folder for `.mcfunction` files and executes the commands within on your Bedrock server.
- **Customizable Command Delay**: Adjust the delay between command executions using an intuitive slider in the GUI, with a range from 0.06 to 0.1 seconds.
- **Real-time Log**: View command execution logs directly in the GUI to monitor what commands are being sent to the server.
- **Simple Setup**: Easy-to-use interface with start and stop controls for managing the execution process.

## Requirements

- Python 3.x
- `tkinter` library (usually included with Python)
- A running Minecraft Bedrock Dedicated Server with RCON enabled

## Installation

1. **Clone the repository**:
    ```bash
    git clone https://github.com/StievenW/BDST-function.git
    cd BDST-function
    ```

2. **Edit the RCON configuration**:
    - Open the `config.py` file and modify the following variables according to your server's configuration:
        ```python
        HOST = '127.0.0.1'  # Change to your server's IP
        PORT = 25575        # Change to your server's RCON port
        PASSWORD = 'yourpassword'  # Change to your server's RCON password
        ```

3. **Set up the functions folder**:
    - Make sure you have a folder named `functions` (or change the path in the code) where your `.mcfunction` files are stored.

## Usage

1. **Run the tool**:
    ```bash
    python function.py
    ```

2. **GUI Overview**:
    - **File List Box**: Displays all `.mcfunction` files found in the specified folder.
    - **Log Box**: Shows real-time logs of the commands executed on the server.
    - **Command Delay Slider**: Allows you to adjust the delay between command executions.
    - **Start Button**: Begins monitoring the folder and executing commands.
    - **Stop Button**: Stops the execution of commands.

3. **Customizing Command Delay**:
    - Use the command delay slider in the GUI to set the desired delay between command executions. The delay can be set between 0.06 and 0.1 seconds.

## Contributing

Contributions are welcome! Please submit a pull request or open an issue to discuss your ideas.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
