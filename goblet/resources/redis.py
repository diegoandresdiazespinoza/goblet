from goblet.deploy import create_cloudfunction, destroy_cloudfunction

from goblet.config import GConfig
import logging

from goblet.resources.infrastructure import Infrastructure
from goblet.client import get_default_project, get_default_location
from goblet.utils import get_python_runtime

log = logging.getLogger("goblet.deployer")
log.setLevel(logging.INFO)


class Redis(Infrastructure):
    """Redis Deployment
    https://cloud.google.com/memorystore/docs/redis/connect-redis-instance-functions#python_1

    Only one redis instance is supported per function
    """

    resource_type = "redis"
    valid_backends = ["cloudrun", "cloudfunction"]

    def __init__(
        self, name, versioned_clients=None, resources=None
    ):
        super(Redis, self).__init__(
            name,
            versioned_clients=versioned_clients,
            resources=resources,
        )
        self.resources = resources or {}

    def get(self):
        resp = self.versioned_clients.redis.execute("get", parent_key="name", parent_schema=f"projects/{get_default_project()}/locations/{get_default_location()}/instances/{self.name}")
        return resp

    def _deploy(self,entrypoint=None, config={}):
        if not self.resources:
            return

        log.info("deploying redis......")
        config = GConfig()
        redis_configs = config.redis or {}
        req_body = {
            "name": f"projects/{get_default_project()}/locations/{get_default_location()}/instances/{self.name}",
            "tier": "BASIC", # Default,
            "memorySizeGb": "1", #Default
            **self.resources["kwargs"],
            **redis_configs,
        }
        resp = self.versioned_clients.redis.execute("create", params={
            "instanceId": self.name, "body": req_body
        })
        self.versioned_clients.redis.wait_for_operation(resp["name"], calls="projects.locations.operations")

    def destroy(self):
        if not self.resources:
            return
        resp = self.versioned_clients.redis.execute("delete", parent_key="name", parent_schema=f"projects/{get_default_project()}/locations/{get_default_location()}/instances/{self.name}")
        self.versioned_clients.redis.wait_for_operation(resp["name"], calls="projects.locations.operations")

    def update_config(self):
        """
        Pass relevent environment variables to functions deploy config.
        """
        instance = self.get()
        return {
            "environmentVariables": {
                "REDISHOST":instance["host"],
                "REDISPORT": instance["port"]
            }
        }