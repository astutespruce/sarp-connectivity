<script lang="ts">
	const { radius = 4, color = '#000000', borderColor = null, borderWidth = 0 } = $props()
	const width = $derived(2 * borderWidth + 2 * radius)
	const center = $derived(width / 2)
</script>

<div class="flex items-center justify-start flex-none" style="width:{width}px;">
	<svg style="width:{width}px; height:{width}px;">
		<circle
			cx={center}
			cy={center}
			r={radius}
			fill={color}
			stroke={borderColor}
			stroke-width={borderWidth}
		/>
	</svg>
</div>
