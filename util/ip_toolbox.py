"""
File: ip_toolbox.py
Author: Chuncheng Zhang
Date: 2024-10-17
Copyright & Email: chuncheng.zhang@ia.ac.cn

Purpose:
    The toolbox for the ip address and location query.

Functions:
    1. Requirements and constants
    2. Function and class
    3. Play ground
    4. Pending
    5. Pending
"""


# %% ---- 2024-10-17 ------------------------
# Requirements and constants
import io
import json
import requests

from PIL import Image
from pathlib import Path
from loguru import logger


# %% ---- 2024-10-17 ------------------------
# Function and class
class IpToolbox(object):
    pwd = Path(__file__).parent

    mapbox_access_token = open(pwd.joinpath('.mapboxtoken')).read()
    headers = json.loads(open(pwd.joinpath('headers.json')).read())
    proxies = json.loads(open(pwd.joinpath('proxy.json')).read())

    def get_ip_address(self, use_proxy: bool = False):
        '''
        Get my IP or the VPN IP address.

            url = 'https://checkip.amazonaws.com/'

        Args:
            use_proxy: bool. Whether to use the proxy.

        Returns:
            The IP address or the VPN IP address.
        '''
        url = 'https://checkip.amazonaws.com/'
        if use_proxy:
            resp = requests.get(url, proxies=self.proxies)
        else:
            resp = requests.get(url)
        address = resp.content.decode().strip()
        if use_proxy:
            logger.debug(f'Got ip address: {address}, proxy: {self.proxies}')
        else:
            logger.debug(f'Got ip address: {address}, without proxy')
        return address

    def get_location(self, ip_address: str):
        '''
        Get the location of the ip_address.

            url = f'http://ip-api.com/json/{ip_address}'

        Args:
            ip_address: str. The IP address, like 108.181.24.77

        Returns:
            The dict of the location information, for example
            {
                'status': 'success',
                'country': 'United States',
                'countryCode': 'US',
                'region': 'CA',
                'regionName': 'California',
                'city': 'Los Angeles',
                'zip': '90060',
                'lat': 34.0544,
                'lon': -118.2441,
                'timezone': 'America/Los_Angeles',
                'isp': 'Psychz Networks',
                'org': 'TELUS Communications Inc.',
                'as': 'AS40676 Psychz Networks',
                'query': '108.181.24.77'
            }
        '''
        url = f'http://ip-api.com/json/{ip_address}'
        resp = requests.get(url)
        obj = json.loads(resp.content)
        logger.debug(f'Got location {obj} from {url}')
        return obj

    def get_img(self, lat: float, lon: float, zoom: int = 3, width: int = 600, height: int = 600):
        '''
        Get image from mapbox
            Reference: https://docs.mapbox.com/api/maps/static-images/
            Template: https://api.mapbox.com/styles/v1/{username}/{style_id}/static/{overlay}/{lon},{lat},{zoom},{bearing},{pitch}|{bbox}|{auto}/{width}x{height}{@2x}

        Args:
            lat: float, The latitude of the center.
            lon: float, The longitude of the center.
            zoom: int, The zoom level of the image.

        Returns:
            The received image.
        '''
        token = f'access_token={self.mapbox_access_token}'
        url = f"https://api.mapbox.com/styles/v1/mapbox/streets-v12/static/{lon},{
            lat},{zoom},20/{width}x{height}?{token}"
        logger.debug(f'Requesting {url}')
        try:
            resp = requests.get(url, headers=self.headers,
                                stream=True, timeout=3)
            buf = io.BytesIO(resp.content)
            img = Image.open(buf)
            logger.debug(f'Got {img} from {url}')
        except:
            logger.error('Failed got img')
            img = Image.open(
                self.pwd.joinpath('world map.jpg')).resize((width, height))
        return img

# %% ---- 2024-10-17 ------------------------
# Play ground


# %% ---- 2024-10-17 ------------------------
# Pending


# %% ---- 2024-10-17 ------------------------
# Pending
