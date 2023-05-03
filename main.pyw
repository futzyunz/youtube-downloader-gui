from pytube import YouTube
import tkinter as tk
import eyed3
import os
import subprocess
import threading

# == List of functions ==
# defining a function to create a new thread
def new_submit():
    threading.Thread(target=submit).start()

# defining an empty function
def empty_event():
   pass

# defining a function to close/destroy window
def close_win():
   window.destroy()
   
# defining a function to enable/disable window close button
def close_event(value):
    if value==False:
        window.protocol("WM_DELETE_WINDOW", empty_event)
    else:
        window.protocol("WM_DELETE_WINDOW", close_win)
        
# defining a function to lock operations
def lock_event(value):
    if value==True:
        btn_submit.config(state=tk.DISABLED)
        btn_clear.config(state=tk.DISABLED)
        for i in entrylist:
            i.config(state=tk.DISABLED)
        for i in radiolist:
            i.config(state=tk.DISABLED)
        checkbox.config(state=tk.DISABLED)
        close_event(not value)
    else:
        btn_submit.config(state=tk.NORMAL)
        btn_clear.config(state=tk.NORMAL)
        for i in entrylist:
            i.config(state=tk.NORMAL)
        for i in radiolist:
            i.config(state=tk.NORMAL)
        checkbox.config(state=tk.NORMAL)
        close_event(not value)

# defining a function that will clear the entry fields
def clear():
    url_var.set("")
    title_var.set("")
    artist_var.set("")
    album_var.set("")

    status_var.set("")
    #type_var.set("1")
    trim_var.set("0")
    start_var.set("")
    end_var.set("")
    unlock()

# defining a function that will get all the entry fields
def submit():
    try:
        value=True
        lock_event(value)
        label_status.config(fg="green")
        status_var.set("Program Loading...")
        url=url_var.get()
        title=title_var.get()
        artist=artist_var.get()
        album=album_var.get()
        videotype=type_var.get()
        trim=trim_var.get()

        if trim:
            start=start_var.get()
            end=end_var.get()

        if videotype=="1":
            if url=="" or title=="" or artist=="" or album=="":
                label_status.config(fg="red")
                status_var.set("Please fill in all fields")
                lock_event(False)
                unlock()
                return
        else:
            if url=="" or title=="":
                label_status.config(fg="red")
                status_var.set("Please fill in all fields")
                lock_event(False)
                unlock()
                return

        status_var.set("Reading from URL...")
        # read youtube url
        yt = YouTube(url)
        if videotype=="1":
            # extract audio from youtube video
            video = yt.streams.get_audio_only()
            # old code:
            # yt.streams.filter(only_audio=True).first()

        elif videotype=="2":
            # extract video from youtube video
            video = yt.streams.filter(only_video=True).order_by('resolution').desc().first()

        elif videotype=="3":
            # extract mp4 from youtube video, progressive video up to 720p resolution
            video = yt.get_highest_resolution()
            # old code:
            # video = yt.streams.filter(progressive=True,file_extension='mp4')
            # .order_by('resolution').desc().first()           
        
        status_var.set("Dowloading Audio/Video...")
        # download the file
        out_file = video.download()
        # save the file
        base, ext = os.path.splitext(out_file)
        renamed_file = title + ext
        os.replace(out_file, renamed_file)
        new_file = renamed_file

        if videotype=="1":
            new_file = title + ".mp3"
            status_var.set("Processing Audio...")
            # Convert the file using ffmpeg into 320 bitrate(adjustable) mp3
            audconv = ['ffmpeg','-i',renamed_file,'-b:a','320k',new_file]
            subprocess.run(audconv)

            process(new_file, artist, album, title)
            os.remove(renamed_file)

        value=False
        
        # trim '-ss',start,'-to',end
        if trim:
            status_var.set("Trimming...")
            audconv = ['ffmpeg']
            if start!="":
                audconv.extend(['-ss',start])
            if end!="":
                audconv.extend(['-to',end])
            audconv.extend(['-i',new_file,'-c','copy','1'+new_file])
            subprocess.run(audconv)
            os.remove(new_file)
            os.replace('1'+new_file, new_file)

        # Relocate path for the downloaded file to User Desktop without extraction of zip/rar
        current_path = os.getcwd()
        
        if os.environ["TEMP"] in current_path:
            try:
                os.chdir(os.path.join(os.environ["USERPROFILE"], "Desktop"))
            except Exception:
                os.chdir(os.path.join(os.environ["USERPROFILE"], "OneDrive/Desktop"))
                
        os.rename(os.path.join(current_path, new_file), os.path.join(os.getcwd(), os.path.join(new_file)))
        lock_event(value)
        clear()
        status_var.set("Done")
            
    except:
        label_status.config(fg="red")
        status_var.set("An Error Occured!")
        lock_event(False)
        unlock()
        print(traceback.format_exc())

# defining a function that will edit the metadata of audiofile
def process(file, artist, album, title):
    status_var.set("Processing Audio Information...")
    audiofile=eyed3.load(file)
    if audiofile.tag is None:
        audiofile.tag = eyed3.id3.Tag()
    audiofile.tag.title=u""+title
    audiofile.tag.artist=u""+artist
    audiofile.tag.album=u""+album
    audiofile.tag.save()

# defining a function to disable/enable entries
def unlock():
    videotype=type_var.get()
    if videotype == "1":
        entrylist[2].config(state=tk.NORMAL)
        entrylist[3].config(state=tk.NORMAL)
    else:
        entrylist[2].config(state=tk.DISABLED)
        entrylist[3].config(state=tk.DISABLED)

    trim=trim_var.get()
    if trim:
        entrylist[4].config(state=tk.NORMAL)
        entrylist[5].config(state=tk.NORMAL)
    else:
        entrylist[4].config(state=tk.DISABLED)
        entrylist[5].config(state=tk.DISABLED)

# == Main Application ==
# Create a new non-resizeable window with a title
window = tk.Tk()
# Hide Window
window.withdraw()
window.title("Youtube Downloader by FutzYunz v1.3")
window.resizable(False, False)

# Initially positions tkinter window at the center (redundant code)
pos_x = int((window.winfo_screenwidth()/2) - (window.winfo_width()/2))
pos_y = int((window.winfo_screenheight()/2) - (window.winfo_height()/2))

window.geometry(f'+{pos_x}+{pos_y}')

# Create a new frame `frm_form` to contain the Label
# and Entry widgets for entering address information
frm_form = tk.Frame(relief=tk.SUNKEN, borderwidth=3)
# Pack the frame into the window
frm_form.pack()

# List of field labels
labels = [
    "URL:",
    "Title:",
    "Artist:",
    "Album:",
]

# List of field entries
url_var = tk.StringVar()
title_var = tk.StringVar()
artist_var = tk.StringVar()
album_var = tk.StringVar()

entries = [
    url_var,
    title_var,
    artist_var,
    album_var,
]

# RadioButton and CheckboxButton variables
type_var = tk.StringVar(frm_form, "1")
trim_var = tk.IntVar()

entrylist=[]
radiolist=[]

# Loop over the list of field labels
for idx, text in enumerate(labels):
    # Create a Label widget with the text from the labels list
    label = tk.Label(master=frm_form, text=text)
    # Create an Entry widget
    entry = tk.Entry(master=frm_form, width=50, textvariable=entries[idx])
    entrylist.append(entry)
    # Use the grid geometry manager to place the Label and
    # Entry widgets in the row whose index is idx
    label.grid(row=idx, column=0, sticky="E")
    entry.grid(row=idx, column=1, columnspan=3)

# Dictionary to create multiple buttons
values = {"Audio Only" : "1",
          "Video Only" : "2",
          "Audio + Video" : "3"}

# Create multiple Radiobuttons
label = tk.Label(master=frm_form, text="Type:")
label.grid(row=4, column=0, sticky="E")
for (text, value) in values.items():
    radio = tk.Radiobutton(master=frm_form, text=text, variable=type_var,
                value=value, command=unlock)
    radiolist.append(radio)
    radio.grid(row=4, column=int(value))

# Create a Checkbox widget
checkbox = tk.Checkbutton(master=frm_form, text="Trim (hh:mm:ss)",
                          variable=trim_var, command=unlock)
checkbox.grid(row=5, column=1, sticky="W", columnspan=3)

# List of field labels
labels = [
    "Start Time:",
    "End Time:",
]

# List of field entries in format [hh:mm:ss]
# example: 00:14:20
start_var = tk.StringVar()
end_var = tk.StringVar()

entries = [start_var,end_var]

# Loop over the list of field labels
for idx, text in enumerate(labels):
    # Create a Label widget with the text from the labels list
    label = tk.Label(master=frm_form, text=text)
    # Create an Entry widget
    entry = tk.Entry(master=frm_form, width=50, textvariable=entries[idx])
    entrylist.append(entry)
    # Use the grid geometry manager to place the Label and
    # Entry widgets in the row whose index is idx
    label.grid(row=6+idx, column=0, sticky="E")
    entry.grid(row=6+idx, column=1, columnspan=3)

# Create a new frame `frm_buttons` to contain the
# Submit and Clear buttons. This frame fills the
# whole window in the horizontal direction and has
# 5 pixels of horizontal and vertical padding.
frm_buttons = tk.Frame()
frm_buttons.pack(fill=tk.X, ipadx=5, ipady=5)

# Status variable
status_var = tk.StringVar()

# Create a Label widget for the status text
label_status = tk.Label(master=frm_buttons, fg="green",
                 textvariable=status_var, compound="top")
label_status.pack(side=tk.LEFT, ipadx=10)

# Create the "Submit" button and pack it to the
# right side of `frm_buttons`
btn_submit = tk.Button(master=frm_buttons, text="Download", command=new_submit)
btn_submit.pack(side=tk.RIGHT, padx=10, ipadx=10)

# Create the "Clear" button and pack it to the
# right side of `frm_buttons`
btn_clear = tk.Button(master=frm_buttons, text="Clear", command=clear)
btn_clear.pack(side=tk.RIGHT, ipadx=10)

# Freeze the trim function at the beginning
entrylist[4].config(state=tk.DISABLED)
entrylist[5].config(state=tk.DISABLED)

# Positions the tkinter window correctly at the center of display
window.update()

pos_x = int((window.winfo_screenwidth()/2) - (window.winfo_width()/2))
pos_y = int((window.winfo_screenheight()/2) - (window.winfo_height()/2))

window.geometry(f'+{pos_x}+{pos_y}')
# Show hidden window
window.deiconify()

# Start the application
window.mainloop()
