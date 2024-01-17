from flask import Response, jsonify, make_response


class APIResponse(Response):
    @classmethod
    def respond(cls, data):
        return make_response(jsonify(data=data))

    @classmethod
    def error(cls, message, status_code=200, data=None):
        error_data = {'error': message, 'data': data}
        return make_response(jsonify(error_data), status_code)
