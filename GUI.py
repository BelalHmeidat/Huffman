import customtkinter as ctk
from customtkinter import filedialog

import Build_Huff_Tree
import Compress
import Uncompress

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")
app = ctk.CTk()
app.title("Huffman Compressor")
app.geometry("600x400")

app.resizable(False, False)

# main_frame = ctk.CTkFrame(master=app)
# main_frame.pack(padx=20, pady=20)

file_frame = ctk.CTkFrame(master=app)
file_frame.pack(side=ctk.TOP, padx=5, pady=20, anchor='n')
file_lb = ctk.CTkLabel(master=file_frame, text="File")
file_lb.pack(side=ctk.LEFT, padx=20, pady=20)
file_path_lb = ctk.CTkEntry(master=file_frame, state="readonly")
file_path_lb.pack(side=ctk.LEFT, padx=20, pady=20, ipadx=100)
file_browse_bt = ctk.CTkButton(master=file_frame, text="Browse")
file_browse_bt.pack(side=ctk.LEFT, padx=20, pady=20)

output_dir_specify_opt = ctk.CTkCheckBox(master=app, text="Specify an output directory", font=("Ariel", 16))
output_dir_specify_opt.pack(side=ctk.TOP, padx=20, pady=20)

output_lb = ctk.CTkLabel(master=app, text="", font=("Ariel", 14), wraplength=500)
output_lb.pack(side=ctk.TOP, ipadx=100, padx=20, pady=20)

button_frame = ctk.CTkFrame(master=app)
button_frame.pack(side=ctk.TOP, padx=20, pady=20)

view_huff_tree_bt = ctk.CTkButton(master=button_frame, text="View Huffman Tree", state="disabled")
view_huff_tree_bt.pack(side=ctk.LEFT, padx=20, pady=20)

view_header_info_bt = ctk.CTkButton(master=button_frame, text="View Header Content", state="disabled")
view_header_info_bt.pack(side=ctk.LEFT, padx=20, pady=20)


def log_compress_prog(output_dir, filename):
    output_lb.configure(text=f"File compressed to {output_dir}{filename}.huff", text_color="green")
    output_lb.update()


def log_decompress_progress(output_dir, filename):
    output_lb.configure(text=f'File uncompressed to {output_dir}/{filename}', text_color="green")
    output_lb.update()


def view_header_window(old_size, new_size, header, header_size):
    info = f"Uncompressed file size: {old_size} Bytes\nCompressed File Size: {new_size} Bytes\nHeader Size: {header_size} Bytes"
    header_info_window = ctk.CTkToplevel(master=app)

    header_info_window.title("Header Content Info")
    header_info_window.minsize(400, 200)
    header_info_window.resizable(False, False)

    header_info_frame = ctk.CTkFrame(master=header_info_window)
    header_info_frame.pack(side=ctk.TOP, padx=5, pady=5)

    header_info_lb = ctk.CTkLabel(master=header_info_frame, text=info)
    header_info_lb.pack(side=ctk.LEFT, padx=5, pady=5)
    header_info_val_lb = ctk.CTkLabel(master=header_info_frame, text="", text_color="green")
    header_info_val_lb.pack(side=ctk.LEFT, padx=5, pady=5)

    header_info_text = ctk.CTkTextbox(master=header_info_window)
    # header_info_text.delete(0, -1)
    header_info_text.pack(side=ctk.TOP, padx=5, pady=5, ipady=350, ipadx=350)
    header_info_text.insert("0.0", header)
    header_info_text.configure(state="disabled")


def browse_file():
    # allowed_filetypes = ("All files", "*.*"),
    input_file_path = filedialog.askopenfilename(title="Select a file", initialdir="./")
    if input_file_path == "":
        return
    file_path_lb.configure(state='normal')
    file_path_lb.delete(0, 'end')
    file_path_lb.insert(-1, str(input_file_path))
    file_path_lb.configure(state="disabled")

    def browse_output_dir():
        output_dir = filedialog.askdirectory(title="Select a directory to save output to", initialdir="./")
        if output_dir == "":
            return
        return output_dir

    output_dir = input_file_path.replace(input_file_path.split('/')[-1], "")
    if output_dir_specify_opt.get() == 1:
        output_dir = browse_output_dir()

    if output_dir == "" or None:
        file_path_lb.configure(state="normal")
        file_path_lb.delete(0, 'end')
        file_path_lb.configure(state="disabled")
        return
    elif input_file_path[-5:] == '.huff':
        output_lb.configure(text=f'Decompressing to {output_dir}/{input_file_path.split("/")[-1].replace(".huff", "")}', text_color="white")
        output_lb.update()
        header_size, header, original_file_size, compressed_file_size = Uncompress.run(input_file_path, output_dir)
        view_header_info_bt.configure(
            command=lambda: view_header_window(original_file_size, compressed_file_size, header, header_size))
        log_decompress_progress(output_dir, input_file_path.split('/')[-1][:-5])
    else:
        huff_file_name = input_file_path.split('/')[-1] + '.huff'
        output_lb.configure(text=f'Compressing to {output_dir}{huff_file_name}', text_color="white")
        output_lb.update()
        header_size, header, original_file_size, compressed_file_size = Compress.run(input_file_path, output_dir)
        view_header_info_bt.configure(
            command=lambda: view_header_window(original_file_size, compressed_file_size, header, header_size))
        log_compress_prog(output_dir, input_file_path.split('/')[-1])
    view_header_info_bt.configure(state="normal")
    view_header_info_bt.update()
    view_huff_tree_bt.configure(state="normal", command=lambda: Build_Huff_Tree.dot.view())#os.system(r'/Users/belal/PycharmProjects/Huffman/huffman_binary_tree.png'))
    view_huff_tree_bt.update()


file_browse_bt.configure(command=lambda: browse_file())

app.mainloop()
