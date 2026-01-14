<script lang="ts">
	import { superForm, defaults } from 'sveltekit-superforms'
	import { zod4Client } from 'sveltekit-superforms/adapters'
	import { zod4 } from 'sveltekit-superforms/adapters'
	import { z } from 'zod'
	import { v4 as uuid } from 'uuid'
	import LoadingIcon from '@lucide/svelte/icons/loader-circle'

	import { CONTACT_EMAIL, MAILCHIMP_FORM } from '$lib/env'
	import { fetchJSONP } from '$lib/api'
	import { cn } from '$lib/utils'
	import { Alert } from '$lib/components/alert'
	import { Button } from '$lib/components/ui/button'
	import * as Dialog from '$lib/components/ui/dialog'
	import {
		Field,
		Control,
		Label,
		FieldErrors,
		Button as SubmitButton
	} from '$lib/components/ui/form'
	import { Input } from '$lib/components/ui/input'
	import { Textarea } from '$lib/components/ui/textarea'
	import { saveToStorage } from '$lib/util/dom'
	import { captureException } from '$lib/util/log'

	type UserInfoData = {
		email: string
		firstName: string
		lastName: string
		organization: string
		use: string
	}

	// lookup of local form fields to Mailchimp API form fields
	const mailchimpFieldMap = {
		email: 'EMAIL',
		firstName: 'FNAME',
		lastName: 'LNAME',
		organization: 'MMERGE5',
		use: 'MMERGE6'
	}

	let { open = $bindable(true), onContinue } = $props()
	let hasError = $state(false)

	const submitUserInfo = async (data: UserInfoData) => {
		// Mailchimp doesn't have CORS support, so we have to use JSONP to submit form data.
		// yuck!
		const params = {
			u: MAILCHIMP_FORM.userId,
			id: MAILCHIMP_FORM.formId1,
			f_id: MAILCHIMP_FORM.formId2,
			...Object.fromEntries(
				Object.entries(mailchimpFieldMap).map(([field, formFieldName]) => [
					formFieldName,
					data[field as keyof typeof data]
				])
			)
		}

		try {
			type MailChimpResponse = {
				result: string
				msg: string
			}
			const response = await fetchJSONP(MAILCHIMP_FORM.url, params, 'c')
			const { result, msg } = response as MailChimpResponse

			if (result === 'error') {
				const error = `MailChimp submit error: ${msg}`
				captureException(error)
				return { error }
			}

			saveToStorage('downloadForm', data)

			return { error: null }
		} catch (ex) {
			captureException(ex as Error | string)
			return { error: ex }
		}
	}

	const schema = z.object({
		email: z.email(),
		firstName: z.string().min(1, 'first name is required'),
		lastName: z.string().min(1, 'last name is required'),
		organization: z.string().min(1, 'organization is required'),
		use: z
			.string()
			.min(1, 'this field is required')
			.refine((use) => use.trim().length > 0, 'this field must not be empty')
	})

	const form = superForm(defaults(zod4(schema)), {
		id: uuid(),
		SPA: true,
		validators: zod4Client(schema),
		onUpdate: async function ({ form }) {
			if (form.valid) {
				const { data } = form
				const { error = null } = await submitUserInfo(data)

				if (error) {
					hasError = true
				} else {
					onContinue()
				}
			}
		}
	})

	const { form: formData, enhance, submitting, delayed } = form
</script>

<Dialog.Root bind:open>
	<Dialog.Content
		showCloseButton={false}
		class={cn('sm:max-w-5xl h-full sm:h-auto pt-4 overflow-auto', { 'sm:max-w-3xl': hasError })}
	>
		<Dialog.Header class="border-b-4 border-b-blue-9 pb-1">
			<Dialog.Title class="text-xl sm:text-2xl">Please tell us about yourself</Dialog.Title>
		</Dialog.Header>

		{#if hasError}
			<Alert title="Uh oh!" class="text-lg">
				<p class="text-base">
					We're sorry, there was an unexpected error submitting your information. We'll try again
					the next time you download.
					<br /><br />
					If this happens again, please <a href={`mailto:${CONTACT_EMAIL}`}>contact us</a>.
				</p>
			</Alert>

			<Dialog.Footer
				class="justify-between sm:justify-between gap-8 border-t border-t-grey-2 pt-4 mt-4"
			>
				<Button variant="secondary" onclick={() => (open = false)}>Cancel</Button>
				<Button onclick={onContinue}>Continue to download anyway</Button>
			</Dialog.Footer>
		{:else}
			<form use:enhance>
				<div class="grid sm:grid-cols-[1fr_2.5fr] gap-8">
					<div class="pt-4">
						<p>We use this information to:</p>
						<ul class="list-disc list-outside mt-2 pl-8 [&>li+li]:mt-2">
							<li>get in touch with you if we discover errors in the data</li>
							<li>provide statistics about how this tool is being used to our funders</li>
							<li>
								better understand how this tool is being used so that we can prioritize improvements
							</li>
						</ul>
					</div>
					<div>
						<div class="grid sm:grid-cols-2 gap-12">
							<div>
								<Field {form} name="email">
									<Control>
										{#snippet children({ props })}
											<Label class="font-bold">Email</Label>
											<Input {...props} bind:value={$formData.email} />
										{/snippet}
									</Control>
									<FieldErrors class="-mt-1 italic" />
								</Field>
								<Field {form} name="firstName" class="mt-6">
									<Control>
										{#snippet children({ props })}
											<Label class="font-bold">First name</Label>
											<Input {...props} bind:value={$formData.firstName} />
										{/snippet}
									</Control>
									<FieldErrors class="-mt-1 italic" />
								</Field>
								<Field {form} name="lastName" class="mt-6">
									<Control>
										{#snippet children({ props })}
											<Label class="font-bold">Last name</Label>
											<Input {...props} bind:value={$formData.lastName} />
										{/snippet}
									</Control>
									<FieldErrors class="-mt-1 italic" />
								</Field>
							</div>

							<div>
								<Field {form} name="use">
									<Control>
										{#snippet children({ props })}
											<Label class="font-bold">How will you use the data?</Label>
											<Textarea {...props} bind:value={$formData.use} class="min-h-48" />
										{/snippet}
									</Control>
									<FieldErrors class="-mt-1 italic" />
								</Field>
							</div>
						</div>
						<Field {form} name="organization" class="w-full mt-4">
							<Control>
								{#snippet children({ props })}
									<Label class="font-bold">Organization</Label>
									<Input {...props} bind:value={$formData.organization} />
								{/snippet}
							</Control>
							<FieldErrors class="-mt-1 italic" />
						</Field>
					</div>
				</div>

				<Dialog.Footer
					class="justify-between sm:justify-between gap-8 border-t border-t-grey-2 pt-4 mt-4"
				>
					<Button variant="secondary" onclick={() => (open = false)}>Cancel</Button>
					<SubmitButton disabled={$delayed || $submitting}>
						{#if $delayed}
							<LoadingIcon class="size-5 motion-safe:animate-spin" />
						{/if}

						Submit
					</SubmitButton>
				</Dialog.Footer>
			</form>
		{/if}
	</Dialog.Content>
</Dialog.Root>
