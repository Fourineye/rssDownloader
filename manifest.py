'''
    Paul Smith
    
    A python class for holding rss feed data and saving it in usable format
    for the app.
      
'''


import os, time
import feedparser as fp
from simple_term_menu import TerminalMenu
from file_utils import read_manifest, write_manifest, clean_path
from fancy_print import fprint, pause, clear
from episode import Episode


class Manifest:
    def __init__(self):
        self.title = ''
        self.author = ''
        self.folder = ''
        self.url = ''
        self.last_updated = ()
        self.episodes = []
        
    @staticmethod
    def from_json(path):
        manifest = Manifest()
        try:
            json_data = read_manifest(path + '.manifest')
        except:
            fprint('No manifest found...', 'rt')
            return None
        manifest.title = json_data['title']
        manifest.author = json_data['author']
        manifest.last_updated = tuple(json_data['last_updated'])
        manifest.folder = path
        manifest.url = json_data['url']
        for number, episode in enumerate(json_data['episodes']):
            episode = Episode.from_dict(episode, path, number)
            manifest.episodes.append(episode)
        return manifest
    
    @staticmethod
    def from_fp(feed_object):
        manifest = Manifest()
        manifest.title = feed_object.feed.title
        manifest.author = feed_object.feed.author
        manifest.folder = '../' + clean_path(manifest.title.replace(" ", "_")) + '/'
        manifest.url = feed_object.href
        manifest.last_updated = feed_object.feed.updated_parsed
        for number, episode in enumerate(feed_object.entries[::-1]):
            episode = Episode.from_fp(episode, manifest.folder, number)
            manifest.episodes.append(episode)
        return manifest
    
    @staticmethod
    def from_url(url):
        fprint("Fetching feed...", 'g')
        feed_object = fp.parse(url)
        fprint("Generating manifest...", 'gO')
        try:
            manifest = Manifest.from_fp(feed_object)
        except:
            fprint('Invalid URL...', 'rtO')
            return None
        return manifest
        
    def save_to_json(self):
        json_data = {
            'title': self.title,
            'author': self.author,
            'last_updated': self.last_updated,
            'url': self.url,
            'episodes': [
                episode.to_json() for episode in self.episodes
            ]
        }
        write_manifest(json_data, self.folder + '.manifest')
    
    def get_episode(self, title):
        for episode in self.episodes:
            if episode.title == title:
                return episode
        return None
        
    def update(self, forced=False):
        feed_object = fp.parse(self.url)
        if (self.last_updated == feed_object.feed.updated_parsed) and not forced:
            fprint('Manifest up to date..', 'gt')
            pause()
            return
        
        if self.title == feed_object.feed.title:
            for number, feed_episode in enumerate(feed_object.entries[::-1]):
                episode = self.get_episode(feed_episode.title)
                if episode is None:
                    self.episodes.insert(number, Episode.from_fp(feed_episode, self.folder, number))
                else:
                    episode.update_fp(feed_episode, number)
        fprint('Manifest updated', 'gt')
        pause()
    
    def view_episodes(self):
        # Initialize variables
        page_size = 25
        current_page = 1
        last_page = len(self.episodes) // page_size + 1
    
        # Loop until a episode is selected
        selecting_episode = True
        while selecting_episode:
            # get start and end index
            start = (current_page - 1) * page_size
            end = page_size * current_page
            if end >= len(self.episodes):
                end = len(self.episodes) - 1
                selecting_episode = False
        
            # create list of episode titles and commands
            episodes = []
            if current_page != 1:
                episodes.append("[,] Previous page")
            for episode in self.episodes[start:end]:
                episodes.append(episode.title)
         
            if selecting_episode:
                episodes.append("[.] Next page")
        
            episodes.append("[q] Back")
            episode_menu = TerminalMenu(episodes)
        
            # Display menu
            clear()
            fprint(f'{self.title}: {current_page}/{last_page}', 'gt')
            episode = episode_menu.show()
        
            # Process Selection
        
            if episodes[episode] == "[.] Next page":
                current_page += 1
            elif episodes[episode] == "[,] Previous page":
                current_page -= 1
                selecting_episode = True
            elif episodes[episode] == "[q] Back":
                selecting_episode = False
                clear()
            else:
                episode = self.get_episode(episodes[episode])
                selecting_episode = episode.view()
                self.save_to_json()
                clear()
    
    def download_episodes(self, verbosity=1, force=False, episodes=None):
        if episodes is None:
            for episode in self.episodes:
                episode.download(verbosity=verbosity, force=force)
        else:
            for episode in episodes:
                if isinstance(episode, int):
                    self.episodes[episode].download(verbosity=verbosity, force=force)
                elif isinstance(episode, str):
                    if episode.isnumeric():
                        self.episodes[int(episode)].download(verbosity=verbosity, force=force)
                    else:
                        self.get_episode(episode).download(verbosity=verbosity, force=force)
        self.save_to_json()
        pause()
