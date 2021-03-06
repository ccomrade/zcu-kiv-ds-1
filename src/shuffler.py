#!/usr/bin/env python3

import os, threading, random, requests, error_handlers

from flask import Flask, request, abort, jsonify

app = Flask(__name__)
app.register_blueprint(error_handlers.blueprint)

BANK_SERVERS = os.environ['SHUFFLER_BANK_SERVERS'].split(' ')

for server in BANK_SERVERS:
	app.logger.info('Using bank server at ' + server)

class Message:
	def __init__(self, operation, amount, seq):
		self.operation = operation
		self.amount = amount
		self.seq = seq

	def serialize(self):
		return {
			'operation': self.operation,
			'amount': self.amount,
			'seq': self.seq
		}

class MessageDispatcher:
	def __init__(self):
		self.buffer = []
		self.condition = threading.Condition()

		threading.Thread(target=self.__worker_loop, daemon=True).start()
		app.logger.info('Worker thread started')

	def __dispatch(self, buffer):
		# make sure messages are sent in a different order
		random.shuffle(buffer)
		random.shuffle(buffer)
		random.shuffle(buffer)

		for message in buffer:
			payload = message.serialize()

			app.logger.info('Sending ' + str(payload))

			for server in BANK_SERVERS:
				app.logger.info('To ' + server)

				try:
					response = requests.post('http://' + server + '/api/v1/account', json=payload)
					response.raise_for_status()
				except requests.RequestException:
					app.logger.exception('Failed to contact bank server at ' + server)

	def __worker_loop(self):
		while True:
			buffer = []

			with self.condition:
				# sleep until something is received
				if len(self.buffer) == 0:
					self.condition.wait()

				# wait a bit for more messages
				while len(self.buffer) < 200 and self.condition.wait(2):
					pass

				# grab all messages received so far
				buffer = self.buffer
				self.buffer = []

			# send messages in random order
			self.__dispatch(buffer)

	def add(self, message):
		with self.condition:
			self.buffer.append(message)
			self.condition.notify()

dispatcher = MessageDispatcher()

@app.route('/api/v1/messages', methods=['POST'])
def add_message():
	data = request.get_json()

	try:
		operation = data['operation']
		amount = int(data['amount'])
		seq = int(data['seq'])
	except (KeyError, ValueError):
		app.logger.exception('Invalid request data')
		abort(400)

	dispatcher.add(Message(operation, amount, seq))

	app.logger.info('Added operation {} with amount {} and seq {}'.format(operation, amount, seq))

	return jsonify({'status': 'OK'})

if __name__ == '__main__':
	app.run()
