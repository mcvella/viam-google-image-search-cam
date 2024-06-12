"""
This file registers the model with the Python SDK.
"""

from viam.components.camera import Camera
from viam.resource.registry import Registry, ResourceCreatorRegistration

from .googleSearchCam import googleSearchCam

Registry.register_resource_creator(Camera.SUBTYPE, googleSearchCam.MODEL, ResourceCreatorRegistration(googleSearchCam.new, googleSearchCam.validate))
