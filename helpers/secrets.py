import configparser
import os


class Secrets:
    """
    Save secret user information in an ini file
    """

    def __init__(self, file_path):
        self.secrets = None
        self.file_path = file_path

    def create_file_if_not_exists(self):
        """
        Creates secrets file if it doesn't exist
        :return:
        """

        if not os.path.isfile(self.file_path):
            open(self.file_path, 'w').close()

    def load_file(self):
        """
        Loads secrets file if not yet loaded
        :return:
        """

        # Nothing to do if secrets are already loaded
        if self.secrets is None:
            # In case the file doesn't exist, we create it first
            self.create_file_if_not_exists()

            # Load the ini file
            self.secrets = configparser.ConfigParser()
            self.secrets.read(self.file_path)

    def save_file(self):
        """
        Save the file on the disk
        :return:
        """
        # Load the secrets file
        self.load_file()

        # Save file on the disk
        with open(self.file_path, 'w') as secrets_file:
            self.secrets.write(secrets_file)

    def get(self, section, key):
        """
        Return a specific secret identified by its key in a section
        :param section: section containing the secret
        :param key: secret identifier
        :return: String: secret value or None if it doesn't exists
        """

        # Load the secrets file
        self.load_file()

        # Check that the section exists
        if not self.has_section(section):
            return None

        # Return requested secret
        return self.secrets[section].get(key)

    def put(self, section, key, value):
        """
        Save a specific secret identified by its key in a section
        :param section: section containing the secret
        :param key: secret identifier
        :return:
        """

        # Load the secrets file
        self.load_file()

        # Create secret section if it doesn't exists
        if section not in self.secrets:
            self.secrets[section] = {}

        # Save secret
        self.secrets[section][key] = value

    def has_section(self, section):
        """
        Check that the file contain a specific section
        :param section: section identifier
        :return: True if the file contains the section
        """

        # Load the secrets file
        self.load_file()

        return section in self.secrets
