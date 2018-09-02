import adal
from helper_functions import *
import json
import requests
from sds_error import SdsError
from sds_type import SdsType
from sds_stream import SdsStream
import time


class SdsClient(object):
    """Handles communication with SDS Service"""
    def __init__(self, tenant, url, resource, authority, client_id,
                 client_secret):

        self.tenantId = tenant
        self.url = url
        self.resource = resource
        self.clientId = client_id
        self.clientSecret = client_secret
        self.authority = authority
        self.__token = ""
        self.__expiration = 0
        self.__get_token()
        self.__set_path_and_query_templates()
        self.type_names = []

    @property
    def uri(self):
        return self.url

    def get_or_create_type(self, namespace_id, sds_type):
        self.type_names.append(sds_type.Id)
        """Tells SDS Service to create a type based on local 'type' or get
        if existing type matches"""
        if namespace_id is None:
            raise TypeError
        if sds_type is None or not isinstance(sds_type, SdsType):
            raise TypeError

        req_url = self.url + self.__typesPath.format(
            tenant_id=self.tenantId,
            namespace_id=namespace_id,
            type_id=sds_type.Id)
        payload = sds_type.to_json()
        response = requests.post(
            url=req_url,
            data=payload,
            headers=self.__sds_headers())
        if response.status_code < 200 or response.status_code >= 300:
            response.close()
            cleanup(self, namespace_id, self.type_names)
            raise SdsError(
                "Failed to create type, {type_id}. {status}:{reason}".
                format(type_id=sds_type.Id, status=response.status_code,
                       reason=response.text))

        sds_type = SdsType.from_json(json.loads(response.content))
        response.close()
        return sds_type

    def delete_type(self, namespace_id, type_id):
        """Tells SDS Service to delete the type specified by 'type_id'"""
        if namespace_id is None:
            raise TypeError
        if type_id is None:
            raise TypeError

        response = requests.delete(
            self.url + self.__typesPath.format(tenant_id=self.tenantId,
                                               namespace_id=namespace_id,
                                               type_id=type_id),
            headers=self.__sds_headers())

        if response.status_code < 200 or response.status_code >= 300:
            response.close()
            raise SdsError("Failed to delete SdsType, "
                           "{type_id}. {status}:{reason}".
                           format(type_id=type_id,
                                  status=response.status_code,
                                  reason=response.text))
        response.close()

    def create_or_update_stream(self, namespace_id, stream):
        """Tells SDS Service to create a stream based on the local 'stream'
        SdsStream object"""
        if namespace_id is None:
            raise TypeError
        if stream is None or not isinstance(stream, SdsStream):
            raise TypeError
        req_url = self.url + self.__streamsPath.format(
            tenant_id=self.tenantId,
            namespace_id=namespace_id,
            stream_id=stream.Id)

        payload = stream.to_json()
        headers = self.__sds_headers()

        response = requests.put(
            url=req_url,
            data=payload,
            headers=headers)
        if response.status_code < 200 or response.status_code >= 300:
            response.close()
            cleanup(self, namespace_id, self.type_names)
            raise SdsError("Failed to create SdsStream, {stream_id}. "
                           "{status}:{reason}".
                           format(stream_id=stream.Id,
                                  status=response.status_code,
                                  reason=response.text))

        response.close()

    def delete_stream(self, namespace_id, stream_id):
        """Tells SDS Service to delete the stream speficied by 'stream_id'"""
        if namespace_id is None:
            raise TypeError
        if stream_id is None:
            raise TypeError

        response = requests.delete(
            self.url + self.__streamsPath.format(tenant_id=self.tenantId,
                                                 namespace_id=namespace_id,
                                                 stream_id=stream_id),
            headers=self.__sds_headers())
        if response.status_code < 200 or response.status_code >= 300:
            response.close()
            raise SdsError("Failed to delete SdsStream, {stream_id}. "
                           "{status}:{reason}".
                           format(stream_id=stream_id,
                                  status=response.status_code,
                                  reason=response.text))

        response.close()

    def get_last_value(self, namespace_id, stream_id, value_class, view_id=""):
        """Retrieves JSON object from SDS Service the last value to be added to
         the stream specified by 'stream_id'"""
        if namespace_id is None:
            raise TypeError
        if stream_id is None:
            raise TypeError
        if value_class is None:
            raise TypeError

        response = requests.get(
            self.url + self.__getLastValue.format(tenant_id=self.tenantId,
                                                  namespace_id=namespace_id,
                                                  stream_id=stream_id,
                                                  view_id=view_id),
            headers=self.__sds_headers())
        if response.status_code < 200 or response.status_code >= 300:
            response.close()
            raise SdsError("Failed to get last value for SdsStream "
                           "{stream_id}. {status}:{reason}".
                           format(stream_id=stream_id,
                                  status=response.status_code,
                                  reason=response.text))

        content = json.loads(response.content)
        response.close()
        return value_class.from_json(content)

    def get_window_values(self, namespace_id, stream_id,
                          value_class, start, end, view_id=""):
        """Retrieves JSON object representing a window of values from the
        stream specified by 'stream_id'"""
        if namespace_id is None:
            raise TypeError
        if stream_id is None:
            raise TypeError
        if value_class is None:
            raise TypeError
        if start is None:
            raise TypeError
        if end is None:
            raise TypeError

        response = requests.get(
            self.url + self.__getWindowValues.format(tenant_id=self.tenantId,
                                                     namespace_id=namespace_id,
                                                     stream_id=stream_id,
                                                     start=start,
                                                     end=end,
                                                     view_id=view_id),
            headers=self.__sds_headers())
        if response.status_code < 200 or response.status_code >= 300:
            response.close()
            raise SdsError("Failed to get window values for SdsStream "
                           "{stream_id}. {status}:{reason}".
                           format(stream_id=stream_id,
                                  status=response.status_code,
                                  reason=response.text))

        content = json.loads(response.content)
        response.close()

        values = []
        for c in content:
            values.append(value_class.from_dictionary(c))
        return values

    def update_value(self, namespace_id, stream_id, value):
        """Tells SDS Service to update the value described by 'value', a local
        SdsValue object"""
        if namespace_id is None:
            raise TypeError
        if stream_id is None:
            raise TypeError
        if value is None:
            raise TypeError

        if callable(getattr(value, "to_json", None)):
            payload = value.to_json()
        else:
            payload = value

        req_url = self.url + self.__updateValuePath.format(
            tenant_id=self.tenantId,
            namespace_id=namespace_id,
            stream_id=stream_id)

        response = requests.put(url=req_url,
                                data=payload,
                                headers=self.__sds_headers())
        if response.status_code < 200 or response.status_code >= 300:
            response.close()
            raise SdsError(
                "Failed to update value for SdsStream, {}. {}:{}".
                format(stream_id, response.status_code, response.text))
        response.close()

    # private methods
    def __get_token(self):
        if (self.__expiration - time.time()) > 5 * 60:
            return self.__token

        context = adal.AuthenticationContext(self.authority,
                                             validate_authority=True)
        token = context.acquire_token_with_client_credentials(
            self.resource, self.clientId, self.clientSecret)

        if token is None:
            raise Exception("Failed to retrieve AAD Token")

        self.__expiration = float(token['expiresIn']) + time.time()
        self.__token = token['accessToken']
        return self.__token

    def __sds_headers(self):
        return {"Authorization": "bearer %s" % self.__get_token(),
                "Content-type": "application/json",
                "Accept": "*/*; q=1"}

    def __set_path_and_query_templates(self):
        self.__basePath = "/api/Tenants/{tenant_id}/Namespaces/{namespace_id}"
        self.__typesPath = self.__basePath + "/Types/{type_id}"
        self.__streamsPath = self.__basePath + "/Streams/{stream_id}"
        self.__getStreamsPath = self.__basePath + "/Streams?" \
                                                  "query={query}&" \
                                                  "skip={skip}&" \
                                                  "count={count}"
        self.__dataPath = self.__basePath + "/Streams/{stream_id}/Data"
        self.__getLastValue = self.__dataPath + "/GetLastValue?" \
                                                "viewid={view_id}"
        self.__getWindowValues = self.__dataPath + "/GetWindowValues?" \
                                                   "startIndex={start}&" \
                                                   "endIndex={end}&" \
                                                   "viewid={view_id}"
        self.__updateValuePath = self.__dataPath + "/UpdateValue"
