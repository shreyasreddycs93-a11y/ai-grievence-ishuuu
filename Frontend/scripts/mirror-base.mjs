// Vercel services: copy the build into dist/citizen/ as well, so assets resolve
// whether or not the platform strips the "/citizen" route prefix before serving.
import { cpSync, readdirSync, mkdirSync } from 'node:fs'

const prefix = 'citizen'
mkdirSync(`dist/${prefix}`, { recursive: true })
for (const name of readdirSync('dist')) {
  if (name !== prefix) cpSync(`dist/${name}`, `dist/${prefix}/${name}`, { recursive: true })
}
