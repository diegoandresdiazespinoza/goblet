from goblet.deploy import create_cloudfunction, destroy_cloudfunction

from goblet.config import GConfig
import logging

from goblet.resources.infrastructure import Infrastructure
from goblet.client import get_default_project, get_default_location
from goblet.utils import get_python_runtime

log = logging.getLogger("goblet.deployer")
log.setLevel(logging.INFO)


class VPCConnector(Infrastructure):
    """VPCConnector Deployment
    https://cloud.google.com/memorystore/docs/redis/connect-redis-instance-functions#python_1

    Only one vpcconnector is supported per function
    """

    resource_type = "vpcconnector"
    valid_backends = ["cloudrun", "cloudfunction"]

    def __init__(
        self, name, versioned_clients=None, resources=None
    ):
        super(VPCConnector, self).__init__(
            name,
            versioned_clients=versioned_clients,
            resources=resources,
        )
        self.resources = resources or {}

    def _deploy(self,entrypoint=None, config={}):
        if not self.resources:
            return

        log.info("deploying vpc connector......")
        config = GConfig()
        vpcconnector_configs = config.vpcconnector or {}
        req_body = {
            "name": f"projects/{get_default_project()}/locations/{get_default_location()}/connectors/{self.name}",
            "network": "default", # Default,
            "ipCidrRange": "1", #Default
            **self.resources["kwargs"],
            **vpcconnector_configs,
        }
        resp = self.versioned_clients.vpcconnector.execute("create", params={
            "connectorId": self.name, "body": req_body
        })
        self.versioned_clients.redis.wait_for_operation(resp["name"], calls="projects.locations.operations")

    def destroy(self):
        if not self.resources:
            return
        resp = self.versioned_clients.vpcconnector.execute("delete", parent_key="name", parent_schema=f"projects/{get_default_project()}/locations/{get_default_location()}/connectors/{self.name}")
        self.versioned_clients.redis.wait_for_operation(resp["name"], calls="projects.locations.operations")

    def update_config(self):
        """
        Pass relevent environment variables to functions deploy config.
        """
        return {
            "vpcConnector": f"projects/{get_default_project()}/locations/{get_default_location()}/connectors/{self.name}"
        }