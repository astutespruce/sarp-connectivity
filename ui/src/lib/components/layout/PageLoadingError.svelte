<script lang="ts">
	import { CONTACT_EMAIL } from '$lib/env'
	import { Alert } from '$lib/components/alert'
</script>

<Alert title="Oh no!" class="text-lg mt-8">
	<p class="text-lg">
		We're sorry, there was an unexpected error loading this page. Please reload this page in your
		browser.
		<br /><br />
		If that doesn't fix the problem, please <a href={`mailto:${CONTACT_EMAIL}`}>contact us</a> to let
		us know!
	</p>
</Alert>
