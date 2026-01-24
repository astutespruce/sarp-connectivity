<script lang="ts">
	type Coords = {
		lat: number
		lng: number
	}

	const { map } = $props()

	let coords: Coords | null = $state(null)

	$effect(() => {
		if (!map) {
			return
		}

		map.on('mousemove', ({ lngLat }: { lngLat: Coords }) => {
			coords = lngLat
		})

		map.on('mouseout', () => {
			coords = null
		})
	})
</script>

{#if coords !== null}
	<div class="absolute bottom-0 left-25 py-1 px-2 z-2000 bg-white/50 text-xs">
		{Math.round(coords.lat * 100000) / 100000}° N,
		{Math.round(coords.lng * 100000) / 100000}° E
	</div>
{/if}
