#!/usr/bin/env python3

import sys, random, requests

if len(sys.argv) < 3:
	print('Usage: {} SEQUENCER_ADDRESS MESSAGE_COUNT'.format(sys.argv[0]), file=sys.stderr)
	sys.exit(2)

SEQUENCER_ADDRESS = sys.argv[1]
MESSAGE_COUNT = int(sys.argv[2])

OPERATIONS = [ 'CREDIT', 'DEBIT' ]

for _ in range(MESSAGE_COUNT):
	operation = random.choice(OPERATIONS)
	amount = random.randint(10000, 50000)

	payload = {
		'operation': operation,
		'amount': amount
	}

	print('Sending ' + str(payload))

	response = requests.post('http://' + SEQUENCER_ADDRESS + '/api/v1/messages', json=payload)
	response.raise_for_status()

print('Sent {} messages to {}'.format(MESSAGE_COUNT, SEQUENCER_ADDRESS))
