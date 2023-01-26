import feedparser as fp
import requests
import sys, os, time, json
from simple_term_menu import TerminalMenu
from fancy_print import fprint, clear, progress_bar
from file_utils import clean_path, write_manifest, read_manifest


def debug_entry(entry):
    for item, value in entry.items():
        print('Item: ', item)
        print('Value: ', value)

def download_file(url: str, filename: str=None, callback=None):
    if filename is None:
        filename = url.split('/')[-1]
    # NOTE the stream=True parameter below
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        file_size = int(r.headers.get('Content-Length'))
        content_remaining = int(file_size)
        with open(filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192): 
                # If you have chunk encoded response uncomment if
                # and set chunk_size parameter to None.
                #if chunk:
                content_remaining -= len(chunk)
                f.write(chunk)
                if callable(callback):
                    callback(content_remaining, file_size)
    

def download_callback(content_remaining, file_size) -> None:
    progress = file_size - content_remaining
    percentage = progress / file_size
    
    progress_bar(percent, f' {round(progress/1048576, 2)}MB / {round(file_size/1048576, 2)}MB', 'Ogt')

def update_manifest(path: str, feed_object) -> None:
    fprint("Updating Manifest...", 'b')
    fprint('-' * 20, 'b')
    manifest = read_manifest(path + 'manifest.json')
    progress = 2
    total = len(feed_object.entries) + 2
    fprint('-' * 20 + f' 00.00%', 'bO')
    manifest['title'] = feed_object.feed.title
    manifest['author'] = feed_object.feed.author
    
    manifest['episodes'] = []
    for number, entry in enumerate(feed_object.entries[::-1]):
        percent= progress / total
        progress_bar(percent, f'{round(percent * 100, 2)}%')
        episode = {}
        episode['title'] = entry.title
        episode['file_path'] = path + clean_path(entry.title.lower().replace(" ", "").replace("/", '-') + '.mp3')
        episode['downloaded'] = os.path.exists(episode['file_path'])
        episode['download_link'] = entry.links[1]['href']
        episode['number'] = number
        episode['published'] = entry.published
        episode['summary'] = entry.summary
        manifest['episodes'].append(episode)
        progress += 1
    percent= progress / total
    progress_bar(percent, f'{round(percent * 100, 2)}%')
    write_manifest(manifest, path + 'manifest.json')
    fprint('Manifest Updated', 'gt')
    input("")
    clear()


def download_episodes(feed_object, folder):
    for number, entry in enumerate(feed_object.entries[::-1]):
            
        path = folder + clean_path(entry.title.lower().replace(" ", "").replace("/", '-') + '.mp3')
        url = entry.links[1]['href']
            
        fprint(f'Episode Title: {entry.title}')
        if not os.path.exists(path):
            print("-" * 20)
            download_file(url, path, download_callback)
        else:
            fprint("Found in directory", 'gt')
    
    update_manifest(folder, feed_object)
    

def view_episode(episode) -> bool:
    actions = ["Back to list", "Exit"]
    action_menu = TerminalMenu(actions)
    clear()
    if episode['downloaded']:
        title_format = 'gt'
    else:
        title_format = 'bt'
    fprint(episode['title'], title_format)
    fprint(episode['published'], 'b')
    fprint(episode['summary'], 'g')
    choice = action_menu.show()
    
    if choice == 0:
        return True
    if choice == 1:
        return False


def view_episodes(folder):
    if not os.path.exists(folder + 'manifest.json'):
        fprint('Manifest not found', 'rt')
        return
    clear()
    
    # Load Manifest
    manifest = read_manifest(folder + 'manifest.json')
    
    # Initialize variables
    page_size = 25
    current_page = 1
    last_page = len(manifest['episodes']) // page_size + 1
    
    # Loop until a episode is selected
    selecting_episode = True
    while selecting_episode:
        # get start and end index
        start = (current_page - 1) * page_size
        end = page_size * current_page
        if end >= len(manifest['episodes']):
            end = len(manifest['episodes']) - 1
            selecting_episode = False
        
        # create list of episode titles and commands
        episodes = []
        if current_page != 1:
            episodes.append("Previous page")
        for episode in manifest['episodes'][start:end]:
            episodes.append(episode['title'])
         
        if selecting_episode:
            episodes.append("Next page")
        
        episodes.append("Back")
        episode_menu = TerminalMenu(episodes)
        
        # Display menu
        clear()
        fprint(f'{manifest["title"]}: {current_page}/{last_page}', 'gt')
        episode = episode_menu.show()
        
        # Process Selection
        
        if episodes[episode] == "Next page":
            current_page += 1
        elif episodes[episode] == "Previous page":
            current_page -= 1
            selecting_episode = True
        elif episodes[episode] == "Back":
            selecting_episode = False
            clear()
        else:
            if current_page == 1:
                episode += 1
            episode = manifest['episodes'][start + episode - 1]
            selecting_episode = view_episode(episode)
            
if __name__ == '__main__':
    
    feed_manifest = read_manifest('feed_manifest.json')
    feeds = [feed['title'] for feed in feed_manifest['feeds'] ]
    actions = [
        "Download New",
        "View Episodes",
        "Update Manifest",
        "Exit"
    ]
    
    action_menu = TerminalMenu(actions)
    feed_menu = TerminalMenu(feeds)
    feed = feed_menu.show()
    feed = feed_manifest['feeds'][feed]
    
    if not os.path.exists(feed['folder']):
        os.mkdir(feed['folder'])
    
    active = True
    while active:
        fprint(feed['title'], 'bt')
        

        action = action_menu.show()
    
        if action == 0:
            feed_ = fp.parse(feed['link'])
            download_episodes(feed_, feed['folder'])
        elif action == 1:
            view_episodes(feed['folder'])
        elif action == 2:
            feed_ = fp.parse(feed['link'])
            update_manifest(feed['folder'], feed_)
        elif action == 3:
            active = False
            
