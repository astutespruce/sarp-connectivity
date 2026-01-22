<script lang="ts">
	// All scores are normalized on a 0-1 basis, with 0 being lowest value
	const { label, score, tier } = $props()
</script>

<div class="not-first-of-type:mt-12">
	<div class="text-sm">{label}</div>
	<div class="flex items-center mt-2 gap-5">
		<div class="flex-none text-muted-foreground text-xs">Low</div>

		<div class="flex-auto relative mt-1">
			<div class="h-0.5 bg-grey-2"></div>
			<div
				class="absolute pt-1 -top-4 w-8 h-8 rounded-xl bg-grey-8 -ml-4 text-center color-white"
				style={`left: ${score}%;`}
			>
				{tier}
			</div>
		</div>

		<div class="flex-none text-muted-foreground text-xs">High</div>
	</div>
</div>
