import assert from 'node:assert/strict';
import test from 'node:test';

import { requireMutationResult } from './result.ts';

test('a GraphQL mutation error is surfaced to the caller', () => {
	assert.throws(
		() =>
			requireMutationResult(
				{ data: undefined, error: { message: 'Authentication required' } },
				'create_event',
				'Failed to create event'
			),
		/Authentication required/
	);
});

test('missing mutation data produces an actionable fallback error', () => {
	assert.throws(
		() =>
			requireMutationResult(
				{ data: undefined, error: undefined },
				'create_event',
				'Failed to create event'
			),
		/Failed to create event/
	);
});
