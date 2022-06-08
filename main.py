import requests
import logging as log
import pygame

from time import sleep


API_ENDPOINT = 'https://sirens.in.ua/api/v1/'

NEGATIVE_RESPONSES = [None, 'no_data']
POSITIVE_RESPONSES = ['full', 'partial']

SIREN_FILENAME = 'siren.mp3'


def init_logger():
    log.basicConfig(format='%(asctime)s %(message)s', datefmt='[%d/%m/%Y %H:%M:%S] ', level=log.INFO)


def init_soundplayer():
    pygame.mixer.init()
    pygame.mixer.music.load(SIREN_FILENAME)


class UkraineSirenAPI:
    url: str

    def __init__(self, url) -> None:
        self.url = url
    
    def get_siren_status(self) -> dict:
        response = requests.get(self.url)
        if response.status_code == 200:
            return response.json()
        else:
            log.warning(f'Failed to get new siren status (code: {response.status_code})')
            return dict()


class UkraineSirenObserver:
    api: UkraineSirenAPI
    region_status: dict

    def __init__(self, api: UkraineSirenAPI) -> None:
        self.api = api
        self.region_status = dict()
    
    def update_status(self) -> None:
        try:
            new_data = self.api.get_siren_status()
            self.region_status.update(new_data)
        except Exception as e:
            log.exception(f'Failed to get new siren status')
    
    def get_active_siren_regions(self) -> list:
        return [region for region in self.region_status if self.region_status.get(region) in POSITIVE_RESPONSES]

    
def main():
    init_logger()

    log.info('Initializing sound player')
    init_soundplayer()

    api = UkraineSirenAPI(API_ENDPOINT)
    observer = UkraineSirenObserver(api)

    log.info('Starting region siren observer')
    while True:
        observer.update_status()
        regions = observer.get_active_siren_regions()

        if regions:
            log.info(f'One or more regions have an active siren alert ({regions})')
            log.info('Playing siren alert...')
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy() is True:
                continue
        else:
            log.info('No regions have an active siren alert')

        log.info('Waiting 10 seconds until updating region status')
        sleep(10) #  Always wait 10 seconds before updating state

        # Can also do when a new alert pops up
        # Pronounce name?


if __name__ == '__main__':
    main()
