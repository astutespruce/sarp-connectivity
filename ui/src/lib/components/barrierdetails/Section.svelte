<script lang="ts">
	const { title, children } = $props()
</script>

<section class="pb-8">
	<h2 class="text-xl py-1 px-2 bg-blue-8 font-normal text-white border-b-2 border-b-blue-9">
		{title}
	</h2>

	{@render children()}
</section>
