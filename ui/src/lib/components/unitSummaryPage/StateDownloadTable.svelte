<script lang="ts">
	import DownloadIcon from '@lucide/svelte/icons/download'

	import { resolve } from '$app/paths'
	import { Downloader } from '$lib/components/download'
	import { Button } from '$lib/components/ui/button'
	import * as DropdownMenu from '$lib/components/ui/dropdown-menu'
	import { formatNumber } from '$lib/util/format'

	const downloadConfig = { scenario: 'NCWC', layer: 'State' }

	const { total, states, areaName } = $props()

	const stateIds = $derived(states.map(({ id }: { id: string }) => id))
</script>

<h2 class="text-2xl font-bold mt-24">Statistics by state</h2>

<table
	class="w-full mt-2 [&_th]:px-2 [&_th]:py-4 [&_td]:px-2 [&_td]:py-2 [&_tr+tr]:border-t [&_tr+tr]:border-t-grey-1"
>
	<thead class="font-bold bg-grey-1 border-b-2 border-b-grey-3 text-left">
		<tr>
			<th class="w-[16rem]">State</th>
			<th class="w-48">Inventoried dams</th>
			<th class="w-48">Surveyed road/stream crossings</th>
			<th class="w-48">Unsurveyed road/stream crossings</th>
			<th aria-label="download link column" class="w-24"> </th>
		</tr>
	</thead>
	<tbody>
		{#each states as state (state.id)}
			<tr>
				<td class="font-bold"
					><a href={resolve(`/states/${state.id}`, { id: state.id })}>{state.name}</a></td
				>
				<td>{formatNumber(state.dams)} </td>
				<td>{formatNumber(state.totalSmallBarriers)} </td>
				<td>{formatNumber(state.unsurveyedRoadCrossings)} </td>
				<td>
					<DropdownMenu.Root>
						<DropdownMenu.Trigger class="flex gap-1 items-center text-link cursor-pointer ">
							<DownloadIcon class="size-5" /> Download
						</DropdownMenu.Trigger>
						<DropdownMenu.Content class="w-72" collisionPadding={20}>
							<div>
								<Downloader
									label="Dams"
									barrierType="dams"
									areaName={state.name}
									disabled={state.dams === 0}
									config={{ ...downloadConfig, summaryUnits: { State: [state.id] } }}
									triggerClass="text-sm h-7 hover:no-underline hover:bg-blue-1/50 w-full justify-start"
									triggerVariant="link"
								/>
							</div>
							<div>
								<Downloader
									label="Dams & surveyed crossings"
									barrierType="combined_barriers"
									triggerLabel="dams & surveyed crossings"
									areaName={state.name}
									disabled={state.totalSmallBarriers === 0}
									config={{ ...downloadConfig, summaryUnits: { State: [state.id] } }}
									triggerClass="text-sm h-7 hover:no-underline hover:bg-blue-1/50 w-full justify-start"
									triggerVariant="link"
								/>
							</div>
							<div>
								<Downloader
									label="Surveyed & unsurveyed crossings"
									barrierType="road_crossings"
									triggerLabel="surveyed & unsurveyed crossings"
									areaName={state.name}
									disabled={state.totalSmallBarriers + state.unsurveyedRoadCrossings === 0}
									config={{ ...downloadConfig, summaryUnits: { State: [state.id] } }}
									triggerClass="text-sm h-7 hover:no-underline hover:bg-blue-1/50 w-full justify-start"
									triggerVariant="link"
								/>
							</div>
						</DropdownMenu.Content>
					</DropdownMenu.Root>
				</td>
			</tr>
		{/each}

		<tr class="border-t-2! border-t-grey-3! bg-grey-1/50">
			<td class="font-bold">Total</td>
			<td class="font-bold">{formatNumber(total.dams)} </td>
			<td class="font-bold">{formatNumber(total.totalSmallBarriers)} </td>
			<td class="font-bold">{formatNumber(total.unsurveyedRoadCrossings)} </td>
			<td>
				<DropdownMenu.Root>
					<DropdownMenu.Trigger class="flex gap-1 items-center text-link cursor-pointer">
						<DownloadIcon class="size-5" /> Download
					</DropdownMenu.Trigger>
					<DropdownMenu.Content class="w-72" collisionPadding={20}>
						<div>
							<Downloader
								label="Dams"
								barrierType="dams"
								{areaName}
								disabled={total.dams === 0}
								config={{ ...downloadConfig, summaryUnits: { State: stateIds } }}
								triggerClass="text-sm h-7 hover:no-underline hover:bg-blue-1/50 w-full justify-start"
								triggerVariant="link"
							/>
						</div>

						<div>
							<Downloader
								label="Dams & surveyed road crossings"
								barrierType="combined_barriers"
								triggerLabel="dams & surveyed crossings"
								{areaName}
								disabled={total.totalSmallBarriers === 0}
								config={{ ...downloadConfig, summaryUnits: { State: stateIds } }}
								triggerClass="text-sm h-7 hover:no-underline hover:bg-blue-1/50 w-full justify-start"
								triggerVariant="link"
							/>
						</div>

						<div>
							<Downloader
								label="Surveyed & unsurveyed road crossings"
								barrierType="road_crossings"
								triggerLabel="surveyed & unsurveyed crossings"
								{areaName}
								disabled={total.totalSmallBarriers + total.unsurveyedRoadCrossings === 0}
								config={{ ...downloadConfig, summaryUnits: { State: stateIds } }}
								triggerClass="text-sm h-7 hover:no-underline hover:bg-blue-1/50 w-full justify-start"
								triggerVariant="link"
							/>
						</div>
					</DropdownMenu.Content>
				</DropdownMenu.Root>
			</td>
		</tr>
	</tbody>
</table>

<div class="grid sm:grid-cols-2 gap-8 mt-8 text-muted-foreground text-sm">
	<div>
		<b>{formatNumber(total.dams - total.rankedDams, 0)} inventoried dams</b> and
		<b>
			{formatNumber(total.smallBarriers - total.rankedSmallBarriers, 0)} surveyed road/stream crossings
		</b>
		were not analyzed because they could not be correctly located on the aquatic network or were otherwise
		excluded from the analysis. You can optionally include these in your download.
	</div>
	<div>
		Note: These statistics are based on inventoried dams and surveyed road/stream crossings. Because
		the inventory is incomplete in many areas, areas with a high number of dams or surveyed
		road/stream crossings may simply represent areas that have a more complete inventory.
	</div>
</div>
