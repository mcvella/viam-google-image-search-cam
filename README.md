# google-image-search camera modular service

*google-image-search* is a Viam modular service that provides camera capabilities, using the [Google Programmable Search Engine API](https://developers.google.com/custom-search/docs/structured_search#sort-by-attribute).

The model this module makes available is *mcvella:camera:google-image-search*

## Prerequisites

You must register for a Google account and create a [programmable search engine](https://programmablesearchengine.google.com/controlpanel/all).
Record the *Search Engine ID*.
You can then get [an API key](https://developers.google.com/custom-search/v1/introduction#identify_your_application_to_google_with_api_key), which you'll also use in your module configuration.

## API

The google-image-search resource implements the [RDK camera API](https://github.com/rdk/camera-api), specifically get_image() and do_command().

### get_image

On each get_image() call, an image matching the search term will be returned, by default the next image in a Google image search result.
If it is the first get_image() call for that search term since the component was initialized, the first search result image will be returned, at which point images will be returned sequentially by [index](#index-integer).
After the last image is returned, the next get_image() call will return the image at the 0 index (start at the beginning sequentially).

The following can be passed via the *get_image()* extra parameter:

#### query (string, *required*)

The text query to search for.

#### index (integer)

If specified, return the image with this index (if it exists).
Note that the Google API used will only return up to 200 results, at which will reset to index 0.
Passing [index](#index-integer) will also reset the incremental index for [query](#query-string-required).

#### index_jog (integer)

If specified, move index by [index_jog](#index_jog-integer) and return the image at that index.
Negative integers are accepted.

Example:

```python
camera.get_image(extra={"query":"black bear","index":0}) # returns the first Google image search result for 'black bear'
camera.get_image(extra={"query":"black bear"}) # returns the second Google image search result for 'black bear'
camera.get_image(extra={"query":"black bear"}) # returns the third Google image search result for 'black bear'
camera.get_image(extra={"query":"black bear"}) # returns the fourth Google image search result for 'black bear'
camera.get_image(extra={"query":"black bear", "index_jog": -2}) # returns the third Google image search result for 'black bear'
camera.get_image(extra={"query":"black bear","index":1}) # returns the second Google image search result for 'black bear'
camera.get_image(extra={"query":"polar bear"}) # returns the first Google image search result for 'polar bear'
```

### do_command()

do_command allows [dir](#query-string), [index](#index-integer), and [index_jog](#index_jog-integer) to be set via a 'set' command.

Example:

``` python
camera.do_command({'set': {'index': 10}})
```

## Viam Service Configuration

Example attribute configuration:

```json
{
    "query": "gray fox",
    "google_search_engine_id": "abc123",
    "google_api_key": "xyz123"
}
```

### Attributes

The following attributes are available for `mcvella:camera:google-image-search` model:

| Name | Type | Inclusion | Description |
| ---- | ---- | --------- | ----------- |
| `query` | string | **Required** |  Default Google Image API search term. Can be overridden via extra params on get_image() calls. |
| `google_search_engine_id` | string | **Required** |  Google Programmable Search Engine ID |
| `google_api_key` | string | **Required** |  Google Programmable Search Engine API key |
