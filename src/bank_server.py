#!/usr/bin/env python3

import error_handlers

from flask import Flask, request, abort, jsonify

app = Flask(__name__)
app.register_blueprint(error_handlers.blueprint)

class Transaction:
	def __init__(self, amount, seq):
		self.amount = amount
		self.seq = seq

	def __eq__(self, other):
		return self.seq == other.seq

	def __lt__(self, other):
		return self.seq < other.seq

class BankAccount:
	def __init__(self, initial_balance):
		self.balance = initial_balance
		self.pending_transactions = []
		self.current_seq = 0

	def __commit_transaction(self, ts):
		self.balance += ts.amount
		self.current_seq += 1

		app.logger.info('Transaction with seq {} and amount {} committed'.format(ts.seq, ts.amount))

	def __try_commit_pending_transactions(self):
		while self.pending_transactions:
			ts = self.pending_transactions[0]

			# all intermediate transactions must be processed first
			if ts.seq != self.current_seq:
				break

			self.__commit_transaction(ts)

			self.pending_transactions.pop(0)

	def __push_pending_transaction(self, ts):
		self.pending_transactions.append(ts)
		self.pending_transactions.sort()

	def add_transaction(self, ts):
		if ts.seq < self.current_seq:
			return False

		if ts.seq == self.current_seq:
			# consecutive transactions are processed immediately
			self.__commit_transaction(ts)

			# maybe some pending transactions can be processed now
			self.__try_commit_pending_transactions()
		else:
			# the transaction sequence number must be unique
			if ts in self.pending_transactions:
				return False

			# transactions with higher sequence number are deferred for later processing
			self.__push_pending_transaction(ts)

			app.logger.info('Transaction with seq {} and amount {} is pending'.format(ts.seq, ts.amount))

		return True

account = BankAccount(initial_balance=5000000)

@app.route('/api/v1/account', methods=['GET'])
def get_account_status():
	return jsonify({
		'balance': account.balance,
		'current_seq': account.current_seq,
		'pending_transactions': len(account.pending_transactions)
	})

@app.route('/api/v1/account', methods=['POST'])
def add_new_transaction():
	data = request.get_json()

	try:
		operation = data['operation']
		amount = int(data['amount'])
		seq = int(data['seq'])
	except (KeyError, ValueError):
		app.logger.exception('Invalid request data')
		abort(400)

	if (operation != 'CREDIT' and operation != 'DEBIT') or amount <= 0 or seq < 0:
		abort(400)

	if operation == 'DEBIT':
		# debit operation is actually just adding a negative amount
		amount = -amount

	if not account.add_transaction(Transaction(amount, seq)):
		abort(400)

	return jsonify({'status': 'OK'})

if __name__ == '__main__':
	app.run()
