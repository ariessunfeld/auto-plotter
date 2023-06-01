# What is Auto Plotter?

Auto Plotter is designed to make data visualization as easy as possible. You can give it CSV, TSV, XLSX, JSON, or other data products, simply by copying the file(s) into the auto-plotter folder, and then describe what kind of plot(s) you want made from your data. It does the rest. 

## Details

Auto Plotter uses GPT 4 to write python code to generate the kind of plot(s) you described, using the provided file(s) as directed. It then uses GPT 3.5 to add error handling to the code it wrote and to analyze it for safety. After this process, you have the option to view and/or run the code it produced to generate the kinds of visualizations you requested.

# Usage

To launch Auto-Plotter, simply run `python3 auto-plotter.py` in the terminal or command prompt. Assuming the installation and setup process went smoothly, a GUI (graphical user interface) should open. In the text window at the very bottom of the GUI, you can type your request to Auto Plotter, and when you're ready, click send. If you reference files on your computer in your request, make sure that they are The status of the process will be displayed in the terminal or command prompt while Auto Plotter thinks about your message and then writes and validates code in response to your message.

## Example Usage

Some example requests are listed below. For each of these requests, Auto Plotter will assume that the files mentioned by name in the request are present in the auto-plotter directory, and that any column names / keys listed in the request are present in the corresponding files.
* "I have a file called data.csv with columns for SiO2, FeOT, and MnO, and a column called Category. I want a scatterplot of SiO2 on the y axis and FeOT on the x axis with a continuous MnO heatmap, just for the data in category A."
* I have a file called data.csv and another file called categories.csv. The data.csv file has a Target column and chemistry columns. The categories.csv has a Target column and a Category column. I want a single heatmap showing the pearson's r correlation coefficients between MnO and the following oxides [SiO2, FeOT, MgO] across all the categories. The categories should appear on the horizontal axis of the heatmap, and the three oxides along the vertical axis.

# Setup

Auto Plotter requires that you have Python and Pip installed on your computer, and that you have an OpenAI API key. The API key is free to obtain, but a payment method is required, as you will be charged a tiny amount (one or two cents) for typical usage.

## Installing Python

If you don't have it already, download and install python from https://www.python.org/downloads/. There should be a yellow Download button for the latest version. When installing, make sure to add python to PATH if prompted.

## Installing Pip

Open the terminal or command prompt, execute `curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py`, then execute `python3 get-pip.py` and follow the installation prompts. Pip should now be installed on your system.

## Getting an OpenAI API Key

If you don't have an OpenAI API key already, go to platform.openai.com/account/api-keys. If you don't have an OpenAI account yet, you will have to sign up with your email. Then follow the instructions to add a payment method. You can set a usage limit so that no more than $X is charged to your card each month. For typical usage of Auto Plotter, a usage limit of $5 should be more than enough.

## Cloning the Repository

If you have Git installed on your computer, copy the cloning link for this repository, then open the terminal or command prompt and run `git clone link-goes-here`. If you prefer to simply download the code as a zip file, you can do that, too.

## Setting up the Environment (.env)

Open the Finder or File Browser and unzip the code directory (folder) (if you didn't clone the repository with Git). Open a new terminal or command prompt and navigate into the auto-plotter directory. (To navigate in the terminal or command promot, use `cd`.)Then execute `ls` on Mac, or `dir` on Windows to ensure that you have these files: `requirements.txt`, `template.env`, and `auto-plotter.py`. Open `template.env` and replace the text `your-api-key-goes-here` with your full API key from OpenAI. Then rename `template.env` to `.env`. You can do this in the terminal or command prompt by executing the following command: `mv template.env .env`. 

## Installing Dependencies

### Creating a Virtual Environment

It's recommended to install dependencies in a virtual environment to avoid conflicts with other packages you might have installed. To do this, navigate into the auto-plotter directory on the terminal or command prompt, then run `python3 -m venv venv`. This will create a folder called `venv`. To activate the new virtual environment you just created, run `source venv/bin/activate` (on macOS) or `.\venv\Scripts\activate` (on Windows). 

Now run `pip install -r requirements.txt`. You will need to be connected to the internet for this step to work. This will install the 3rd-party python libraries necessary for auto-plotter to work, but instead of installing them in your base environment, they will be installed in the virtual environment.