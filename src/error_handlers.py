from flask import Blueprint

blueprint = Blueprint('error_handlers', __name__)

@blueprint.app_errorhandler(400)
def handle_400(error):
	return {'status': 'Bad Request'}, 400

@blueprint.app_errorhandler(404)
def handle_404(error):
	return {'status': 'Not Found'}, 404

@blueprint.app_errorhandler(500)
def handle_500(error):
	return {'status': 'Internal Server Error'}, 500

@blueprint.app_errorhandler(502)
def handle_502(error):
	return {'status': 'Bad Gateway'}, 502
