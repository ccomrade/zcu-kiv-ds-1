#!/usr/bin/env python3

import os, logging, threading, random, requests, error_handlers

from flask import Flask, request, abort

app = Flask(__name__)
app.logger.setLevel(logging.INFO)
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
		while self.running:
			buffer = []

			with self.condition:
				# sleep until something is received
				if len(self.buffer) == 0:
					self.condition.wait()

				# wait a bit for more messages
				while self.running and len(self.buffer) < 200 and self.condition.wait(2):
					pass

				# grab all messages received so far
				buffer = self.buffer
				self.buffer = []

			# send messages in random order
			self.__dispatch(buffer)

	def __enter__(self):
		self.running = True
		self.worker = threading.Thread(target=self.__worker_loop)

		self.worker.start()
		app.logger.info('Worker thread started')

	def __exit__(self, type, value, traceback):
		self.running = False

		with self.condition:
			self.condition.notify_all()

		app.logger.info('Waiting for worker thread to stop...')
		self.worker.join()
		app.logger.info('Worker thread stopped')

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

	return {'status': 'OK'}

if __name__ == '__main__':
	# ensure proper start and stop of worker thread for dispatching messages
	with dispatcher:
		app.run()
