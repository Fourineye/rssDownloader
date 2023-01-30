'''
    Paul Smith 2023
    
    An app designed for downloading podcasts from rss feeds and viewing
    the episodes in a saved manifest
    
'''
import os
import time
import feedparser as fp
from simple_term_menu import TerminalMenu
from fancy_print import fprint, clear, pause
from file_utils import clean_path, write_manifest, read_manifest
from manifest import Manifest


def select_feed():
    '''
        Select a feed from the saved manifest
        
        returns: {'title': str, 'url': str, 'folder': str}
        
    '''
    
    # Loop until feed is selected
    selecting_feed = True
    while selecting_feed:
        # Get saved list of feeds, or create one if it does not exist
        if not os.path.exists('feed_manifest.json'):
            write_manifest({'feeds': []}, 'feed_manifest.json')
        feed_manifest = read_manifest('feed_manifest.json')
        
        # Create a list of feed titles and actions for the selection menu
        feeds = [feed['title'] for feed in feed_manifest['feeds'] ]
        feeds.append("Add feed")
        feed_menu = TerminalMenu(feeds)
        
        # Get user selection
        fprint('Available Feeds', 'g')
        feed = feed_menu.show()
        
        # Handle the 'Add feed' action
        if feeds[feed] == "Add feed":
            clear()
            # Get the url from the user
            feed_to_add = input("Enter feed URL: ")
            # Attempt to parse rss xml from the url
            try:
                # Parse the rss feed using feedparser
                feed = fp.parse(feed_to_add)
                
                # Create new feed entry 
                entry = {}
                entry['title'] = feed.feed.title
                entry['url'] = feed_to_add
                entry['folder'] = f'../{clean_path(feed.feed.title.replace(" ", "_"))}/'
                
                # Save the entry to the manifest
                feed_manifest['feeds'].append(entry)
                write_manifest(feed_manifest, 'feed_manifest.json')
            except:
                # Handle error
                fprint("There was a problem... please try again", 'rt')
                pause()
                clear()
                # Return to beginning of loop
                continue
        else:
            # Get the user's selection from the manifest
            feed = feed_manifest['feeds'][feed]
            selecting_feed = False
    
    # Make a folder for the feed if one does not exist
    if not os.path.exists(feed['folder']):
        os.mkdir(feed['folder'])
        
    # Return the feed selected
    return feed
    
                             
if __name__ == '__main__':
    # Define action menu
    actions = [
        "Download New",
        "View Episodes",
        "Update Manifest",
        "Back",
        "Exit"
    ]
    action_menu = TerminalMenu(actions)
    
    # Loop until user exits
    running = True
    while running:
        # Select saved feed
        feed = select_feed()
    
        # Load the manifest
        manifest = Manifest.from_json(feed['folder'])
        if manifest is None:
            manifest = Manifest.from_url(feed['link'])
        
        # Loop until user exits or changes feeds
        active = True
        while active:
            # Display Title, date, and action menu
            clear()
            fprint(manifest.title, 'bt')
            fprint('Last updated: ' + time.asctime(manifest.last_updated), 'b')

            action = action_menu.show()
           
            # Process user action selection
            if action == 0:
                manifest.download_episodes()
            elif action == 1:
                manifest.view_episodes()
            elif action == 2:
                manifest.update()
            elif action == 3:
                active = False
                clear()
            elif action == 4:
                active = False
                running = False
                
