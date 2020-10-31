#!/usr/bin/env python3

import os, logging, requests, error_handlers

from flask import Flask, request, abort, jsonify

app = Flask(__name__)
app.logger.setLevel(logging.INFO)
app.register_blueprint(error_handlers.blueprint)

SHUFFLER_ADDRESS = os.environ['SEQUENCER_SHUFFLER_ADDRESS']

app.logger.info('Using shuffler at ' + SHUFFLER_ADDRESS)

seq = 0

@app.route('/api/v1/messages', methods=['POST'])
def forward_message():
	data = request.get_json()

	try:
		operation = data['operation']
		amount = int(data['amount'])
	except (KeyError, ValueError):
		app.logger.exception('Invalid request data')
		abort(400)

	global seq

	payload = {
		'operation': operation,
		'amount': amount,
		'seq': seq
	}

	app.logger.info('Sending ' + str(payload) + ' to shuffler')

	try:
		response = requests.post('http://' + SHUFFLER_ADDRESS + '/api/v1/messages', json=payload)
		response.raise_for_status()
	except requests.RequestException:
		app.logger.exception('Failed to contact shuffler at ' + SHUFFLER_ADDRESS)
		abort(502)

	seq += 1

	return jsonify({'status': 'OK'})

if __name__ == '__main__':
	app.run()
