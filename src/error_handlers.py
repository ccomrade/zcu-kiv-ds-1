from flask import Blueprint, jsonify

blueprint = Blueprint('error_handlers', __name__)

@blueprint.app_errorhandler(400)
def handle_400(error):
	return jsonify({'status': 'Bad Request'}), 400

@blueprint.app_errorhandler(404)
def handle_404(error):
	return jsonify({'status': 'Not Found'}), 404

@blueprint.app_errorhandler(500)
def handle_500(error):
	return jsonify({'status': 'Internal Server Error'}), 500

@blueprint.app_errorhandler(502)
def handle_502(error):
	return jsonify({'status': 'Bad Gateway'}), 502
