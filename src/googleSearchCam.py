from typing import ClassVar, Mapping, Sequence, Any, Dict, Optional, Tuple, Final, List, cast
from typing_extensions import Self

from typing import Any, Dict, Final, List, NamedTuple, Optional, Tuple, Union

from PIL import Image

from viam.media.video import NamedImage
from viam.proto.common import ResponseMetadata

from viam.module.types import Reconfigurable
from viam.proto.app.robot import ComponentConfig
from viam.proto.common import ResourceName
from viam.resource.base import ResourceBase
from viam.resource.types import Model, ModelFamily
from viam.components.component_base import ValueTypes

from viam.components.camera import Camera, ViamImage
from viam.media.utils.pil import pil_to_viam_image

from viam.logging import getLogger
from viam.errors import ViamError, NotSupportedError
from viam.media.video import CameraMimeType

import os
import requests
from io import BytesIO

LOGGER = getLogger(__name__)

class googleSearchCam(Camera, Reconfigurable):

    class Properties(NamedTuple):
        supports_pcd: bool = False
        intrinsic_parameters = None
        distortion_parameters = None

    MODEL: ClassVar[Model] = Model(ModelFamily("mcvella", "camera"), "google-image-search")
    
    camera_properties: Camera.Properties = Properties()
    # will store current get_image index for a given directory here
    query_index: dict
    query: str = ''
    google_api_key: str = ''
    google_search_engine_id: str = ''
    max_index: int = 200

    # Constructor
    @classmethod
    def new(cls, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]) -> Self:
        my_class = cls(config.name)
        my_class.reconfigure(config, dependencies)
        return my_class

    # Validates JSON Configuration
    @classmethod
    def validate(cls, config: ComponentConfig):
        query = config.attributes.fields["query"].string_value or ''
        if query == '':
            raise Exception("'query' is a required attribute")
        google_api_key = config.attributes.fields["google_api_key"].string_value or ''
        if google_api_key == '':
            raise Exception("'google_api_key' is a required attribute")
        google_search_engine_id = config.attributes.fields["google_search_engine_id"].string_value or ''
        if google_search_engine_id == '':
            raise Exception("'google_search_engine_id' is a required attribute")
        return

    # Handles attribute reconfiguration
    def reconfigure(self, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]):
        self.query_index = {}
        self.query = config.attributes.fields["query"].string_value
        self.google_api_key = config.attributes.fields["google_api_key"].string_value
        self.google_search_engine_id = config.attributes.fields["google_search_engine_id"].string_value
        return
    
    async def get_image(
        self, mime_type: str = "", *, extra: Optional[Dict[str, Any]] = None, timeout: Optional[float] = None, **kwargs
    ) -> ViamImage:
        if extra.get('query') != None:
            self.query = extra.get('query')
        
        image_index: int
        if extra.get('index') != None:
            image_index = extra['index']
        if extra.get('index_jog') != None:
            image_index = self._jog_index(extra['index_jog'], self.query)
        elif self.query_index.get(self.query) != None:
            image_index = self.query_index[self.query]
        else:
            image_index = 0
    
        # Use Google search to get metadata
        search_uri = f"https://www.googleapis.com/customsearch/v1?key={self.google_api_key}&searchType=image&q={self.query}&num=1&start={image_index}&cx={self.google_search_engine_id}"
        meta = requests.get(search_uri)
        LOGGER.debug(self.query_index.get(self.query))
        LOGGER.debug(meta.json()['items'][0]['link'])

        # increment for next get_image() call
        self.query_index[self.query] = image_index + 1
        if self.query_index[self.query] > self.max_index:
            self.query_index[self.query] = 0

        r = requests.get(meta.json()['items'][0]['link'])
        img = Image.open(BytesIO(r.content))

        
        return pil_to_viam_image(img.convert('RGB'), CameraMimeType.JPEG)
    
    def _jog_index(self, index_jog, requested_dir):
        requested_index = self.directory_index[requested_dir] + index_jog
        max_index = self.max_index
        if requested_index < 0:
            return max_index - requested_index
        elif requested_index > max_index:
            return requested_index - max_index - 1

    async def get_images(self, *, timeout: Optional[float] = None, **kwargs) -> Tuple[List[NamedImage], ResponseMetadata]:
        raise NotImplementedError()

    async def get_point_cloud(
        self, *, extra: Optional[Dict[str, Any]] = None, timeout: Optional[float] = None, **kwargs
    ) -> Tuple[bytes, str]:
        raise NotImplementedError()

    # Implements the do_command which will respond to a map with key "request"
    async def do_command(self, command: Mapping[str, ValueTypes], *,
                         timeout: Optional[float] = None,
                         **kwargs) -> Mapping[str, ValueTypes]:
        ret = {}
        if command.get('set') != None:
            setDict = command.get('set')
            if setDict.get('query') != None:
                self.query = setDict.get('query')
            if setDict.get('index') != None:
                if isinstance(setDict['index'], int):
                    self.query_index[self.query] = setDict['index']
            if setDict.get('index_jog') != None:
                index = self._jog_index(setDict['index_jog'], self.query)
                self.query_index[self.query] = index
                ret = { "index" : index }
        return ret
    
    async def get_properties(self, *, timeout: Optional[float] = None, **kwargs) -> Properties:
       return self.camera_properties

