import path from 'path'
import tailwindcss from '@tailwindcss/vite'
import { sveltekit } from '@sveltejs/kit/vite'
import { defineConfig } from 'vite'
import { enhancedImages } from '@sveltejs/enhanced-img'
import { config as dotEnvConfig } from 'dotenv'

// have to configure dotenv to load correct .env file
dotEnvConfig({ path: `.env.${process.env.NODE_ENV}` })

export default defineConfig({
	plugins: [tailwindcss(), enhancedImages(), sveltekit()],
	server: {
		fs: {
			allow: [path.resolve(__dirname, './package.json')]
		}
	}
})
