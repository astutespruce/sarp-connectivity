<script lang="ts">
	import { attachmentKeywords } from '$lib/config/constants'
	import { isEmptyString } from '$lib/util/string'

	import Entry from './Entry.svelte'

	const { attachments } = $props()

	const photos = $derived.by(() => {
		if (isEmptyString(attachments)) {
			return []
		}

		const [prefix, parts] = attachments.split('|')
		return parts
			.split(',')
			.sort((a: string, b: string) =>
				attachmentKeywords.indexOf(a.split(':')[0]) < attachmentKeywords.indexOf(b.split(':')[0])
					? -1
					: 1
			)
			.map((part: string) => {
				const [keyword, partId] = part.split(':')
				return { keyword, url: `${prefix}/${partId}` }
			})
	})
</script>

<Entry label="Barrier survey photos">
	<div class={`grid grid-cols-${Math.min(2, attachments.length)} gap-4 mt-2`}>
		{#each photos as photo (photo.url)}
			<a
				href={photo.url}
				target="_blank"
				rel="external"
				class="flex flex-col overflow-hidden items-center"
			>
				<img
					src={photo.url}
					alt={photo.keyword}
					class="w-full border border-grey-7 hover:border-link"
				/>

				<div class="text-xs text-muted-foreground text-center">
					{photo.keyword}
				</div>
			</a>
		{/each}
	</div>
</Entry>
