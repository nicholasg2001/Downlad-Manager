import os, logging, re

from os import scandir, rename
from os.path import splitext, exists, join, isdir
from time import sleep 
from shutil import move
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

def get_downloads_folder():
    home = os.path.expanduser("~")
    return os.path.join(home, "Downloads")

source_dir = get_downloads_folder()
dest_dir_music = os.path.join(source_dir, "Music")
dest_dir_applications = os.path.join(source_dir, "Applications")
dest_dir_schoolwork = os.path.join(source_dir, "Schoolwork")
dest_dir_miscdocuments = os.path.join(source_dir, "Misc_Documents")
dest_dir_image = os.path.join(source_dir, "Images")
dest_dir_video = os.path.join(source_dir, "Videos")

# Ensure destination directories exist
for dest_dir in [dest_dir_music, dest_dir_applications, dest_dir_schoolwork, dest_dir_miscdocuments, dest_dir_image, dest_dir_video]:
    if not isdir(dest_dir):
        os.makedirs(dest_dir)


image_extensions = [".jpg", ".jpeg", ".jpe", ".jif", ".jfif", ".jfi", ".png", ".gif", ".webp", ".tiff", ".tif", ".psd", ".raw", ".arw", ".cr2", ".nrw",
                    ".k25", ".bmp", ".dib", ".heif", ".heic", ".ind", ".indd", ".indt", ".jp2", ".j2k", ".jpf", ".jpf", ".jpx", ".jpm", ".mj2", ".svg", ".svgz", ".ai", ".eps", ".ico"]

video_extensions = [".webm", ".mpg", ".mp2", ".mpeg", ".mpe", ".mpv", ".ogg",
                    ".mp4", ".mp4v", ".m4v", ".avi", ".wmv", ".mov", ".qt", ".flv", ".swf", ".avchd"]

audio_extensions = [".m4a", ".flac", "mp3", ".wav", ".wma", ".aac"]

document_extensions = [".doc", ".docx", ".odt",
                       ".pdf", ".xls", ".xlsx", ".ppt", ".pptx"]

application_extensions = [".exe", ".msi", ".bat", ".cmd", ".com", ".jar", ".app", ".run"]

def make_unique(dest, name):
    filename, extension = splitext(name)
    counter = 1
    #If file already exists, add a unique number to filename
    while exists(f"{dest}/{name}"):
        name = f"{filename}({str(counter)}){extension}"
        counter += 1

    return name

def move_file(dest, entry, name):
    if exists(entry):  # Check if the file or folder still exists
        if exists(join(dest, name)):
            unique_name = make_unique(dest, name)
            old_name_path = join(dest, name)
            new_name_path = join(dest, unique_name)
            rename(old_name_path, new_name_path)
        else:
            move(entry, dest)
    else:
        logging.warning(f"File or folder does not exist: {entry}")

class MoverHandler(FileSystemEventHandler):
    #This function will run anytime theres a change in "source_dir"
    def on_modified(self, event):
        with scandir(source_dir) as entries:
            for entry in entries:
                name = entry.name
                self.check_audio_files(entry, name)
                self.check_video_files(entry, name)
                self.check_image_files(entry, name)
                self.check_document_files(entry, name)

    def check_audio_files(self, entry, name):  #Checks all Audio Files
        for audio_extension in audio_extensions:
            if name.endswith(audio_extension) or name.endswith(audio_extension.upper()):
                dest = dest_dir_music
                move_file(dest, entry, name)
                logging.info(f"Moved audio file: {name}")
                return 

    def check_video_files(self, entry, name):  #Checks all Video Files
        for video_extension in video_extensions:
            if name.endswith(video_extension) or name.endswith(video_extension.upper()):
                move_file(dest_dir_video, entry, name)
                logging.info(f"Moved video file: {name}")
                return 

    def check_image_files(self, entry, name):  #Checks all Image Files
        for image_extension in image_extensions:
            if name.endswith(image_extension) or name.endswith(image_extension.upper()):
                move_file(dest_dir_image, entry, name)
                logging.info(f"Moved image file: {name}")
                return 

    def check_application_files(self, entry, name):  # Checks all Application Files
        for application_extension in application_extensions:
            if name.endswith(application_extension) or name.endswith(application_extension.upper()):
                move_file(dest_dir_applications, entry, name)
                logging.info(f"Moved application file: {name}")
                return


    def check_document_files(self, entry, name):
        # Regex for checking if a document is schoolwork
        pattern = re.compile(r'[A-Z]{3}\d{3}')
        folder_name = os.path.basename(entry)  # Get the base name of the folder
        # Check if it's a ZIP file
        if name.endswith(".zip") and pattern.search(folder_name):
            move_file(dest_dir_schoolwork, entry, name)
            logging.info(f"Moved ZIP file: {name}")
            return 

        # Check if it's a folder and the folder name matches the regex
        if os.path.isdir(entry) and pattern.search(folder_name):
            move_file(dest_dir_schoolwork, entry, name)
            logging.info(f"Moved schoolwork folder: {name}")
            return 

        # Check if it's a document file and matches the regex
        for documents_extension in document_extensions:
            if name.endswith(documents_extension) or name.endswith(documents_extension.upper()):
                # Use re.search to check if the pattern is found anywhere in the string
                if pattern.search(name):
                    move_file(dest_dir_schoolwork, entry, name)
                    logging.info(f"Moved schoolwork document file: {name}")
                    return 

        # If none of the conditions matched, move it to misc documents
        move_file(dest_dir_miscdocuments, entry, name)
        logging.info(f"Moved misc document file/folder: {name}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    path = source_dir
    event_handler = MoverHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            sleep(10)
    except KeyboardInterrupt:
        observer.stop()
    observer.join() 