import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import logging
import os
from datetime import datetime
try:
    import defusedxml.minidom as xml
except ImportError:
    import xml.dom.minidom as xml

class Instagram:
    def __init__(self, cookie):
        """This sets up this class to communicate with Instagram.

        Args:
            cookie: A dictionary object with the required cookie values (ds_user_id, sessionid, csrftoken).
        """
        # ... (existing code)

    def downloadReel(self, resp, target_user_id):
        """Download stories of a followed user's tray.

        Download the stories of a followed user.

        Args:
            resp: JSON dictionary of reel from IG API
            target_user_id: User ID of the specific user to download

        Returns:
            None
        """
        try:
            for index, item in enumerate(resp['items']):
                logging.debug('    ' + str(index))
                user_id = item['user']['pk']

                # Check if the current story belongs to the target user
                if user_id != target_user_id:
                    continue

                username = item['user']['username']
                timestamp = item['taken_at']
                postid = item['id']
                mediatype = item['media_type']
                if mediatype == 2:  # Video
                    # ... (existing code)
                elif mediatype == 1:  # Image
                    # ... (existing code)
                else:  # Unknown
                    # ... (existing code)

                path = self.formatPath(username, user_id, timestamp, postid, mediatype)
                self.getFile(url, path)
        except KeyError:  # JSON 'item' key does not exist for later items in tray as of 6/2/2017
            pass

    def downloadTray(self, resp, target_user_id):
        """Download stories of logged in user's tray.

        Download the stories as available in the tray. The tray contains a list of
        reels, a collection of the stories posted by a followed user.

        The tray only contains a small set of reels of the first few users. To download
        the rest, a reel must be obtained for each user in the tray.

        Args:
            resp: JSON dictionary of tray from IG API
            target_user_id: User ID of the specific user to download

        Returns:
            None
        """
        for reel in resp['tray']:
            self.downloadReel(reel, target_user_id)

    def downloadStoryLive(self, resp, target_user_id):
        """Download post-live stories of a followed user's tray.

        Download the post-live stories of a followed user.

        Args:
            resp: JSON dictionary of reel from IG API
            target_user_id: User ID of the specific user to download

        Returns:
            None
        """
        try:
            for index, item in enumerate(resp["post_live"]["post_live_items"]):
                logging.debug('    ' + str(index))
                user_id = item["user"]["pk"]

                # Check if the current live story belongs to the target user
                if user_id != target_user_id:
                    continue

                username = item["user"]["username"]
                timestamp = item["broadcasts"][0]["published_time"]
                postid = item["broadcasts"][0]["media_id"]
                dash = item["broadcasts"][0]["dash_manifest"]
                dashxml = xml.parseString(dash)
                elements = dashxml.getElementsByTagName("BaseURL")
                for eindex, element in enumerate(elements):
                    for node in element.childNodes:
                        if node.nodeType == node.TEXT_NODE:
                            url = node.data
                            mediatype = 3
                            path = self.formatPath(username, user_id, timestamp, postid + "_" + str(eindex), mediatype)
                            self.getFile(url, path)
        except KeyError:  # No "post_live" key
            logging.debug('    ' + 'No live stories.')

    # ... (existing code)

# Example usage:
# Provide your Instagram cookie as a dictionary
cookie = {
    "ds_user_id": "your_user_id",
    "sessionid": "your_session_id",
    "csrftoken": "your_csrf_token",
    "mid": "your_mid"
}

# Create an instance of the Instagram class with the target user ID
instagram_instance = Instagram(cookie)

# Get the reel tray
reel_tray_response = instagram_instance.getReelTray()

# Replace 'your_target_user_id' with the actual user ID you want to download
target_user_id = 'your_target_user_id'

# Download stories of the target user's tray
instagram_instance.downloadTray(reel_tray_response.json(), target_user_id)

# Download post-live stories of the target user's tray
instagram_instance.downloadStoryLive(reel_tray_response.json(), target_user_id)

# Close the Instagram session
instagram_instance.close()
