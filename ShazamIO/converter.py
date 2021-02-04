from io import BytesIO

from pydub import AudioSegment

from ShazamIO.algorithm import SignatureGenerator
from ShazamIO.typehints import *
from ShazamIO.models import *
import aiohttp


class AboutTrack:
    def __init__(self, track: dict):
        self.track = track
        self.track_id = track['key']
        self.title = self.track['title']
        self.author = self.track['subtitle']
        self.photo_url = self.track['images']['coverarthq'] if 'images' in self.track else None
        self.ringtone_url = self.track['hub']['actions'][1]['uri'] if 'actions' in self.track['hub'] else None
        self.artist_id = self.track['artists'][0]['id'] if 'artists' in self.track else None
        self.shazam_url = f'https://www.shazam.com/track/{self.track_id}'

    def __str__(self):
        return (f'Author: {self.author} - {self.title}\n'
                f'Artist ID: {self.artist_id}'
                f'Shazam URL: {self.shazam_url}\n'
                f'Ringtone: {self.ringtone_url}\n'
                f'Track photo: {self.photo_url}\n')


class Converter(Request):

    @staticmethod
    def data_search(timezone: str, uri: str, samplems: int, timestamp: int) -> dict:
        return {'timezone': timezone, 'signature': {'uri': uri, 'samplems': samplems},
                'timestamp': timestamp, 'context': {}, 'geolocation': {}}

    @staticmethod
    async def city_id_from(city: CityName) -> CityID:
        async with aiohttp.ClientSession() as session:
            async with session.get(ShazamUrl.CITY_IDs_EN) as resp:
                data = await resp.json()
                for k, v in data.items():
                    if v == city:
                        return k.split('_')[2]

    @staticmethod
    def normalize_audio_data(song_data: bytes) -> AudioSegment:

        audio = AudioSegment.from_file(BytesIO(song_data))
        audio = audio.set_sample_width(2)
        audio = audio.set_frame_rate(16000)
        audio = audio.set_channels(1)

        return audio

    @staticmethod
    def create_signature_generator(audio: AudioSegment) -> SignatureGenerator:
        signature_generator = SignatureGenerator()
        signature_generator.feed_input(audio.get_array_of_samples())
        signature_generator.MAX_TIME_SECONDS = 8
        if audio.duration_seconds > 12 * 3:
            signature_generator.samples_processed += 16000 * (int(audio.duration_seconds / 16) - 6)
        return signature_generator

