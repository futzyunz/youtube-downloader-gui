from pytube import YouTube
import tkinter as tk
import eyed3
import os
import subprocess
import threading
import traceback

# == List of functions ==
# defining function to create a new thread
def new_submit():
    threading.Thread(target=submit).start()

# defining an empty function
def empty_event():
    pass

# defining function to close/destroy window
def close_win():
    window.destroy()
   
# defining function to alter enable/disable close window to default close button
def close_event(value):
    if value==False:
        window.protocol("WM_DELETE_WINDOW", empty_event)
    else:
        window.protocol("WM_DELETE_WINDOW", close_win)
        
# defining function to lock operations(disable buttons, fields and close window)
def lock_event(value):
    if value==True:
        btn_submit.config(state=tk.DISABLED)
        btn_clear.config(state=tk.DISABLED)
        for i in entrylist:
            i.config(state=tk.DISABLED)
        for i in radiolist:
            i.config(state=tk.DISABLED)
        for i in spinboxlist:
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
        for i in spinboxlist:
            i.config(state=tk.NORMAL)
        checkbox.config(state=tk.NORMAL)
        close_event(not value)

# defining function to clear the entry fields
def clear():
    for i in entries:
        i.set("")

    status_var.set("")
    #type_var.set(1)
    trim_var.set(0)

    for i in spinboxes:
        i.set(0)
    unlock()

# defining function that will get all the entry fields
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

        if trim_var.get()==1:
            limit_length()

        # check for empty fields
        if videotype==1:
            if url=="" or title=="" or artist=="" or album=="":                
                raise AttributeError
        else:
            if url=="" or title=="":
                raise AttributeError

        status_var.set("Reading from URL...")
        # read youtube url
        yt = YouTube(url)
        if videotype==1:
            # extract audio from youtube video
            video = yt.streams.get_audio_only()

        elif videotype==2:
            # extract video from youtube video
            video = yt.streams.filter(only_video=True).order_by('resolution').desc().first()

        elif videotype==3:
            # extract mp4 from youtube video, progressive video up to 720p resolution
            video = yt.streams.get_highest_resolution()
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

        if videotype==1:
            new_file = title + ".mp3"
            status_var.set("Processing Audio...")
            # Convert the file using ffmpeg into 320 bitrate(adjustable) mp3
            audconv = ['ffmpeg','-loglevel','quiet','-i',renamed_file,'-b:a','320k',new_file]
            subprocess.run(audconv,shell=True)

            process(new_file, artist, album, title)
            os.remove(renamed_file)

        value=False
        
        # trim '-ss',start,'-to',end
        if trim:
            status_var.set("Trimming...")
            audconv = ['ffmpeg','-loglevel','quiet']
            readspinboxes = [i.get() for i in spinboxes]
            start = ":".join(readspinboxes[:3])
            end = ":".join(readspinboxes[3:])
            
            audconv.extend(['-ss',start])
            audconv.extend(['-to',end])
            audconv.extend(['-i',new_file,'-c','copy','1'+new_file])
            subprocess.run(audconv,shell=True)
            os.remove(new_file)
            os.replace('1'+new_file, new_file)

        # Relocate path for the downloaded file to User Desktop without extraction of zip/rar
        current_path = os.getcwd()
        
        if os.environ["TEMP"] in current_path:
            try:
                os.chdir(os.path.join(os.environ["USERPROFILE"], "Desktop"))
            except Exception:
                os.chdir(os.path.join(os.environ["USERPROFILE"], "OneDrive/Desktop"))
                
        os.rename(os.path.join(current_path, new_file), os.path.join(os.getcwd(), new_file))
        lock_event(value)
        clear()
        status_var.set("Done")

    # Exception happens when there's an empty field
    except AttributeError:
        label_status.config(fg="red")
        status_var.set("Please fill in all fields")
        lock_event(False)
        unlock()

    # Other exceptions
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

# defining function to update video length
def set_video_length():
    try:
        length = YouTube(url_var.get()).length
        hrs = length // 60 // 60
        mins = length // 60 % 60
        secs = length % 60

        end_hr_var.set(hrs)
        end_min_var.set(mins)
        end_sec_var.set(secs)

        # Defining global variables to set maximum hours, minutes and seconds of video
        global maxhr, maxmin, maxsec
        maxhr = hrs
        maxmin = mins
        maxsec = secs
        
        if hrs == 0:
            spinboxlist[0].config(state=tk.DISABLED)
            spinboxlist[3].config(state=tk.DISABLED)
            
            if mins == 0:
                spinboxlist[1].config(state=tk.DISABLED)
                spinboxlist[4].config(state=tk.DISABLED)

    except:
        label_status.config(fg="red")
        status_var.set("Please input a valid URL!")
        for i in spinboxlist:
            i.config(state=tk.DISABLED)
        trim_var.set(0)

# defining function to limit video length input
def limit_length():
    readspinboxes = [int(i.get()) for i in spinboxes]
    if readspinboxes[3] == 0 and readspinboxes[4] == 0 and readspinboxes[5] <= 1:
        spinboxes[5].set(1)
        
    if readspinboxes[3] >= maxhr:
        spinboxes[3].set(maxhr)
        
        if readspinboxes[4] >= maxmin:
            spinboxes[4].set(maxmin)
            
            if readspinboxes[5] >= maxsec:
                spinboxes[5].set(maxsec)
    
    if readspinboxes[3] >= 0:
        if readspinboxes[0] > readspinboxes[3]:
            spinboxes[0].set(readspinboxes[3])

        elif readspinboxes[0] == readspinboxes[3]:
            if readspinboxes[4] > 0:
                if readspinboxes[1] > readspinboxes[4]:
                    spinboxes[1].set(readspinboxes[4])

                elif readspinboxes[1] == readspinboxes[4]:
                    if readspinboxes[5] > 0:
                        if readspinboxes[2] >= readspinboxes[5]:
                            spinboxes[2].set(readspinboxes[5]-1)
        
# defining a function to disable/enable entries
def unlock():
    videotype=type_var.get()
    if videotype == 1:
        entrylist[2].config(state=tk.NORMAL)
        entrylist[3].config(state=tk.NORMAL)
    else:
        entrylist[2].config(state=tk.DISABLED)
        entrylist[3].config(state=tk.DISABLED)

    trim=trim_var.get()
    if trim:
        for i in spinboxlist:
            i.config(state=tk.NORMAL)
        set_video_length()
    else:
        for i in spinboxlist:
            i.config(state=tk.DISABLED)

# == Main Application ==
# Create a new non-resizeable window with a title
window = tk.Tk()
window.title("Youtube Downloader by FutzYunz v1.35")
window.resizable(False, False)

# Hide Window
window.withdraw()

# Initially positions tkinter window at the center
# (Failed as redundant code since widget objects haven't been created yet atm)
pos_x = int((window.winfo_screenwidth()/2) - (window.winfo_width()/2))
pos_y = int((window.winfo_screenheight()/2) - (window.winfo_height()/2))
window.geometry(f'+{pos_x}+{pos_y}')

# Create a new frame `frm_form` to contain the Label
# and Entry widgets for entering address information
frm_form = tk.Frame(relief=tk.SUNKEN, borderwidth=3)
# Pack the frame into the window
frm_form.pack()

# Configure the grid column weight
frm_form.columnconfigure(1, weight=3)
frm_form.columnconfigure(2, weight=1)
frm_form.columnconfigure(3, weight=3)
frm_form.columnconfigure(4, weight=1)
frm_form.columnconfigure(5, weight=3)

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
type_var = tk.IntVar(frm_form, 1)
trim_var = tk.IntVar()

entrylist=[]
radiolist=[]
spinboxlist=[]

# Loop over the list of field labels
for idx, text in enumerate(labels):
    # Create a Label widget with the text from the labels list
    label = tk.Label(master=frm_form, text=text)
    # Create an Entry widget
    entry = tk.Entry(master=frm_form, textvariable=entries[idx])
    entrylist.append(entry)
    # Use the grid geometry manager to place the Label and
    # Entry widgets in the row whose index is idx
    label.grid(row=idx, column=0, sticky="E")
    entry.grid(row=idx, column=1, columnspan=5, sticky="EW")

# Dictionary to create multiple buttons
values = {"Audio Only" : 1,
          "Video Only" : 2,
          "Audio + Video" : 3}

# Create multiple Radiobuttons
label = tk.Label(master=frm_form, text="Type:")
label.grid(row=4, column=0, sticky="E")
for (text, value) in values.items():
    radio = tk.Radiobutton(master=frm_form, text=text, variable=type_var,
                value=value, command=unlock)
    radiolist.append(radio)
    radio.grid(row=4, column=value*2-1, sticky="W", ipadx=5)

# Create a Checkbox widget
checkbox = tk.Checkbutton(master=frm_form, text="Trim (hh:mm:ss)",
                          variable=trim_var, command=unlock)
checkbox.grid(row=5, column=1, sticky="W")

# List of field labels
labels = [
    "Start Time:",
    "End Time:",
]

# List of field entries in format [hh:mm:ss]
# example: 00:14:20
# Spinbox variables
start_hr_var = tk.StringVar(value=0)
start_min_var = tk.StringVar(value=0)
start_sec_var = tk.StringVar(value=0)
end_hr_var = tk.StringVar(value=0)
end_min_var = tk.StringVar(value=0)
end_sec_var = tk.StringVar(value=0)

spinboxes = [start_hr_var, start_min_var, start_sec_var,
           end_hr_var, end_min_var, end_sec_var]

# Loop over the list of field labels
for idx, text in enumerate(labels):
    # Create a Label widget with the text from the labels list
    label = tk.Label(master=frm_form, text=text)
    for i in range(idx*3, idx*3+3):
        # Create a Spinbox widget with min and max value
        spinbox = tk.Spinbox(master=frm_form, from_=0, to=59,
                             textvariable=spinboxes[i], wrap=True, command=limit_length, vcmd=limit_length)
        spinboxlist.append(spinbox)
        spinbox.grid(row=6+idx, column=(i%3)*2+1, sticky="EW")

        if not i == idx*3+2:
            templabel = tk.Label(master=frm_form, text=":")
            templabel.grid(row=6+idx, column=(i%3)*2+2, sticky="EW", ipadx=5)
        
    # Use the grid geometry manager to place the Spinbox, Label and
    # Entry widgets in the row whose index is idx
    label.grid(row=6+idx, column=0, sticky="E")


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

# Disable the trim input entry at the beginning while program loads
for i in spinboxlist:
    i.config(state=tk.DISABLED)

# Positions the tkinter window correctly at the center of display
window.update()

pos_x = int((window.winfo_screenwidth()/2) - (window.winfo_width()/2))
pos_y = int((window.winfo_screenheight()/2) - (window.winfo_height()/2))
window.geometry(f'+{pos_x}+{pos_y}')

# Display hidden window
window.deiconify()

# Start the main application
window.mainloop()
