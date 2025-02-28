"""
This module defines the ContainerManager class for managing Docker containers in CTFd.
"""

import atexit
import time
import json
import docker
import paramiko.ssh_exception
import requests
import random

from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers import SchedulerNotRunningError

from CTFd.models import db

from .models import ContainerInfoModel

class ContainerException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self) -> str:
        if self.message:
            return self.message
        else:
            return "Unknown Container Exception"

class ContainerManager:
    def __init__(self, settings, app):
        self.settings = settings
        self.client = None
        self.app = app
        if settings.get("docker_base_url") is None or settings.get("docker_base_url") == "":
            return

        try:
            self.initialize_connection(settings, app)
        except ContainerException:
            print("Docker could not initialize or connect.")
            return

    # ... (keep other methods unchanged)

    @run_command
    def create_container(self, image: str, port_range_start: int, port_range_end: int, command: str, volumes: str):
        """
        Create a new Docker container with port range mapping.
        """
        kwargs = {}

        # Set memory and CPU limits
        if self.settings.get("container_maxmemory"):
            try:
                mem_limit = int(self.settings.get("container_maxmemory"))
                if mem_limit > 0:
                    kwargs["mem_limit"] = f"{mem_limit}m"
            except ValueError:
                raise ContainerException("Configured container memory limit must be an integer")

        if self.settings.get("container_maxcpu"):
            try:
                cpu_period = float(self.settings.get("container_maxcpu"))
                if cpu_period > 0:
                    kwargs["cpu_quota"] = int(cpu_period * 100000)
                    kwargs["cpu_period"] = 100000
            except ValueError:
                raise ContainerException("Configured container CPU limit must be a number")

        # Handle volumes
        if volumes is not None and volumes != "":
            try:
                volumes_dict = json.loads(volumes)
                kwargs["volumes"] = volumes_dict
            except json.decoder.JSONDecodeError:
                raise ContainerException("Volumes JSON string is invalid")

        # Create port mappings for the range
        ports = {}
        for port in range(port_range_start, port_range_end + 1):
            ports[str(port)] = None

        try:
            return self.client.containers.run(
                image,
                ports=ports,
                command=command,
                detach=True,
                auto_remove=True,
                **kwargs
            )
        except docker.errors.ImageNotFound:
            raise ContainerException("Docker image not found")

    @run_command
    def get_container_ports(self, container_id: str) -> dict:
        """
        Get all mapped ports for a container.

        Args:
            container_id (str): The ID of the container.

        Returns:
            dict: A dictionary mapping internal ports to external ports.
        """
        try:
            container = self.client.containers.get(container_id)
            port_mappings = {}
            
            for internal_port, mappings in container.ports.items():
                if mappings:
                    # Remove the '/tcp' or '/udp' from the internal port
                    clean_internal_port = internal_port.split('/')[0]
                    port_mappings[clean_internal_port] = mappings[0]["HostPort"]
            
            return port_mappings
        except Exception as e:
            raise ContainerException(f"Failed to get container ports: {str(e)}")

    # ... (keep other methods unchanged)
