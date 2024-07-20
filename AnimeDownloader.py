from hianime import HiAnimeIE
import re
from colorama import Fore
from yt_dlp import YoutubeDL
from yt_dlp.utils import clean_html, get_element_by_class, get_elements_html_by_class
import os

def get_episode_input(prompt, min_value, max_value):
    while True:
        try:
            episode_no = int(input(prompt))
            if min_value <= episode_no <= max_value:
                return episode_no
            else:
                print(f"Please enter a number between {min_value} and {max_value}.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")

def choose_resolution():
    print("\nChoose resolution:\n\n"
          "1." + Fore.LIGHTYELLOW_EX + " 1080p" + Fore.LIGHTWHITE_EX + " (FHD)\n2." + Fore.LIGHTYELLOW_EX + " 720p " +
          Fore.LIGHTWHITE_EX + "(HD)\n3. " + Fore.LIGHTYELLOW_EX + "360p " + Fore.LIGHTWHITE_EX + " (SD)\n")
    resolution_map = {1: '1080p', 2: '720p', 3: '360p'}
    while True:
        try:
            choice = int(input("Enter Choice: "))
            if choice in [1, 2, 3]:
                resolution_height = resolution_map[choice]
                return resolution_height
            else:
                print("Invalid choice. Please enter 1, 2, or 3.")
        except ValueError:
            print("Invalid input. Please enter a number (1, 2, or 3).")

class Main(HiAnimeIE):
    def __init__(self):
        print(Fore.LIGHTGREEN_EX + "Anime " + Fore.LIGHTWHITE_EX + "Downloader")
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
        }
        self._downloader = YoutubeDL(ydl_opts)  # Initialize the downloader
        name_of_anime = input("Enter Name of Anime: ")
        url = "https://hianime.to/search?keyword=" + name_of_anime
        webpage = self._download_webpage(url, None)
        anime_elements=get_elements_html_by_class('flw-item',webpage)
        if not anime_elements:
            print("No anime found")
            return
        # MAKE DICT WITH ANIME TITLES
        dict_with_anime_elements = {}
        for i, element in enumerate(anime_elements, 1):
            name_of_anime=(clean_html(get_element_by_class('film-name',element)))
            url_of_anime="https://hianime.to/" + (re.search(r'href="/watch/([^"]+)"', element)).group(1)
            try:
                sub_episodes_available=(clean_html(get_element_by_class('tick-item tick-sub',element)))
            except ValueError:
                sub_episodes_available = 0
            try:    
                dub_episodes_available=(clean_html(get_element_by_class('tick-item tick-dub',element)))
            except ValueError:
                dub_episodes_available = 0
            dict_with_anime_elements[i] = {
                'name': name_of_anime,
                'url': url_of_anime,
                'sub_episodes': int(sub_episodes_available),
                'dub_episodes': int(dub_episodes_available)
            }
        # PRINT ANIME TITLES TO THE CONSOLE
        for i, el in dict_with_anime_elements.items():
            print(
                Fore.LIGHTRED_EX + str(i) + ": " + Fore.LIGHTCYAN_EX + el['name'] + Fore.WHITE + " | " + "Episodes: " +
                Fore.LIGHTYELLOW_EX + str(
                    el['sub_episodes']) + Fore.LIGHTWHITE_EX + " SUB" + Fore.LIGHTGREEN_EX + " / " +
                Fore.LIGHTYELLOW_EX + str(el['dub_episodes']) + Fore.LIGHTWHITE_EX + " DUB")
        # USER SELECTS ANIME
        while True:
            try:
                number_of_anime = int(input("\nSelect an anime you want to download: "))
                if number_of_anime in dict_with_anime_elements:
                    chosen_anime_dict = dict_with_anime_elements[number_of_anime]
                    break
                else:
                    print("Invalid anime number. Please select a valid anime.")
            except ValueError:
                print("Invalid input. Please enter a valid number.")
        # Display chosen anime details
        print("\nYou have chosen " + Fore.LIGHTCYAN_EX + chosen_anime_dict['name'] + Fore.LIGHTWHITE_EX)
        print(f"URL: {chosen_anime_dict['url']}")
        print("SUB Episodes: " + Fore.LIGHTYELLOW_EX + str(chosen_anime_dict['sub_episodes']) + Fore.LIGHTWHITE_EX)
        print("DUB Episodes: " + Fore.LIGHTYELLOW_EX + str(chosen_anime_dict['dub_episodes']) + Fore.LIGHTWHITE_EX)
        download_type = 'SUB'
        if chosen_anime_dict['dub_episodes'] != 0 and chosen_anime_dict['sub_episodes'] != 0:
            download_type = input(
                "\nBoth SUB and DUB episodes are available. Do you want to download SUB or DUB? (Enter 'SUB' or 'DUB'): ").strip().upper()
            while download_type not in ['SUB', 'DUB']:
                print("Invalid choice. Please enter 'SUB' or 'DUB'.")
                download_type = input(
                    "\nBoth SUB and DUB episodes are available. Do you want to download SUB or DUB? (Enter 'SUB' or 'DUB'): ").strip().upper()
        elif chosen_anime_dict['dub_episodes'] == 0:
            print("Dub episodes are not available. Defaulting to SUB.")
        else:
            print("Sub episodes are not available. Defaulting to DUB.")
            download_type = "DUB"
        # Get starting and ending episode numbers
        if chosen_anime_dict[f"{download_type.strip().lower()}_episodes"] != "1":
            start_episode = get_episode_input("Enter the starting episode number: ", 1,
                                              chosen_anime_dict[f"{download_type.strip().lower()}_episodes"])
            end_episode = get_episode_input("Enter the ending episode number: ", start_episode,
                                            chosen_anime_dict[f"{download_type.strip().lower()}_episodes"])
        else:
            start_episode = 1
            end_episode = 1
        format = download_type+choose_resolution()
        params = {
                    'playliststart': start_episode,
                    'playlistend': end_episode,
                    'format': format,
                    'outtmpl': os.path.join(chosen_anime_dict['name'],'%(series)s - Episode %(episode_number)s - %(episode)s.%(ext)s'),
                    'postprocessors': [{'already_have_subtitle': False,
                                        'key': 'FFmpegEmbedSubtitle'},
                                        {'add_chapters': True,
                                        'add_infojson': 'if_exists',
                                        'add_metadata': True,
                                        'key': 'FFmpegMetadata'}],
                    'subtitleslangs': ['all'],
                    'writesubtitles': True
                }
        with YoutubeDL(params) as ytdl:
            ytdl.add_info_extractor(HiAnimeIE())
            ytdl_info = ytdl.extract_info(chosen_anime_dict['url'], download=True, ie_key=HiAnimeIE.ie_key())
        input(Fore.WHITE + "\nPress any key to" + Fore.LIGHTRED_EX +" Exit" + Fore.WHITE + "...")

if __name__ == "__main__":
    Main()