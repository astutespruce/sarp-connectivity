<script lang="ts">
	const { title, children } = $props()
</script>

<section class="not-first-of-type:mt-1">
	<h2 class="text-lg py-1 px-2 bg-grey-1 font-bold">{title}</h2>

	<div class="mt-2">
		{@render children()}
	</div>
</section>
