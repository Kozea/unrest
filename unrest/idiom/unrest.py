import json

from . import Idiom
from ..util import Response


class UnRestIdiom(Idiom):
    def request_to_data(self, request):
        if request.payload:
            try:
                return json.loads(request.payload.decode('utf-8'))
            except json.JSONDecodeError as e:
                self.rest.raise_error(400, 'JSON Error in payload: %s' % e)

    def data_to_response(self, data, method, status=200):
        if (
            method == 'GET'
            and self.rest.unrest.empty_get_as_404
            and 'occurences' in data
            and data['occurences'] == 0
        ):
            status = 404
        payload = json.dumps(data)
        headers = {'Content-Type': 'application/json'}
        response = Response(payload, headers, status)
        return response
