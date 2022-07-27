import logging

from goblet.client import VersionedClients, get_default_location, get_default_project

log = logging.getLogger("goblet.deployer")
log.setLevel(logging.INFO)


class Infrastructure:
    """Base Infrastructure class"""

    resources = None
    resource_type = ""
    can_sync = False

    def __init__(
        self,
        name,
        versioned_clients: VersionedClients = None,
        resources=None
    ):
        self.name = name
        self.resources = resources or {}
        self.versioned_clients = versioned_clients or VersionedClients()


    def register_instance(self, name, kwargs):
        self.resources={
            "name": name,
            "kwargs": kwargs or {}
        }

    def deploy(self, sourceUrl=None, entrypoint=None, config={}):
        self._deploy(sourceUrl, entrypoint, config=config)

    def _deploy(self, sourceUrl=None, entrypoint=None, config={}):
        raise NotImplementedError("deploy")

    def destroy(self):
        raise NotImplementedError("destroy")

    def sync(self, dryrun=False):
        if self.can_sync:
            log.info(f"syncing {self.resource_type}")
            self._sync(dryrun)

    def _sync(self, dryrun=False):
        pass

    def __add__(self, other):
        if other.resources:
            self.resources.update(other.resources)
        return self

    def update_config(self, write_to_config=True):
        """
        Pass relevent environment variables to functions deploy config.
        Default will update config.json
        """
        pass 