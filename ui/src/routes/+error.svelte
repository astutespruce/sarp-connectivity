<script>
	import { browser } from '$app/environment'
	import { page } from '$app/state'
	import { CONTACT_EMAIL, SITE_NAME } from '$lib/env'

	console.error(page.status)
	console.error(page.error)

	if (page.status !== 404 && browser && window.Sentry) {
		window.Sentry.captureException(page.error)
	}
</script>

<svelte:head>
	<title>{page.status} | {SITE_NAME}</title>
</svelte:head>

{#if page.status === 404}
	<div class="relative w-full h-full">
		<div class="hidden md:block absolute top-0 bottom-0 left-0 right-0 overflow-hidden">
			<enhanced:img
				src="$lib/assets/images/25898720604_f380ee9709_k.jpg"
				alt=""
				class="brightness-80"
			/>
			<div class="sticky bottom-0">
				<div class="absolute bottom-0 right-0 bg-black/65 text-white px-2 text-sm">
					Photo: students looking for macroinvertebrates in Cartoogechaye Creek, NC |
					<a
						href="https://www.flickr.com/photos/usfwssoutheast/25898720604/"
						target="_blank"
						class="text-white"
					>
						U.S. Fish & Wildlife Service Southeast Region</a
					>
				</div>
			</div>
		</div>
		<div class="relative mx-auto max-w-200 p-4 bg-white top-10">
			<h1 class="text-5xl">PAGE NOT FOUND</h1>
			<div class="text-2xl mt-4">
				However, we hope that by restoring aquatic connectivity, aquatic organisms will continue to
				be FOUND.
			</div>
		</div>
	</div>
{:else}
	<div class="mx-auto max-w-200 p-4 my-20">
		<h1 class="text-5xl">Oh no!</h1>
		<h2 class="text-3xl mt-4">We're sorry, there was an unexpected error</h2>
		<div class="mt-4 text-xl">
			Please try again in a few minutes. <br />
			If that still doesn't work, please
			<a href={`mailto:${CONTACT_EMAIL}`}> let us know</a>!
		</div>
	</div>
{/if}
