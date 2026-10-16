// Combine the three Vite builds into one static output dir for Vercel:
//   dist/            <- Landing   (served at /)
//   dist/citizen/    <- Frontend  (served at /citizen/)
//   dist/officer/    <- OfficerFrontend (served at /officer/)
import { cpSync, rmSync, mkdirSync } from 'node:fs'

rmSync('dist', { recursive: true, force: true })
mkdirSync('dist', { recursive: true })
cpSync('Landing/dist', 'dist', { recursive: true })
cpSync('Frontend/dist', 'dist/citizen', { recursive: true })
cpSync('OfficerFrontend/dist', 'dist/officer', { recursive: true })
