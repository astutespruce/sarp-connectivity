<script>
	import { browser } from '$app/environment'
	import { page } from '$app/state'
	import { CONTACT_EMAIL, SITE_NAME } from '$lib/env'
	import { NotFoundPage } from '$lib/components/layout'

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
	<NotFoundPage />
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
