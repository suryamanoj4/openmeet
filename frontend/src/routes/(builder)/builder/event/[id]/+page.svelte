<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import { getEvent, getEventTickets } from '$lib/services/events';
	import { CREATE_TICKET, DELETE_TICKET } from '$lib/graphql/queries/tickets';
	import { EVENT_PAGE, SAVE_EVENT_PAGE, PUBLISH_EVENT_PAGE, UNPUBLISH_EVENT_PAGE } from '$lib/graphql/queries/events';
	import { graphqlClient } from '$lib/graphql/client';
	import Button from '$lib/components/ui/button.svelte';
	import Input from '$lib/components/ui/input.svelte';
	import Label from '$lib/components/ui/label.svelte';
	import Card from '$lib/components/ui/card.svelte';
	import Badge from '$lib/components/ui/badge.svelte';
	import Modal from '$lib/components/ui/modal.svelte';
	import { ArrowLeft, Plus, Trash2, Layout, Eye, Ticket, Save, Globe, GripVertical, EyeOff, ChevronUp, ChevronDown, X } from 'lucide-svelte';
	import type { Event } from '$lib/graphql/types';

	// ---- Types ----
	type BlockType = 'hero' | 'text' | 'image' | 'about' | 'schedule' | 'speakers' | 'venue' | 'faqs' | 'cta' | 'video' | 'html' | 'divider';

	interface Block {
		id: string;
		type: BlockType;
		visible: boolean;
		props: Record<string, unknown>;
	}

	interface SpeakerItem { id: string; name: string; role: string; photo: string; bio: string; }
	interface ScheduleItem { id: string; time: string; title: string; description: string; }
	interface FAQItem { id: string; question: string; answer: string; }

	const blockTypeInfo: Record<BlockType, { label: string; icon: string; defaultProps: Record<string, unknown> }> = {
		hero: { label: 'Hero', icon: '✺', defaultProps: { headline: 'Welcome to {event}', subheadline: 'Join us for an amazing experience', bgColor: '#1a1a2e', bgImage: '', ctaText: 'Get Tickets', ctaLink: '#tickets' } },
		text: { label: 'Text', icon: '¶', defaultProps: { content: 'Write your content here...' } },
		image: { label: 'Image', icon: '🖼', defaultProps: { url: '', alt: '', caption: '' } },
		about: { label: 'About', icon: 'ℹ', defaultProps: { title: 'About', content: 'Event description...' } },
		schedule: { label: 'Schedule', icon: '🕐', defaultProps: { title: 'Schedule', items: [] as ScheduleItem[] } },
		speakers: { label: 'Speakers', icon: '👥', defaultProps: { title: 'Speakers', items: [] as SpeakerItem[] } },
		venue: { label: 'Venue', icon: '📍', defaultProps: { title: 'Venue', address: '', city: '', mapEmbed: '' } },
		faqs: { label: 'FAQs', icon: '❓', defaultProps: { title: 'Frequently Asked Questions', items: [] as FAQItem[] } },
		cta: { label: 'Call to Action', icon: '🎯', defaultProps: { headline: 'Ready to Join?', buttonText: 'Register Now', buttonLink: '#tickets' } },
		video: { label: 'Video', icon: '▶', defaultProps: { title: 'Watch', url: '', embedCode: '' } },
		html: { label: 'Custom HTML', icon: '<>', defaultProps: { code: '<!-- custom html -->' } },
		divider: { label: 'Divider', icon: '━', defaultProps: {} },
	};

	// ---- State ----
	let event = $state<Event | null>(null);
	let tickets = $state<{ id: string; name: string; price: number; currency: string; quantity: number }[]>([]);
	let loading = $state(true);
	let blocks = $state<Block[]>([]);
	type Tab = 'tickets' | 'blocks' | 'preview';
	let activeTab = $state<Tab>('tickets');
	let saving = $state(false);
	let saved = $state(false);
	let isPublished = $state(false);
	let selectedBlockIdx = $state<number | null>(null);
	let dragIdx = $state<number | null>(null);
	let previewModal = $state(false);

	// Ticket form
	let newTicketName = $state(''); let newTicketPrice = $state(0); let newTicketQty = $state(100);
	let ticketError = $state<string | null>(null); let savingTicket = $state(false);

	// ---- Init ----
	onMount(async () => {
		const id = $page.params.id as string;
		event = await getEvent(id);
		if (event) {
			const [tkts, pageResult] = await Promise.all([
				getEventTickets(id),
				graphqlClient.query<{ event_page: { blocks: unknown; is_published: boolean } | null }>(EVENT_PAGE, { event_id: id }).toPromise()
			]);
			tickets = tkts;
			if (pageResult.data?.event_page) {
				const rawBlocks = pageResult.data.event_page.blocks as Record<string, unknown>[] | undefined;
				if (rawBlocks && Array.isArray(rawBlocks)) {
					blocks = rawBlocks.map((b: Record<string, unknown>) => ({
						id: b.id as string || crypto.randomUUID(),
						type: b.type as BlockType || 'text',
						visible: (b.visible as boolean) ?? true,
						props: (b.props as Record<string, unknown>) || {},
					}));
				}
				isPublished = pageResult.data.event_page.is_published;
			}
		}
		loading = false;
	});

	// ---- Block operations ----
	function uuid() { return crypto.randomUUID(); }

	function addBlock(type: BlockType) {
		const info = blockTypeInfo[type];
		const props = JSON.parse(JSON.stringify(info.defaultProps));
		if (type === 'hero') props.headline = (props.headline as string).replace('{event}', event?.name || 'Event');
		blocks = [...blocks, { id: uuid(), type, visible: true, props }];
		selectedBlockIdx = blocks.length - 1;
	}

	function removeBlock(idx: number) {
		blocks = blocks.filter((_, i) => i !== idx);
		if (selectedBlockIdx === idx) selectedBlockIdx = null;
		else if (selectedBlockIdx !== null && selectedBlockIdx > idx) selectedBlockIdx--;
	}

	function moveBlock(from: number, to: number) {
		const copy = [...blocks];
		const [moved] = copy.splice(from, 1);
		copy.splice(to, 0, moved);
		blocks = copy;
		if (selectedBlockIdx === from) selectedBlockIdx = to;
	}

	function moveUp(idx: number) { if (idx > 0) moveBlock(idx, idx - 1); }
	function moveDown(idx: number) { if (idx < blocks.length - 1) moveBlock(idx, idx + 1); }
	function toggleVisibility(idx: number) { blocks[idx].visible = !blocks[idx].visible; blocks = [...blocks]; }

	// ---- Drag & Drop ----
	function handleDragStart(e: DragEvent, idx: number) {
		dragIdx = idx;
		e.dataTransfer!.effectAllowed = 'move';
		e.dataTransfer!.setData('text/plain', String(idx));
	}

	function handleDragOver(e: DragEvent) { e.preventDefault(); e.dataTransfer!.dropEffect = 'move'; }

	function handleDrop(e: DragEvent, targetIdx: number) {
		e.preventDefault();
		if (dragIdx !== null && dragIdx !== targetIdx) moveBlock(dragIdx, targetIdx);
		dragIdx = null;
	}

	function handleDragEnd() { dragIdx = null; }

	// ---- Item helpers (Schedule/Speakers/FAQs) ----
	function addScheduleItem(block: Block) {
		const items = (block.props.items as ScheduleItem[]) || [];
		block.props.items = [...items, { id: uuid(), time: '', title: '', description: '' }];
	}
	function removeScheduleItem(block: Block, itemId: string) {
		const items = (block.props.items as ScheduleItem[]) || [];
		block.props.items = items.filter(i => i.id !== itemId);
	}

	function addSpeakerItem(block: Block) {
		const items = (block.props.speakers as SpeakerItem[] || block.props.items as SpeakerItem[]) || [];
		const arr = [...items, { id: uuid(), name: '', role: '', photo: '', bio: '' }];
		block.props.items = arr;
	}
	function removeSpeakerItem(block: Block, itemId: string) {
		const items = (block.props.speakers as SpeakerItem[] || block.props.items as SpeakerItem[]) || [];
		if ('speakers' in block.props) block.props.speakers = items.filter(i => i.id !== itemId);
		else block.props.items = items.filter(i => i.id !== itemId);
	}
	function updateSpeakerField(block: Block, itemId: string, field: string, value: string) {
		const items = (block.props.speakers as SpeakerItem[] || block.props.items as SpeakerItem[]) || [];
		const item = items.find(i => i.id === itemId);
		if (item) (item as Record<string, string>)[field] = value;
	}

	function addFAQItem(block: Block) {
		const items = (block.props.items as FAQItem[]) || [];
		block.props.items = [...items, { id: uuid(), question: '', answer: '' }];
	}
	function removeFAQItem(block: Block, itemId: string) {
		const items = (block.props.items as FAQItem[]) || [];
		block.props.items = items.filter(i => i.id !== itemId);
	}
	function updateFAQField(block: Block, itemId: string, field: 'question' | 'answer', value: string) {
		const items = (block.props.items as FAQItem[]) || [];
		const item = items.find(i => i.id === itemId);
		if (item) item[field] = value;
	}

	function updateScheduleField(block: Block, itemId: string, field: string, value: string) {
		const items = (block.props.items as ScheduleItem[]) || [];
		const item = items.find(i => i.id === itemId);
		if (item) (item as Record<string, string>)[field] = value;
	}

	// ---- Save / Publish ----
	async function savePage() {
		saving = true; saved = false;
		try {
			const blockInputs = blocks.map(b => ({ id: b.id, type: b.type, props: b.props, visible: b.visible }));
			await graphqlClient.mutation(SAVE_EVENT_PAGE, { event_id: $page.params.id as string, input: { blocks: blockInputs, isPublished: isPublished } }).toPromise();
			saved = true;
			setTimeout(() => saved = false, 2500);
		} catch (e) { console.error(e); }
		saving = false;
	}

	async function togglePublish() {
		saving = true;
		try {
			if (isPublished) {
				await graphqlClient.mutation(UNPUBLISH_EVENT_PAGE, { event_id: $page.params.id as string }).toPromise();
				isPublished = false;
			} else {
				await graphqlClient.mutation(PUBLISH_EVENT_PAGE, { event_id: $page.params.id as string }).toPromise();
				isPublished = true;
			}
		} catch (e) { console.error(e); }
		saving = false;
	}

	// ---- Tickets ----
	async function addTicket() {
		if (!newTicketName) return; ticketError = null; savingTicket = true;
		try {
			const r = await graphqlClient.mutation<{ create_ticket: { id: string; name: string } }>(CREATE_TICKET, {
				input: { event_id: $page.params.id as string, name: newTicketName, price: newTicketPrice, quantity: newTicketQty, currency: 'USD', sort_order: tickets.length }
			}).toPromise();
			if (r.data?.create_ticket) {
				tickets = [...tickets, { id: r.data.create_ticket.id, name: newTicketName, price: newTicketPrice, currency: 'USD', quantity: newTicketQty }];
				newTicketName = ''; newTicketPrice = 0; newTicketQty = 100;
			} else ticketError = 'Failed';
		} catch (err) { ticketError = err instanceof Error ? err.message : 'Failed'; }
		savingTicket = false;
	}
	async function removeTicket(id: string) {
		await graphqlClient.mutation(DELETE_TICKET, { id }).toPromise();
		tickets = tickets.filter(t => t.id !== id);
	}

	// ---- Selected block for editing ----
	let selectedBlock = $derived(selectedBlockIdx !== null ? blocks[selectedBlockIdx] : null);
</script>

<div class="mx-auto max-w-7xl px-6 py-8">
	<button onclick={() => goto(`/events/${$page.params.id as string}`)} class="flex items-center gap-2 text-body-md text-on-surface-variant hover:text-fg mb-6 transition-colors">
		<ArrowLeft size={18} /> Back to event
	</button>

	{#if loading}
		<div class="space-y-4">
			<div class="h-16 rounded-xl bg-surface-container animate-pulse"></div>
			<div class="h-96 rounded-xl bg-surface-container animate-pulse"></div>
		</div>
	{:else if !event}
		<div class="text-center py-16"><p class="text-body-lg text-on-surface-variant">Event not found</p></div>
	{:else}
		<!-- Header -->
		<div class="flex items-center justify-between mb-6">
			<div class="flex items-center gap-3">
				<div class="flex h-12 w-12 items-center justify-center rounded-xl bg-primary-fixed text-primary"><Layout size={24} /></div>
				<div>
					<h1 class="text-headline-xl font-bold text-fg">Page Builder</h1>
					<p class="text-body-md text-on-surface-variant">{event.name} {#if isPublished}<Badge variant="success">Published</Badge>{:else}<Badge variant="default">Draft</Badge>{/if}</p>
				</div>
			</div>
			<div class="flex gap-2">
				<Button variant="outline" size="sm" onclick={togglePublish} isLoading={saving}>
					<Globe size={14} class="mr-1" />{isPublished ? 'Unpublish' : 'Publish'}
				</Button>
				<Button variant="primary" size="sm" onclick={savePage} isLoading={saving}>
					<Save size={14} class="mr-1" />{saved ? 'Saved!' : 'Save'}
				</Button>
			</div>
		</div>

		<!-- Tabs -->
		<div class="flex gap-2 mb-6">
			<button class="px-4 py-2 rounded-lg text-label-md font-semibold transition-colors {activeTab === 'tickets' ? 'bg-primary text-on-primary' : 'bg-surface-container-low text-on-surface-variant'}" onclick={() => activeTab = 'tickets'}><Ticket size={16} class="inline mr-1" />Tickets</button>
			<button class="px-4 py-2 rounded-lg text-label-md font-semibold transition-colors {activeTab === 'blocks' ? 'bg-primary text-on-primary' : 'bg-surface-container-low text-on-surface-variant'}" onclick={() => activeTab = 'blocks'}><Layout size={16} class="inline mr-1" />Page Blocks</button>
			<button class="px-4 py-2 rounded-lg text-label-md font-semibold transition-colors {activeTab === 'preview' ? 'bg-primary text-on-primary' : 'bg-surface-container-low text-on-surface-variant'}" onclick={() => { activeTab = 'preview'; previewModal = true; }}><Eye size={16} class="inline mr-1" />Preview</button>
		</div>

		<!-- ============ TICKETS TAB ============ -->
		{#if activeTab === 'tickets'}
			<Card class="p-6">
				<h2 class="text-headline-md font-semibold text-fg mb-4">Ticket Types</h2>
				{#if tickets.length > 0}
					<div class="space-y-3 mb-6">
						{#each tickets as t}
							<div class="flex items-center justify-between p-3 rounded-lg border border-outline-variant">
								<div><p class="text-body-md font-semibold text-fg">{t.name}</p><p class="text-label-sm text-on-surface-variant">{t.currency === 'INR' ? '₹' : '$'}{t.price} &middot; {t.quantity} available</p></div>
								<button onclick={() => removeTicket(t.id)} class="text-on-surface-variant hover:text-error transition-colors"><Trash2 size={16} /></button>
							</div>
						{/each}
					</div>
				{/if}
				<div class="border-t border-outline-variant/60 pt-4">
					<h3 class="text-label-md text-fg mb-3">Add Ticket Type</h3>
					{#if ticketError}<div class="rounded-lg border border-error-container/50 bg-error-container/10 p-3 mb-3"><p class="text-body-md text-error">{ticketError}</p></div>{/if}
					<div class="grid grid-cols-3 gap-3 mb-3">
						<div><Label for="tname">Name</Label><Input id="tname" bind:value={newTicketName} placeholder="General Admission" /></div>
						<div><Label for="tprice">Price</Label><Input id="tprice" type="number" bind:value={newTicketPrice} /></div>
						<div><Label for="tqty">Quantity</Label><Input id="tqty" type="number" bind:value={newTicketQty} /></div>
					</div>
					<Button variant="primary" size="sm" onclick={addTicket} isLoading={savingTicket}><Plus size={14} class="mr-1" />Add Ticket</Button>
				</div>
			</Card>

		<!-- ============ BLOCKS TAB ============ -->
		{:else if activeTab === 'blocks'}
			<div class="grid gap-6 lg:grid-cols-[1fr_380px]">
				<!-- Canvas -->
				<div class="space-y-3">
					{#if blocks.length === 0}
						<Card class="p-16 text-center border-dashed border-2">
							<Layout size={48} class="mx-auto text-on-surface-variant/30 mb-4" />
							<p class="text-headline-md text-on-surface-variant/50 mb-2">Empty Canvas</p>
							<p class="text-body-md text-on-surface-variant/40">Drag blocks from the palette or click to add</p>
						</Card>
					{:else}
						{#each blocks as block, idx (block.id)}
<div
				role="listitem"
				class={dragIdx === idx ? 'opacity-40' : ''}
								draggable="true"
								ondragstart={(e) => handleDragStart(e, idx)}
								ondragover={handleDragOver}
								ondrop={(e) => handleDrop(e, idx)}
								ondragend={handleDragEnd}
							>
								<Card class={selectedBlockIdx === idx ? 'ring-2 ring-primary ring-offset-2 ring-offset-surface-container-lowest' : (block.visible ? '' : 'opacity-60')}>
									<div class="flex items-center gap-2 px-4 py-2 border-b border-outline-variant/60 bg-surface-container-low/50">
										<button class="cursor-grab active:cursor-grabbing text-on-surface-variant/40 hover:text-on-surface-variant" title="Drag to reorder"><GripVertical size={16} /></button>
										<Badge variant={block.visible ? 'primary' : 'default'}>{blockTypeInfo[block.type].label}</Badge>
										<div class="flex-1"></div>
										<button onclick={() => { if (selectedBlockIdx === idx) selectedBlockIdx = null; else selectedBlockIdx = idx; }} class="p-1 rounded hover:bg-surface-container-low text-on-surface-variant/60 hover:text-fg transition-colors" title={selectedBlockIdx === idx ? 'Close editor' : 'Edit block'}>
											{selectedBlockIdx === idx ? '✕' : '✎'}
										</button>
										<button onclick={() => toggleVisibility(idx)} class="p-1 rounded hover:bg-surface-container-low text-on-surface-variant/60 hover:text-fg" title={block.visible ? 'Hide' : 'Show'}>{block.visible ? '👁' : '👁‍🗨'}</button>
										<button onclick={() => moveUp(idx)} disabled={idx === 0} class="p-1 rounded hover:bg-surface-container-low disabled:opacity-20 text-on-surface-variant/60"><ChevronUp size={16} /></button>
										<button onclick={() => moveDown(idx)} disabled={idx === blocks.length - 1} class="p-1 rounded hover:bg-surface-container-low disabled:opacity-20 text-on-surface-variant/60"><ChevronDown size={16} /></button>
										<button onclick={() => removeBlock(idx)} class="p-1 rounded hover:bg-error-container text-on-surface-variant/60 hover:text-error"><Trash2 size={16} /></button>
									</div>

									<!-- Block mini preview -->
									<div class="p-4 text-sm">
										{#if block.type === 'hero'}
											<p class="text-body-lg font-bold text-fg">{block.props.headline as string}</p>
											<p class="text-body-md text-on-surface-variant">{block.props.subheadline as string}</p>
										{:else if block.type === 'text' || block.type === 'about'}
											<p class="text-body-md text-on-surface-variant truncate max-w-lg">{(block.props.content || block.props.title) as string}</p>
										{:else if block.type === 'image'}
											<p class="text-body-md text-on-surface-variant">{block.props.url as string || 'No image set'}</p>
										{:else if block.type === 'schedule'}
											<p class="text-body-md text-on-surface-variant">{(block.props.items as ScheduleItem[])?.length || 0} schedule items</p>
										{:else if block.type === 'speakers'}
											<p class="text-body-md text-on-surface-variant">{(block.props.items as SpeakerItem[])?.length || 0} speakers</p>
										{:else if block.type === 'venue'}
											<p class="text-body-md text-on-surface-variant">{block.props.address as string || 'No venue set'}</p>
										{:else if block.type === 'faqs'}
											<p class="text-body-md text-on-surface-variant">{(block.props.items as FAQItem[])?.length || 0} questions</p>
										{:else if block.type === 'cta'}
											<p class="text-body-md text-on-surface-variant">{block.props.headline as string}</p>
										{:else if block.type === 'video'}
											<p class="text-body-md text-on-surface-variant">{block.props.url as string || 'No video set'}</p>
										{:else if block.type === 'html'}
											<p class="text-label-sm text-on-surface-variant font-mono">{(block.props.code as string)?.substring(0, 80) || 'No code'}</p>
										{:else if block.type === 'divider'}
											<div class="border-t border-outline-variant/60 my-2"></div>
										{/if}
									</div>
								</Card>
							</div>
						{/each}
					{/if}
				</div>

				<!-- Right sidebar: Block palette + Properties editor -->
				<div class="space-y-4 sticky top-24">
					<!-- Block palette -->
					<Card class="p-4">
						<h3 class="text-label-md font-semibold text-fg mb-3">Add Block</h3>
						<div class="grid grid-cols-2 gap-2">
							{#each Object.entries(blockTypeInfo) as [type, info]}
								<button
									class="flex items-center gap-2 text-left px-3 py-2.5 rounded-lg text-label-sm text-on-surface-variant hover:bg-surface-container-low hover:text-fg transition-colors border border-outline-variant/40 hover:border-primary/30"
									onclick={() => addBlock(type as BlockType)}
								>
									<span class="text-base">{info.icon}</span><span>{info.label}</span>
								</button>
							{/each}
						</div>
					</Card>

					<!-- Properties editor -->
					{#if selectedBlock}
						<Card class="p-4">
							<div class="flex items-center justify-between mb-3">
								<h3 class="text-label-md font-semibold text-fg">{blockTypeInfo[selectedBlock.type].label} Properties</h3>
								<button onclick={() => selectedBlockIdx = null} class="text-on-surface-variant/60 hover:text-fg"><X size={14} /></button>
							</div>

							<div class="space-y-3 max-h-[50vh] overflow-y-auto">
								{#if selectedBlock.type === 'hero'}
									<Input label="Headline" bind:value={selectedBlock.props.headline as string} />
									<Input label="Subheadline" bind:value={selectedBlock.props.subheadline as string} />
									<Input label="Background Color" type="color" bind:value={selectedBlock.props.bgColor as string} class="h-10 w-full p-0" />
									<Input label="Background Image URL" bind:value={selectedBlock.props.bgImage as string} placeholder="https://..." />
									<Input label="Button Text" bind:value={selectedBlock.props.ctaText as string} />
									<Input label="Button Link" bind:value={selectedBlock.props.ctaLink as string} placeholder="#tickets" />
								{:else if selectedBlock.type === 'text'}
									<textarea bind:value={selectedBlock.props.content as string} class="w-full min-h-[120px] rounded-lg border border-input bg-surface-container-lowest px-3 py-2 text-body-md focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring resize-y" placeholder="Write your content..."></textarea>
								{:else if selectedBlock.type === 'image'}
									<Input label="Image URL" bind:value={selectedBlock.props.url as string} placeholder="https://..." />
									<Input label="Alt Text" bind:value={selectedBlock.props.alt as string} />
									<Input label="Caption" bind:value={selectedBlock.props.caption as string} />
								{:else if selectedBlock.type === 'about'}
									<Input label="Title" bind:value={selectedBlock.props.title as string} />
									<textarea bind:value={selectedBlock.props.content as string} class="w-full min-h-[100px] rounded-lg border border-input bg-surface-container-lowest px-3 py-2 text-body-md focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring resize-y" placeholder="Write about this event..."></textarea>
								{:else if selectedBlock.type === 'schedule'}
									<Input label="Title" bind:value={selectedBlock.props.title as string} />
									<div class="space-y-2">
										{#each (selectedBlock.props.items as ScheduleItem[]) || [] as item (item.id)}
											<div class="rounded-lg border border-outline-variant p-3 space-y-2">
												<div class="flex justify-between items-center">
													<span class="text-label-sm text-on-surface-variant">Item</span>
													<button onclick={() => removeScheduleItem(selectedBlock!, item.id)} class="text-on-surface-variant/60 hover:text-error"><X size={14} /></button>
												</div>
												<Input bind:value={item.time} placeholder="10:00 AM" oninput={() => updateScheduleField(selectedBlock!, item.id, 'time', item.time)} />
												<Input bind:value={item.title} placeholder="Session title" oninput={() => updateScheduleField(selectedBlock!, item.id, 'title', item.title)} />
												<Input bind:value={item.description} placeholder="Description" oninput={() => updateScheduleField(selectedBlock!, item.id, 'description', item.description)} />
											</div>
										{/each}
										<Button variant="outline" size="sm" class="w-full" onclick={() => addScheduleItem(selectedBlock!)}><Plus size={14} class="mr-1" />Add Item</Button>
									</div>
								{:else if selectedBlock.type === 'speakers'}
									<Input label="Title" bind:value={selectedBlock.props.title as string} />
									<div class="space-y-2">
										{#each (selectedBlock.props.items as SpeakerItem[]) || [] as item (item.id)}
											<div class="rounded-lg border border-outline-variant p-3 space-y-2">
												<div class="flex justify-between items-center">
													<span class="text-label-sm text-on-surface-variant">Speaker</span>
													<button onclick={() => removeSpeakerItem(selectedBlock!, item.id)} class="text-on-surface-variant/60 hover:text-error"><X size={14} /></button>
												</div>
												<Input bind:value={item.name} placeholder="Name" oninput={() => updateSpeakerField(selectedBlock!, item.id, 'name', item.name)} />
												<Input bind:value={item.role} placeholder="Role" oninput={() => updateSpeakerField(selectedBlock!, item.id, 'role', item.role)} />
												<Input bind:value={item.photo} placeholder="Photo URL" oninput={() => updateSpeakerField(selectedBlock!, item.id, 'photo', item.photo)} />
												<textarea bind:value={item.bio} class="w-full min-h-[60px] rounded-lg border border-input bg-surface-container-lowest px-3 py-2 text-body-md focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring resize-y" placeholder="Bio" oninput={() => updateSpeakerField(selectedBlock!, item.id, 'bio', item.bio)}></textarea>
											</div>
										{/each}
										<Button variant="outline" size="sm" class="w-full" onclick={() => addSpeakerItem(selectedBlock!)}><Plus size={14} class="mr-1" />Add Speaker</Button>
									</div>
								{:else if selectedBlock.type === 'venue'}
									<Input label="Title" bind:value={selectedBlock.props.title as string} />
									<Input label="Address" bind:value={selectedBlock.props.address as string} />
									<Input label="City" bind:value={selectedBlock.props.city as string} />
									<Input label="Map Embed Code" bind:value={selectedBlock.props.mapEmbed as string} placeholder="<iframe src=...></iframe>" />
								{:else if selectedBlock.type === 'faqs'}
									<Input label="Title" bind:value={selectedBlock.props.title as string} />
									<div class="space-y-2">
										{#each (selectedBlock.props.items as FAQItem[]) || [] as item (item.id)}
											<div class="rounded-lg border border-outline-variant p-3 space-y-2">
												<div class="flex justify-between items-center">
													<span class="text-label-sm text-on-surface-variant">FAQ</span>
													<button onclick={() => removeFAQItem(selectedBlock!, item.id)} class="text-on-surface-variant/60 hover:text-error"><X size={14} /></button>
												</div>
												<Input bind:value={item.question} placeholder="Question" oninput={() => updateFAQField(selectedBlock!, item.id, 'question', item.question)} />
												<textarea bind:value={item.answer} class="w-full min-h-[60px] rounded-lg border border-input bg-surface-container-lowest px-3 py-2 text-body-md focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring resize-y" placeholder="Answer" oninput={() => updateFAQField(selectedBlock!, item.id, 'answer', item.answer)}></textarea>
											</div>
										{/each}
										<Button variant="outline" size="sm" class="w-full" onclick={() => addFAQItem(selectedBlock!)}><Plus size={14} class="mr-1" />Add FAQ</Button>
									</div>
								{:else if selectedBlock.type === 'cta'}
									<Input label="Headline" bind:value={selectedBlock.props.headline as string} />
									<Input label="Button Text" bind:value={selectedBlock.props.buttonText as string} />
									<Input label="Button Link" bind:value={selectedBlock.props.buttonLink as string} placeholder="#tickets" />
								{:else if selectedBlock.type === 'video'}
									<Input label="Title" bind:value={selectedBlock.props.title as string} />
									<Input label="Video URL" bind:value={selectedBlock.props.url as string} placeholder="https://youtube.com/watch?v=..." />
									<textarea bind:value={selectedBlock.props.embedCode as string} class="w-full min-h-[80px] rounded-lg border border-input bg-surface-container-lowest px-3 py-2 text-body-md focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring resize-y" placeholder="Or paste embed code..."></textarea>
								{:else if selectedBlock.type === 'html'}
									<textarea bind:value={selectedBlock.props.code as string} class="w-full min-h-[150px] rounded-lg border border-input bg-surface-container-lowest px-3 py-2 text-label-sm font-mono focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring resize-y" placeholder="<!-- HTML here -->"></textarea>
								{:else if selectedBlock.type === 'divider'}
									<p class="text-body-md text-on-surface-variant">No properties for divider</p>
								{/if}
							</div>
						</Card>
					{/if}
				</div>
			</div>
		{/if}

		<!-- ============ PREVIEW MODAL ============ -->
		<Modal title="Page Preview" bind:open={previewModal} size="xl" onclose={() => { previewModal = false; activeTab = 'blocks'; }}>
			<div class="space-y-6 max-h-[75vh] overflow-y-auto py-4">
				{#if blocks.length === 0}
					<div class="text-center py-16"><p class="text-body-lg text-on-surface-variant/40">No blocks on this page</p></div>
				{:else}
					{#each blocks.filter(b => b.visible) as block (block.id)}
						<div class="rounded-xl overflow-hidden">
							{#if block.type === 'hero'}
								<div class="text-center py-16 px-8 rounded-xl" style="background-color: {block.props.bgColor || '#1a1a2e'}; background-image: url({block.props.bgImage})">
									<h1 class="text-4xl font-bold text-white mb-4">{block.props.headline as string}</h1>
									<p class="text-xl text-white/80 mb-6">{block.props.subheadline as string}</p>
									{#if block.props.ctaText}
										<button class="inline-flex h-14 px-8 rounded-xl bg-white text-black font-semibold text-lg hover:bg-white/90 transition-all">
											{block.props.ctaText as string}
										</button>
									{/if}
								</div>
							{:else if block.type === 'text'}
								<div class="py-4 px-1">
									<div class="prose prose-lg max-w-none text-fg">{@html (block.props.content as string)?.replace(/\n/g, '<br>')}</div>
								</div>
							{:else if block.type === 'image'}
								{#if block.props.url}
									<figure class="text-center">
										<img src={block.props.url as string} alt={block.props.alt as string} class="w-full max-h-96 object-cover rounded-xl" />
										{#if block.props.caption}<figcaption class="text-body-md text-on-surface-variant mt-2">{block.props.caption as string}</figcaption>{/if}
									</figure>
								{/if}
							{:else if block.type === 'about'}
								<div class="py-6 px-1">
									<h2 class="text-headline-lg font-bold text-fg mb-4">{block.props.title as string}</h2>
									<p class="text-body-md text-on-surface-variant whitespace-pre-line">{block.props.content as string}</p>
								</div>
							{:else if block.type === 'schedule'}
								<div class="py-6 px-1">
									<h2 class="text-headline-lg font-bold text-fg mb-6">{block.props.title as string}</h2>
									<div class="space-y-4">
										{#each (block.props.items as ScheduleItem[]) || [] as item (item.id)}
											<div class="flex gap-4 p-4 rounded-xl border border-outline-variant">
												<div class="text-primary font-bold text-body-md min-w-[80px]">{item.time}</div>
												<div><h3 class="text-body-md font-semibold text-fg">{item.title}</h3><p class="text-body-sm text-on-surface-variant">{item.description}</p></div>
											</div>
										{/each}
									</div>
								</div>
							{:else if block.type === 'speakers'}
								<div class="py-6 px-1">
									<h2 class="text-headline-lg font-bold text-fg mb-6">{block.props.title as string}</h2>
									<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
										{#each (block.props.items as SpeakerItem[]) || [] as item (item.id)}
											<div class="text-center p-6 rounded-xl border border-outline-variant hover:shadow-md transition-shadow">
												{#if item.photo}<img src={item.photo} alt={item.name} class="w-20 h-20 rounded-full mx-auto mb-3 object-cover" />{/if}
												<h3 class="text-body-md font-semibold text-fg">{item.name}</h3>
												<p class="text-label-sm text-primary mb-2">{item.role}</p>
												<p class="text-body-sm text-on-surface-variant">{item.bio}</p>
											</div>
										{/each}
									</div>
								</div>
							{:else if block.type === 'venue'}
								<div class="py-6 px-1">
									<h2 class="text-headline-lg font-bold text-fg mb-4">{block.props.title as string}</h2>
									{#if block.props.mapEmbed}
										<div class="rounded-xl overflow-hidden mb-4">{@html block.props.mapEmbed as string}</div>
									{/if}
									<p class="text-body-md text-fg">{block.props.address as string}</p>
									<p class="text-body-md text-on-surface-variant">{block.props.city as string}</p>
								</div>
							{:else if block.type === 'faqs'}
								<div class="py-6 px-1">
									<h2 class="text-headline-lg font-bold text-fg mb-6">{block.props.title as string}</h2>
									<div class="space-y-3">
										{#each (block.props.items as FAQItem[]) || [] as item (item.id)}
											<details class="group rounded-xl border border-outline-variant p-4 cursor-pointer">
												<summary class="text-body-md font-semibold text-fg list-none flex items-center justify-between">
													{item.question}
													<span class="text-on-surface-variant group-open:rotate-180 transition-transform">▼</span>
												</summary>
												<p class="text-body-md text-on-surface-variant mt-3 pt-3 border-t border-outline-variant/60">{item.answer}</p>
											</details>
										{/each}
									</div>
								</div>
							{:else if block.type === 'cta'}
								<div class="text-center py-16 px-8 bg-primary-fixed/30 rounded-xl">
									<h2 class="text-headline-lg font-bold text-fg mb-4">{block.props.headline as string}</h2>
									<button class="inline-flex h-14 px-8 rounded-xl bg-primary text-on-primary font-semibold text-lg hover:bg-primary/90 transition-all">
										{block.props.buttonText as string}
									</button>
								</div>
							{:else if block.type === 'video'}
								<div class="py-6 px-1">
									{#if block.props.title}
										<h2 class="text-headline-lg font-bold text-fg mb-4">{block.props.title as string}</h2>
									{/if}
									<div class="rounded-xl overflow-hidden aspect-video bg-surface-container">
										{#if block.props.embedCode}
											{@html block.props.embedCode as string}
										{:else if block.props.url}
											<div class="flex items-center justify-center h-full text-on-surface-variant/40">▶ Video URL: {block.props.url as string}</div>
										{:else}
											<div class="flex items-center justify-center h-full text-on-surface-variant/40">No video set</div>
										{/if}
									</div>
								</div>
							{:else if block.type === 'html'}
								<div class="py-4">{@html block.props.code as string}</div>
							{:else if block.type === 'divider'}
								<hr class="border-outline-variant/40 my-2" />
							{/if}
						</div>
					{/each}
				{/if}
			</div>
		</Modal>
	{/if}
</div>