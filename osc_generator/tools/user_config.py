import os
import warnings
import json

class UserConfig:
    """
    class for user defined configurations
    """

    def __init__(self, path):
        self.path_to_config: str = path
        self.catalogs = None
        self.object_boundingbox = None
        self.bbcenter_to_rear = None


    def read_config(self):
        """
        read config file and store relevant information
        """
        try:
            with open(os.path.join(self.path_to_config, 'user_config.json'), 'r') as config_file:
                data = json.load(config_file)

                if "moving_objects" in data:
                    objects = data["moving_objects"]
                    object_bb = []
                    object_bbcenter = []
                    for bb in objects:
                        if "boundingbox" in bb:
                            object_bb.append(bb["boundingbox"])
                        else:
                            object_bb.append(None)
                        if "bbcenter_to_rear" in bb:
                            object_bbcenter.append(bb["bbcenter_to_rear"])
                        else:
                            object_bbcenter.append(None)

                    self.object_boundingbox = object_bb
                    self.bbcenter_to_rear = object_bbcenter

                if "catalogs" in data:
                    self.catalogs = data["catalogs"]

        except FileNotFoundError:
            warnings.warn("User configuration file unavailable/not provided. "
                          "Default object values will be used", UserWarning)

    def write_config(self):
        """
        write config file from relevant information
        """
        config_data = {}
        if self.object_boundingbox is not None and self.bbcenter_to_rear is not None:
            config_data["moving_objects"] = [{'boundingbox': self.object_boundingbox[i],
                                              'bbcenter_to_rear': self.bbcenter_to_rear[i]}
                                             for i in range(len(self.object_boundingbox))]
        if self.catalogs is not None:
            config_data["catalogs"] = self.catalogs

        if config_data:
            try:
                with open(os.path.join(self.path_to_config, 'user_config.json'), 'w') as config_file:
                    json.dump(config_data, config_file, indent=4)
            except:
                warnings.warn("Unable to write config file", UserWarning)
