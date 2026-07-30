import assert from 'node:assert/strict';
import test from 'node:test';

import {
	normalizeEventPageBlocks,
	safeLink,
	videoEmbedUrl
} from './event-page.ts';

test('normalizes only supported event page blocks', () => {
	assert.deepEqual(
		normalizeEventPageBlocks([
			{ id: 'hero-1', type: 'hero', props: { title: 'Welcome' } },
			{ id: 'unknown-1', type: 'script', props: {} },
			{ id: 42, type: 'text' }
		]),
		[
			{
				id: 'hero-1',
				type: 'hero',
				visible: true,
				props: { title: 'Welcome' }
			}
		]
	);
});

test('safeLink accepts local and HTTP links but rejects script protocols', () => {
	assert.equal(safeLink('/tickets'), '/tickets');
	assert.equal(safeLink('https://example.com/event'), 'https://example.com/event');
	assert.equal(safeLink('javascript:alert(1)'), '#');
});

test('videoEmbedUrl accepts exact supported hosts only', () => {
	assert.equal(
		videoEmbedUrl('https://www.youtube.com/watch?v=video123'),
		'https://www.youtube-nocookie.com/embed/video123'
	);
	assert.equal(videoEmbedUrl('https://evilyoutube.com/watch?v=video123'), null);
	assert.equal(
		videoEmbedUrl('https://vimeo.com/12345'),
		'https://player.vimeo.com/video/12345'
	);
});
