import json

from ..util import Response
from . import Idiom


class UnRestIdiom(Idiom):
    """
    The default UnRest implementation.

    Parses request payload as json.
    Serialize data as json.
    Can return a 404 on empty GET if `empty_get_as_404` is set as True in the
    Unrest instance.
    """

    def request_to_payload(self, request):
        if request.payload:
            try:
                return json.loads(request.payload.decode('utf-8'))
            except json.JSONDecodeError as e:
                self.rest.raise_error(400, f'JSON Error in payload: {e}')

    def data_to_response(self, data, request, status=200):
        if (
            request.method == 'GET'
            and self.rest.unrest.empty_get_as_404
            and 'occurences' in data
            and data['occurences'] == 0
        ):
            status = 404
        payload = json.dumps(data)
        headers = {'Content-Type': 'application/json'}
        response = Response(payload, headers, status)
        return response
