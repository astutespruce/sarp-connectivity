import { fileURLToPath } from 'node:url'
import js from '@eslint/js'
import { loadConfig } from '@sveltejs/load-config'
import oxlint from 'eslint-plugin-oxlint'
import svelte from 'eslint-plugin-svelte'
import { includeIgnoreFile, defineConfig } from 'eslint/config'
import globals from 'globals'
import ts from 'typescript-eslint'

const gitignorePath = fileURLToPath(new URL('../.gitignore', import.meta.url))
const svelteConfig = (await loadConfig('./', { traverse: false }))?.config

export default defineConfig(
	includeIgnoreFile(gitignorePath),
	js.configs.recommended,
	...ts.configs.recommended,
	...svelte.configs.recommended,
	// TS/JS already checked by oxlint
	{ ignores: ['**/*.ts', '**/*.js'] },
	{
		languageOptions: {
			globals: { ...globals.browser, ...globals.node }
		},
		rules: {
			'no-undef': 'off',
			// does not detect assignment correctly
			'no-useless-assignment': 'off',
			'svelte/no-navigation-without-resolve': 'warn',
			'@typescript-eslint/no-unused-vars': ['error', { varsIgnorePattern: '^_' }]
		}
	},
	{
		files: ['**/*.svelte', '**/*.svelte.ts', '**/*.svelte.js'],
		languageOptions: {
			parserOptions: {
				projectService: true,
				extraFileExtensions: ['.svelte'],
				parser: ts.parser,
				svelteConfig
			}
		}
	},
	// turn off rules already handled by oxlint
	oxlint.configs['flat/recommended']
)
