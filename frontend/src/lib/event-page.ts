export interface EventPageBlock {
	id: string;
	type: 'hero' | 'text' | 'image' | 'about' | 'schedule' | 'speakers' | 'venue' | 'faqs' | 'cta' | 'video' | 'divider';
	visible: boolean;
	props: Record<string, unknown>;
}

export function normalizeEventPageBlocks(value: unknown): EventPageBlock[] {
	if (!Array.isArray(value)) return [];
	return value
		.filter((block): block is Record<string, unknown> => !!block && typeof block === 'object')
		.filter((block) => typeof block.id === 'string' && typeof block.type === 'string')
		.map((block) => ({
			id: block.id as string,
			type: block.type as EventPageBlock['type'],
			visible: block.visible !== false,
			props: block.props && typeof block.props === 'object'
				? block.props as Record<string, unknown>
				: {}
		}));
}

export function safeLink(value: unknown): string {
	if (typeof value !== 'string') return '#';
	if (value.startsWith('/') || value.startsWith('#')) return value;
	try {
		const url = new URL(value);
		return url.protocol === 'https:' || url.protocol === 'http:' ? url.toString() : '#';
	} catch {
		return '#';
	}
}

export function videoEmbedUrl(value: unknown): string | null {
	if (typeof value !== 'string') return null;
	try {
		const url = new URL(value);
		if (url.hostname === 'youtu.be') return `https://www.youtube-nocookie.com/embed/${url.pathname.slice(1)}`;
		if (url.hostname.endsWith('youtube.com')) {
			const id = url.searchParams.get('v');
			return id ? `https://www.youtube-nocookie.com/embed/${id}` : null;
		}
		if (url.hostname === 'vimeo.com') return `https://player.vimeo.com/video/${url.pathname.slice(1)}`;
	} catch {
		return null;
	}
	return null;
}
