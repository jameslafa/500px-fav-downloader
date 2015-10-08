import os

import requests


class FileSaver:
    """
    Save a file to different storages
    """

    # For the moment we only support disk, dropbox will come soon
    SUPPORTED_STORAGE_TYPES = ['disk']

    def __init__(self, storage_type, disk_storage_path=None):
        """
        Build a FileSaver instance
        :param storage_type: disk is the only available value for the moment
        :param disk_storage_path: directory path where files will be saved
        """

        # Validate the storage_type is supported
        if storage_type not in self.SUPPORTED_STORAGE_TYPES:
            raise AttributeError(str(storage_type) + ' is not a supported storage_type')

        self.storage_type = storage_type
        self.disk_storage_path = disk_storage_path

    def save_image_from_url(self, url, photo_id):
        """
        Download an image from an url and save it
        :param url: url of the image to download
        :param photo_id: id of the picture, used for the file name
        :return:
        """

        # Download file from url
        r = requests.get(url, stream=True)

        # If the response is OK
        if r.status_code == 200:

            if self.storage_type == 'disk':

                # Create the directory on the disk if it doesn't exists
                if not os.path.isdir(self.disk_storage_path):
                    os.mkdir(self.disk_storage_path)

                # Define file_path where the file will be stored
                # TODO: extension shouldn't be hardcoded
                file_path = os.path.join(self.disk_storage_path, str(photo_id) + '.jpg')

                # Save image on the disk
                with open(file_path, 'wb') as f:
                    for chunk in r.iter_content(1024):
                        f.write(chunk)
        else:
            raise RuntimeError("Couldn't download the image")
