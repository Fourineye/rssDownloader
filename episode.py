'''
    Paul Smith
    
    A python class for containing a rss item for podcasts
    
'''


import os, time
from file_utils import clean_path, download_file
from fancy_print import fprint, pause, clear, download_progress
from simple_term_menu import TerminalMenu

class Episode:
    """
    A class to represent a rss item for a podcast
    
    ...
    
    Attributes
    ----------
    title : str
        the title of the podcast episode
    file_path : str
        the file path for the downloaded file
    url : str
        the url for the hosted file
    downloaded : bool
        whether the file is present on the drive at the file_path
    published : tuple
        the publishing date of the episode in tuple format
    summary : str
        the description of the item from the rss feed
    last_updated : tuple
        the last time the episode object was updated
    tags : list
        a list of tags for the episode
        
    Methods
    -------
    to_json()
        returns the object.__dict__ for saving to json
    update_fp(entry: feedparser entry, number: int)
        updates the last_updated time, and compares the entry against the saved
        values, updating them if they have changed
    download(verbosity: int=1, force: bool=False)
        downloads the file at url to file_path with varying levels of status 
        printing
    view()
        shows the title, summary, and a menu of actions available to the user
        
    Static Methods
    --------------
    from_dict(source_dict: dict, folder: str, episode_number: int)
        returns an initalized an Episode object from a dictonary prepending
        the folder to the generated file_path
    from_fp(entry: feedparser entry, folder: str, episode_number: int)
        returns an intialized an Episode object from a feedparser entry
        prepending the folder to the generated file_path
    """
    
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
    
    def to_json(self) -> dict:
        """Returns the object's __dict__
        
        Returns
        -------
        dict
            the objects attributes
        
        """
        return self.__dict__
    
    def update_fp(self, entry, number: int) -> None:
        """Updates the object's attributes from an entry
        
        Parameters
        ----------
        entry : feedparser entry
            An entry from a feedparser parsed feed
        number : int
            The number of the episode chronologically
        """
        
        self.last_updated = time.localtime()
        self.episode_number = number
        url = None
        for link in entry.links:
            if 'audio' in link['type']:
                url = link['href']
        if url is None:
            fprint('No valid audio file', 'rt')

        summary = entry.summary
        published = entry.published_parsed
        if url != self.url:
            self.url = url
            self.downloaded = False
        if summary != self.summary:
            self.summary = summary
        if published != self.published:
            self.published = published
    
    def download(self, verbosity: int=1, force: bool=False)-> None:
        """Downloads the url to file_path
        
        Parameters
        ----------
        verbosity : int, optional
            The logging level for the function (default is 1)
            0: no logging
            1: progress bar
            2: pauses after finished
        force : bool, optional
            Whether the function should overwrite the file if it is already 
            present (default is False)
        
        """
        
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

    def view(self) -> bool:
        """Shows the title, summary, and a menu of actions available to the user
        
        Displays the title of the episode, the date it was published, and the
        summary. Below which it shows a terminal menu  with options to download, 
        go back, or exit, working with a Manifest object for displaying a list of
        episodes
        
        Returns
        -------
        bool
            Whether the user has selected to exit the list view
        """
        
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
            return True
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
        url = None
        for link in entry.links:
            if 'audio' in link['type']:
                url = link['href']
        if url is None:
            fprint('No valid audio file', 'rt')
        published = entry.published_parsed
        summary = entry.summary
        return Episode(title, folder, url, episode_number, published, summary, [])
