import os
import time
import openai
import tkinter as tk
from tkinter import ttk
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

def read_file_contents(filename):
    """
    Read the content of a file and return it as a string.
    :param filename: The name of the file to read.
    :return: The content of the file.
    """
    with open(filename, 'r') as file:
        content = file.read().strip()  # strip() removes any leading/trailing whitespace including newline chars
    return content

# define the file paths
AGENTS_DIR = 'agents'
DATA_VIZ_SYSTEM_DESCRIPTION_FILE = os.path.join(AGENTS_DIR, 'data_viz_agent.txt')
ERROR_HANDLING_SYSTEM_DESCRIPTION_FILE =  os.path.join(AGENTS_DIR, 'error_handling_agent.txt')
CODE_SAFETY_SYSTEM_DESCRIPTION_FILE =  os.path.join(AGENTS_DIR, 'code_safety_agent.txt')

# read the descriptions from the files
DATA_VIZ_SYSTEM_DESCRIPTION = read_file_contents(DATA_VIZ_SYSTEM_DESCRIPTION_FILE)
ERROR_HANDLING_SYSTEM_DESCRIPTION = read_file_contents(ERROR_HANDLING_SYSTEM_DESCRIPTION_FILE)
CODE_SAFETY_SYSTEM_DESCRIPTION = read_file_contents(CODE_SAFETY_SYSTEM_DESCRIPTION_FILE)

DATA_VIZ_MODEL = 'gpt-4'
ERROR_HANDLING_MODEL = 'gpt-3.5-turbo'
CODE_SAFETY_MODEL = 'gpt-3.5-turbo'

VERBOSE = False
MAX_RETRIES = 3

def check_file_exists():
    """
    Check if 'error-handling-output.py' exists and change the state of the 'View Code' and 'Execute Code' buttons accordingly.
    """
    if not os.path.exists('error-handling-output.py'):
        view_button['state'] = 'disabled'
        execute_button['state'] = 'disabled'
    else:
        view_button['state'] = 'normal'
        execute_button['state'] = 'normal'

def process_openai_response(response):
    """
    Process the OpenAI response and return the assistant's response as a string.
    :param response: The response from OpenAI API.
    :return: The content from the assistant's response.
    """
    assistant_response = response.choices[0].message["content"]
    assistant_lines = assistant_response.split('\n')

    # Strip any leading preamble before import statements
    idx = 0
    for i, line in enumerate(assistant_lines):
        if line.startswith('import ') or line.startswith('from '):
            idx = i
            break
    assistant_lines = assistant_lines[idx:]

    # Strip any trailing commentary after the ``` markdown closer
    try:
        end = assistant_lines.index('```')
    except ValueError:
        end = -1
    if end != -1:
        assistant_lines = assistant_lines[:end]

    # Reassemble the content
    assistant_response = '\n'.join(assistant_lines)

    return assistant_response

def write_file(filename, content):
    """
    Write a given content to a file.
    :param filename: The name of the file to write to.
    :param content: The content to write to the file.
    """
    
    with open(filename, 'w') as file:
        file.write(content)

def delete_files(*filenames):
    """
    Delete specified files.
    :param filenames: File names to delete.
    """
    for filename in filenames:
        try:
            os.remove(filename)
        except FileNotFoundError as err:
            print(err)

def get_response(model: str, system_description: str, prev_msgs: list, msg: str, retries: int):
    """
    Get a response from the openai API
    :param model: model to use in API call
    :param system_description: description to use in model configuration
    :param prev_msgs: list of previous messages
    :param msg: message to send as user this time
    :param retries: number of times this function has been called recursively, 
        used to not exceed MAX_RETRIES
    """
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {'role':'system', 'content':system_description},
                *prev_msgs,
                {'role':'user', 'content':msg}
            ]
        )
        return response
    except openai.error.RateLimitError:
        if retries < MAX_RETRIES:
            print('Encountered a RateLimitError. Retrying.')
            return get_response(model, system_description, prev_msgs, msg, retries+1)
        else:
            print(f'Could not access the API at this time. Maximum retries ({MAX_RETRIES}) reached.')
            return 'Could not access the API at this time.'

def send_message():
    """
    Function to manage user messages, perform OpenAI completions, process responses, and update GUI accordingly.
    """
    message = user_input.get()

    # Update GUI
    conversation.configure(state='normal')
    conversation.insert(tk.END, "You: ", "bold")
    conversation.insert(tk.END, message + "\n")
    conversation.configure(state='disabled')
    user_input.delete(0, tk.END)
    
    root.update_idletasks()

    time.sleep(1)

    conversation.configure(state='normal')
    conversation.insert(tk.END, "Data Viz Assistant: ", "bold")
    conversation.insert(tk.END, "Thinking...")
    conversation.configure(state='disabled')

    root.update()

    print('Thinking...')

    response = get_response(
        DATA_VIZ_MODEL, DATA_VIZ_SYSTEM_DESCRIPTION, previous_messages, message, 0)
    assistant_response = process_openai_response(response)
    write_file('output.py', assistant_response)
    print('Done thinking. Preliminary code written to output.py.')

    if VERBOSE:
        conversation.configure(state='normal')
        conversation.delete("end - 12 chars", "end")
        conversation.insert(tk.END, "Done thinking. Preliminary code was written to output.py.\n")
        conversation.insert(tk.END, "\n" + assistant_response + "\n")
        conversation.insert(tk.END, "Error Handling Assistant: ", "bold")
        conversation.insert(tk.END, "Now polishing code with error handling...")
        conversation.configure(state='disabled')
    else:
        conversation.configure(state='normal')
        conversation.delete("end - 12 chars", "end")
        conversation.insert(tk.END, "Done thinking. Preliminary code was written to output.py.\n")
        conversation.insert(tk.END, "Error Handling Assistant: ", "bold")
        conversation.insert(tk.END, "Now polishing code with error handling...")
        conversation.configure(state='disabled')

    root.update_idletasks()

    print('Now polishing code with error handling...')

    response = get_response(
        ERROR_HANDLING_MODEL, ERROR_HANDLING_SYSTEM_DESCRIPTION, [], assistant_response, 0)
    error_handling_response = process_openai_response(response)
    write_file('error-handling-output.py', error_handling_response)
    print('Done adding error handling. Polished code was written to error-handling-output.py.')

    if VERBOSE:
        conversation.configure(state='normal')
        conversation.delete("end - 42 chars", "end")
        conversation.insert(tk.END, 'Done adding error handling. Polished code was written to error-handling-output.py.')
        conversation.insert(tk.END, '\n' + error_handling_response + '\n')
        conversation.insert(tk.END, "Code Safety Assistant: ", "bold")
        conversation.insert(tk.END, "Now analyzing code safety...")
        conversation.configure(state='disabled')
    else:
        conversation.configure(state='normal')
        conversation.delete("end - 42 chars", "end")
        conversation.insert(tk.END, "Done adding error handling. Polished code was written to error-handling-output.py.\n")
        conversation.insert(tk.END, "Code Safety Assistant: ", "bold")
        conversation.insert(tk.END, "Now analyzing code safety...")
        conversation.configure(state='disabled')

    root.update_idletasks()

    print('Now analyzing code safety...')

    response = get_response(
        CODE_SAFETY_MODEL, CODE_SAFETY_SYSTEM_DESCRIPTION, [], error_handling_response, 0)
    safety_response = response.choices[0].message["content"]

    # Dangerous case
    if not safety_response.startswith('All clear'):
        print('WARNING: Code deemed dangerous. Removing python files from disk.')
        delete_files('output.py', 'error-handling-output.py')

        if VERBOSE:
            conversation.configure(state='normal')
            conversation.delete("end - 29 chars", "end")
            conversation.insert(tk.END, "WARNING: Code deemed dangerous. Deleting output.py and error-handling-output.py.")
            conversation.insert(tk.END, '\n' + safety_response + "\n")
            conversation.configure(state='disabled')
        else:
            conversation.configure(state='normal')
            conversation.delete("end - 29 chars", "end")
            conversation.insert(tk.END, "WARNING: Code deemed dangerous. Deleting output.py and error-handling-output.py.")
            conversation.configure(state='disabled')
   
   # All clear case
    else:
        print('All clear.')

        if VERBOSE:
            conversation.configure(state='normal')
            conversation.delete("end - 29 chars", "end")
            conversation.insert(tk.END, "Code deemed safe.")
            conversation.insert(tk.END, '\n' + safety_response + "\n")
            conversation.configure(state='disabled')
        else:
            conversation.configure(state='normal')
            conversation.delete("end - 29 chars", "end")
            conversation.insert(tk.END, "Code deemed safe.\n")
            conversation.configure(state='disabled')

    root.update_idletasks()

    previous_messages.extend([
        {"role": "user", "content": message},
        {"role": "assistant", "content": assistant_response},
    ])

    check_file_exists()

def view_output():
    """
    Function to view the content of 'error-handling-output.py' file in the GUI.
    """
    with open('error-handling-output.py', 'r') as file:
        content = file.read()
    conversation.configure(state='normal')
    conversation.insert(tk.END, "error-handling-output.py content:\n", "bold")
    conversation.insert(tk.END, content + "\n")
    conversation.configure(state='disabled')

def execute_output():
    """
    Function to execute the code in the 'error-handling-output.py' file.
    """
    with open("error-handling-output.py", "r") as f:
        script_code = f.read()
    try:
        exec(script_code, {}, {})
        if VERBOSE:
            print('Used exec')
    except Exception as err:
        print(err)
        # Sometimes exec fails, maybe not as robust as full python interpreter
        try:
            os.system("python3 error-handling-output.py")
            if VERBOSE:
                print('Used os.system')
        except Exception as err2:
            print('Halting process due to error: ', err2)
            conversation.configure(state='normal')
            conversation.insert(tk.END, "Halting process due to error: \n", "bold")
            conversation.insert(tk.END, str(err2) + "\n")
            conversation.configure(state='disabled')

def save_chat_history():
    """
    Function to save the chat history into a text file.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if not os.path.isdir('chat_history'):
        os.mkdir('chat_history')
    filename = os.path.join('chat_history',f"chat_history_{timestamp}.txt")
    with open(filename, 'w') as file:
        try:
            if root.winfo_exists():  # Check if the Tk window exists
                conversation.configure(state='normal')
                file.write(conversation.get("1.0", tk.END))
                conversation.configure(state='disabled')
                print('Chat history saved to', filename)
        finally:
            pass

def exit_program():
    """
    Function to save chat history and close the application.
    """
    save_chat_history()
    root.destroy()

def add_placeholder_to(entry, placeholder, color='grey'):
    entry.insert(0, placeholder)
    entry['style'] = 'Placeholder.TEntry'
    entry.bind("<FocusIn>", lambda args: entry.delete('0', 'end') if entry.get() == placeholder else None)
    entry.bind("<FocusOut>", lambda args: entry.insert('0', placeholder) if entry.get() == '' else None)

if __name__ == '__main__':

    #atexit.register(save_chat_history)

    print('Booting up...')

    gpt_4_access = input('Do you have access to the GPT4 OpenAI API? ([y]/n) ')
    if gpt_4_access.lower() in ['', 'y', 'yes']:
        DATA_VIZ_MODEL = 'gpt-4'
    else:
        DATA_VIZ_MODEL = 'gpt-3.5-turbo'

    verbose = input('Do you want to run in verbose mode? (y/[n]) ')
    if verbose.lower() in ['y', 'yes']:
        VERBOSE = True
    else:
        VERBOSE = False

    root = tk.Tk()
    root.title("Auto Plotter")

    style = ttk.Style()
    style.configure('Placeholder.TEntry', foreground='lightgrey')  # Configure Placeholder style

    frame = ttk.Frame(root, padding="10")
    frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    conversation = tk.Text(frame, wrap=tk.WORD, width=75, height=20, font=("TkDefaultFont", 12))
    conversation.tag_configure("bold", font=("TkDefaultFont", 12, "bold"))
    conversation.grid(row=0, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S))
    conversation.configure(state='disabled')

    user_input = ttk.Entry(frame, width=70, font=("TkDefaultFont", 12))
    user_input.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    add_placeholder_to(user_input, "start typing here")

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
