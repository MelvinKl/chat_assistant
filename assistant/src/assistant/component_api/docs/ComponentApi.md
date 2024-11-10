# assistant.component_api.ComponentApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**assist**](ComponentApi.md#assist) | **POST** /assist | 
[**get_description**](ComponentApi.md#get_description) | **GET** /description | 
[**upload_document**](ComponentApi.md#upload_document) | **POST** /documents | 


# **assist**
> ChatResponse assist(body)



### Example


```python
import assistant.component_api
from assistant.component_api.models.chat_response import ChatResponse
from assistant.component_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = assistant.component_api.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with assistant.component_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = assistant.component_api.ComponentApi(api_client)
    body = 'body_example' # str | 

    try:
        api_response = api_instance.assist(body)
        print("The response of ComponentApi->assist:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ComponentApi->assist: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | **str**|  | 

### Return type

[**ChatResponse**](ChatResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Answer |  -  |
**404** | Couldn&#39;t answer your question. |  -  |
**500** | Something somewhere went terribly wrong. |  -  |
**501** | Doesn&#39;t exist for this component |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_description**
> Description get_description()



### Example


```python
import assistant.component_api
from assistant.component_api.models.description import Description
from assistant.component_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = assistant.component_api.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with assistant.component_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = assistant.component_api.ComponentApi(api_client)

    try:
        api_response = api_instance.get_description()
        print("The response of ComponentApi->get_description:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ComponentApi->get_description: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**Description**](Description.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Available actions |  -  |
**500** | Something somewhere went terribly wrong |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **upload_document**
> upload_document()



### Example


```python
import assistant.component_api
from assistant.component_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = assistant.component_api.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with assistant.component_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = assistant.component_api.ComponentApi(api_client)

    try:
        api_instance.upload_document()
    except Exception as e:
        print("Exception when calling ComponentApi->upload_document: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: multipart/form-data
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Uploading |  -  |
**422** | Unsuported document |  -  |
**501** | Not available for this componment |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

