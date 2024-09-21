# openapi_client.ComponentApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**act**](ComponentApi.md#act) | **POST** /act | 
[**answer_question**](ComponentApi.md#answer_question) | **POST** /question | 
[**get_available_actions**](ComponentApi.md#get_available_actions) | **GET** /availbale/actions | 
[**upload_document**](ComponentApi.md#upload_document) | **POST** /documents | 


# **act**
> str act(body)



### Example


```python
import openapi_client
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.ComponentApi(api_client)
    body = 'body_example' # str | 

    try:
        api_response = api_instance.act(body)
        print("The response of ComponentApi->act:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ComponentApi->act: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | **str**|  | 

### Return type

**str**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Done |  -  |
**500** | Something Somewhere went terribly wrong. |  -  |
**501** | Not available for this component. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **answer_question**
> ChatResponse answer_question(body)



### Example


```python
import openapi_client
from openapi_client.models.chat_response import ChatResponse
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.ComponentApi(api_client)
    body = 'body_example' # str | 

    try:
        api_response = api_instance.answer_question(body)
        print("The response of ComponentApi->answer_question:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ComponentApi->answer_question: %s\n" % e)
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

# **get_available_actions**
> List[KeyValue] get_available_actions()



### Example


```python
import openapi_client
from openapi_client.models.key_value import KeyValue
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.ComponentApi(api_client)

    try:
        api_response = api_instance.get_available_actions()
        print("The response of ComponentApi->get_available_actions:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ComponentApi->get_available_actions: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**List[KeyValue]**](KeyValue.md)

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
import openapi_client
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.ComponentApi(api_client)

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
**422** | Unsupoorted document |  -  |
**501** | Not available for this componment |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

