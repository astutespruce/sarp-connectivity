<script lang="ts">
	import DownloadIcon from '@lucide/svelte/icons/download'
	import { onMount } from 'svelte'

	import { shortBarrierTypeLabels } from '$lib/config/constants'
	import { getFromStorage } from '$lib/util/dom'

	import { Button } from '$lib/components/ui/button'

	import DownloadPopup from './DownloadPopup.svelte'
	import UserInfoPopup from './UserInfoPopup.svelte'
	import { cn } from '$lib/utils'

	const {
		barrierType,
		areaName = null,
		config = {},
		customRank = false,
		label,
		disabled = false,
		showOptions = true,
		includeUnranked = false,
		triggerLabel = null,
		triggerClass = null
	} = $props()

	let isUserInfoPopupOpen: boolean = $state(false)
	let isDownloadPopupOpen: boolean = $state(false)
	let needUserInfo: boolean = $state(true)

	const barrierTypeLabel = $derived(
		shortBarrierTypeLabels[barrierType as keyof typeof shortBarrierTypeLabels]
	)

	onMount(() => {
		// If the user previously entered their contact info, don't ask them for it again
		const formData = getFromStorage('downloadForm')
		if (formData && Object.entries(formData).length > 0) {
			needUserInfo = false
		}
	})

	const show = () => {
		if (disabled) {
			return
		}

		if (needUserInfo) {
			isUserInfoPopupOpen = true
		} else {
			isDownloadPopupOpen = true
		}
	}

	const handleUserInfoContinue = () => {
		needUserInfo = false
		isUserInfoPopupOpen = false
		isDownloadPopupOpen = true
	}
</script>

<Button {disabled} onclick={show} class={cn('', triggerClass)}>
	<DownloadIcon class="size-5" />
	{triggerLabel || barrierTypeLabel}
</Button>

{#if needUserInfo}
	<UserInfoPopup bind:open={isUserInfoPopupOpen} onContinue={handleUserInfoContinue} />
{:else}
	<DownloadPopup
		bind:open={isDownloadPopupOpen}
		{barrierType}
		{label}
		{areaName}
		{config}
		{includeUnranked}
		{customRank}
		{showOptions}
	/>
{/if}
