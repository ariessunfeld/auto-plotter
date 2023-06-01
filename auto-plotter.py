import os
import openai
import tkinter as tk
from tkinter import ttk
import atexit
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

DATA_VIZ_SYSTEM_DESCRIPTION = "You are a helpful data visualization assistant. I am going to describe what kind of visualizations I want, and you will respond with exactly the python code necessary to generate these visualizations, and no other output. You can assume I have matplotlib, numpy, pandas, plotly, and seaborn installed. All plots should be made with high resolution, labeled clearly, and saved to disk. Your output will be put directly into a python file to be executed, so do not include any unecessary commentary."
ERROR_HANDLING_SYSTEM_DESCRIPTION = 'You specialize in adding error handling to python code. The code you will receive is going to be called as a string inside an `exec` function in a larger python script. Your job is to add error handling to each file-read or file-write line. Error handling should raise Exceptions with informative messages if files cannot be read, if columns do not exist in dataframes, or anything similar. For example, if a FileNotFoundError is going to be raised, then raise a FileNotFoundError with an informative message, including the name of the file not found. If files are being written, error handling should ensure that no file with the same name already exists, and if it does, should prompt the user for confirmation before overwriting. You should add this error handling to the python code you receive, and respond with the updated code, but nothing else: no commentary.'
CODE_SAFETY_SYSTEM_DESCRIPTION = 'You are a code safety analyst. You analyze python code and ensure that nothing harmful or unusual will take place if the code is executed. You expect the code to be a data visualization script, usually a combination of reading spreadsheets and creating and saving plots. If you deem the code safe to run, you will respond with "All clear" and nothing else. Otherwise, if you see anything suspicious or concerning, you will respond with "Dangerous. Do not proceed" and nothing else.'


def check_file_exists():
    if not os.path.exists('error-handling-output.py'):
        view_button['state'] = 'disabled'
        execute_button['state'] = 'disabled'
    else:
        view_button['state'] = 'normal'
        execute_button['state'] = 'normal'

def process_openai_response(response):
    assistant_response = response.choices[0].message["content"]
    assistant_lines = assistant_response.split('\n')

    if assistant_lines[0].strip() == "```python" and assistant_lines[-2].strip() == "```":
        assistant_response = '\n'.join(assistant_lines[1:-2])

    return assistant_response

def write_file(filename, content):
    with open(filename, 'w') as file:
        file.write(content)

def delete_files(*filenames):
    for filename in filenames:
        try:
            os.remove(filename)
        except FileNotFoundError as err:
            print(err)

def send_message():
    message = user_input.get()
    conversation.insert(tk.END, "You: " + message + "\n")
    user_input.delete(0, tk.END)

    print('Thinking...')

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": DATA_VIZ_SYSTEM_DESCRIPTION},
            *previous_messages,
            {"role": "user", "content": message},
        ]
    )
    
    assistant_response = process_openai_response(response)
    write_file('output.py', assistant_response)
    print('Done thinking. Preliminary code written to output.py.')

    conversation.insert(tk.END, "Data Viz Assistant:\n", "bold")
    conversation.insert(tk.END, assistant_response + "\n")

    root.update_idletasks()
    print('Adding error handling to code...')

    error_handling_response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=[
            {"role": 'system', "content": ERROR_HANDLING_SYSTEM_DESCRIPTION},
            {"role": 'user', "content": assistant_response}
        ]
    )

    error_handling_response = process_openai_response(error_handling_response)
    write_file('error-handling-output.py', error_handling_response)
    print('Done adding error handling. Finished code written to error-handling-output.py.')

    conversation.insert(tk.END, "\n\nError Handling Assistant:\n", "bold")
    conversation.insert(tk.END, error_handling_response + "\n")

    root.update_idletasks()
    print('Analyzing code safety...')

    safety_response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=[
            {"role": 'system', "content": CODE_SAFETY_SYSTEM_DESCRIPTION},
            {"role": 'user', "content": error_handling_response}
        ]
    )

    safety_response = safety_response.choices[0].message["content"]
    conversation.insert(tk.END, "\n\nCode Safety Assistant: ", "bold")
    conversation.insert(tk.END, safety_response + "\n")

    if safety_response.startswith('Dangerous'):
        print('WARNING: Code deemed dangerous. Removing python files from disk.')
        delete_files('output.py', 'error-handling-output.py')

    previous_messages.extend([
        {"role": "user", "content": message},
        {"role": "assistant", "content": assistant_response},
    ])

    check_file_exists()

def view_output():
    with open('error-handling-output.py', 'r') as file:
        content = file.read()
    conversation.insert(tk.END, "error-handling-output.py content:\n", "bold")
    conversation.insert(tk.END, content + "\n")

def execute_output():
    #output = subprocess.check_output(['python3', 'error-handling-output.py']).decode('utf-8')
    #conversation.insert(tk.END, "Execution result:\n", "bold")
    #conversation.insert(tk.END, output + "\n")
    with open("error-handling-output.py", "r") as f:
        script_code = f.read()
    try:
        exec(script_code)
    except Exception as err:
        print('Halting process due to error: ', err)
        conversation.insert(tk.END, "Halting process due to error: \n", "bold")
        conversation.insert(tk.END, str(err) + "\n")

def save_chat_history():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"chat_history_{timestamp}.txt"
    with open(filename, 'w') as file:
        try:
            file.write(conversation.get("1.0", tk.END))
            print('Chat history saved to', filename)
        finally:
            pass

def exit_program():
    save_chat_history()
    root.destroy()

if __name__ == '__main__':

    atexit.register(save_chat_history)

    print('Booting up...')

    root = tk.Tk()
    root.title("Auto Plotter")

    frame = ttk.Frame(root, padding="10")
    frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    conversation = tk.Text(frame, wrap=tk.WORD, width=75, height=20, font=("TkDefaultFont", 12))
    conversation.tag_configure("bold", font=("TkDefaultFont", 12, "bold"))
    conversation.grid(row=0, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S))

    user_input = ttk.Entry(frame, width=70, font=("TkDefaultFont", 12))
    user_input.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    send_button = ttk.Button(frame, text="Send", command=send_message)
    send_button.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))

    view_button = ttk.Button(frame, text="View Code", command=view_output, state='disabled')
    view_button.grid(row=1, column=2, sticky=(tk.W, tk.E, tk.N, tk.S))

    execute_button = ttk.Button(frame, text="Execute Code", command=execute_output, state='disabled')
    execute_button.grid(row=1, column=3, sticky=(tk.W, tk.E, tk.N, tk.S))

    check_file_exists()

    previous_messages = []

    root.protocol("WM_DELETE_WINDOW", exit_program)

    root.mainloop()
