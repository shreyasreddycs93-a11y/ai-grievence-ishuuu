// Vercel services: copy the build into dist/officer/ as well, so assets resolve
// whether or not the platform strips the "/officer" route prefix before serving.
import { cpSync, readdirSync, mkdirSync } from 'node:fs'

const prefix = 'officer'
mkdirSync(`dist/${prefix}`, { recursive: true })
for (const name of readdirSync('dist')) {
  if (name !== prefix) cpSync(`dist/${name}`, `dist/${prefix}/${name}`, { recursive: true })
}
