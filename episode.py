import os, time
from file_utils import clean_path, download_file
from fancy_print import fprint, pause, clear, download_progress
from simple_term_menu import TerminalMenu

class Episode:
    def __init__(self, title: str, folder:str, url: str, episode_number: int, published: str, summary: str, tags: list):
        self.title = title
        self.file_path = folder + clean_path(title.lower().replace('/','-')) + '.mp3'
        self.url = url
        self.downloaded = os.path.exists(self.file_path)
        self.episode_number = episode_number
        self.published = tuple(published)
        self.summary = summary
        self.last_updated = time.localtime()
        self.tags = tags
    
    def to_json(self):
        return self.__dict__
    
    def update_fp(self, entry, number):
        self.last_updated = time.localtime()
        self.episode_number = number
        url = entry.links[1]['href']
        summary = entry.summary
        published = entry.published_parsed
        if url != self.url:
            self.url = url
            self.downloaded = False
        if summary != self.summary:
            self.summary = summary
        if published != self.published:
            self.published = published
    
    def download(self, verbosity=1, force=False):
        if force or not self.downloaded:
            if verbosity == 0:
                download_file(self.url, self.file_path)
            elif verbosity > 0:
                fprint(self.title, 'g')
                if self.downloaded:
                    fprint('Overwriting File...', 'gt')
                fprint('-' * 20, 'gt')
                download_file(self.url, self.file_path, download_progress)
                self.downloaded = True
        else:
            if verbosity > 0:
                fprint(self.title, 'g')
                fprint("Found in folder", 'gt')
        if verbosity > 1:
            pause()
            clear()

    def view(self):
        actions = ["Back to list", "Download", "Exit"]
        action_menu = TerminalMenu(actions)
        clear()
        if self.downloaded:
            title_format = 'gt'
        else:
            title_format = 'bt'
        fprint(self.title, title_format)
        fprint(time.asctime(tuple(self.published)), 'b')
        fprint(self.summary, 'g')
        choice = action_menu.show()
    
        if choice == 0:
            return True
        if choice == 1:
            self.download(2, True)
            return False
        if choice == 2:
            return False
    
    
    @staticmethod
    def from_dict(source_dict: dict, folder: str, episode_number: int):
        title = source_dict.get('title', None)
        if title is None:
            fprint("Invalid dict: No 'title' key", 'rt')
            return None
        url = source_dict.get('url', None)
        if url is None:
            fprint("Invalid dict: No 'url' key")
            return None
        published = source_dict.get('published', None)
        if published is None:
            fprint("Invalid dict: No 'published' key", 'rt')
            return None
        summary = source_dict.get('summary', None)
        if summary is None:
            fprint("Invalid dict: No 'summary' key", 'rt')
            return None
        tags = source_dict.get('tags', None)
        if tags is None:
            fprint("Invalid dict: No 'tags' key", 'rt')
            return None
        return Episode(title, folder, url, episode_number, published, summary, tags)
        
    @staticmethod
    def from_fp(entry, folder: str, episode_number: int):
        title = entry.title
        url = entry.links[1]['href']
        published = entry.published_parsed
        summary = entry.summary
        return Episode(title, folder, url, episode_number, published, summary, [])
