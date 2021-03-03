from ..util import Response
from . import Idiom


class YamlIdiom(Idiom):
    """
    This is a very basic yaml implementation.

    It does the same thing as the #::unrest.idiom.unrest#UnRestIdiom+1 but with
    yaml instead of json.

    Requires pyyaml to be installed.
    """

    def __init__(self, rest):
        self.rest = rest
        try:
            import yaml
        except ImportError:
            raise ImportError(
                'You must have pyyaml installed to use this idiom'
            )
        self.yaml = yaml

    def request_to_payload(self, request):
        if request.payload:
            try:
                return self.yaml.load(
                    request.payload.decode('utf-8'),
                    Loader=self.yaml.SafeLoader,
                )
            except self.yaml.YAMLError as e:
                self.rest.raise_error(400, f'YAML Error in payload: {e}')

    def data_to_response(self, data, request, status=200):
        if (
            request.method == 'GET'
            and self.rest.unrest.empty_get_as_404
            and 'occurences' in data
            and data['occurences'] == 0
        ):
            status = 404
        payload = self.yaml.dump(data, default_flow_style=False)
        headers = {'Content-Type': 'text/yaml'}
        response = Response(payload, headers, status)
        return response
