import json
import logging
import sys
import time
import os
import instagram
import tarfile

def saveJSON(timestamp: int, type: str, content: dict):
    """Save JSON file

    Args:
        timestamp: Unix timestamp
        type: Name
        content: JSON data

    Returns:
        None
    """
    dirpath = os.getcwd()
    path = os.path.join(dirpath, "json", str(timestamp) + "_" + type + ".json")
    dirpath = os.path.dirname(path)
    os.makedirs(dirpath, exist_ok=True)
    with open(path, "tx") as f:
        json.dump(content, f)

def main():
    """ Main function

    Returns:
        None
    """
    configfile = "config.json"
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

    try:
        logging.info("Opening config file.")
        with open(configfile, "tr") as f:
            config = json.load(f)
    except FileNotFoundError:
        logging.info("File not found.")
        logging.info("Creating new config file.")
        config = {
            "ds_user_id": "",
            "sessionid": "",
            "csrftoken": "",
            "mid": "",
        }
        with open(configfile, "tx+") as f:
            json.dump(config, f)

    # Insert error checking to see if config is valid and works

    logging.info("Initialize IG interface.")
    ig = instagram.Instagram(config)
    logging.info("Get story tray.")
    traytime = int(time.time())
    storyresp = ig.getStories()
    storyjson = storyresp.json()
    saveJSON(traytime, "tray", storyjson)

    logging.info("Downloading story tray.")
    # Replace 'your_target_user_id' with the actual user ID you want to download
    target_user_id = 'your_target_user_id'
    ig.downloadTray(storyjson, target_user_id)
    users = ig.getUserIDs(storyjson)
    for user in users:
        reeltime = int(time.time())
        uresp = ig.getUserStories(user)
        ujson = uresp.json()
        saveJSON(reeltime, "reel_" + str(user), ujson)
        ig.downloadReel(ujson, target_user_id)

    logging.info("Downloading post-live stories.")
    ig.downloadStoryLive(storyjson, target_user_id)

    logging.info("Collecting list of JSON objects.")
    jsonlist = []
    for file in os.listdir("json"):
        if file.endswith(".json"):
            jsonlist.append(os.path.join("json", file))

    logging.info("Creating tar.xz file of JSON objects.")
    path = os.path.join(os.getcwd(), "json", str(traytime) + ".tar.xz")
    with tarfile.open(path, "x:xz") as tar:
        for path in jsonlist:
            tar.add(path)

    logging.info("Removing old JSON objects.")
    for path in jsonlist:
        os.remove(path)

    logging.info("Done.")

if __name__ == "__main__":
    main()
