import { combinedBarriers } from './combinedBarriers'
import { dams } from './dams'
import { roadCrossings } from './roadCrossings'
import { smallBarriers } from './smallBarriers'

const filters = {
	dams,
	small_barriers: smallBarriers,
	combined_barriers: combinedBarriers,
	largefish_barriers: combinedBarriers,
	smallfish_barriers: combinedBarriers,
	road_crossings: roadCrossings
}

export { filters }
