<script lang="ts">
	import { attachmentKeywords } from '$lib/config/constants'
	import { isEmptyString } from '$lib/util/string'

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

<section>
	<h2 class="flex items-baseline justify-between gap-8">
		<div>Barrier survey photos</div>

		<div class="text-xs font-normal flex-none">(click for full size)</div>
	</h2>

	<div class={`grid grid-cols-2 sm:grid-cols-${Math.min(3, attachments.length)} gap-4 mt-2`}>
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
</section>
