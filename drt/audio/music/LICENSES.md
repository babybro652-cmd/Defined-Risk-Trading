# DRT Shorts music library: licenses

Every track here is **CC0 1.0 Universal (public domain dedication)**. No attribution
required, commercial use allowed (YouTube monetization included), editing allowed.
License text: https://creativecommons.org/publicdomain/zero/1.0/

Downloaded 2026-10-30 from the Internet Archive item pages below; each item's
`licenseurl` metadata field reads the CC0 1.0 URL. All are instrumental (checked with
faster-whisper: no vocal segments detected).

Files are 75-second excerpts (from the track start, 2 s fade at the end), loudness
normalized to about -19 LUFS, MP3 160 kbps. `add_audio.py` trims them to the video length.

| File | Title | Artist | Album / source item | License |
|---|---|---|---|---|
| aeroplane.mp3 | Aeroplane | Loyalty Freak Music (made for Lack of Color) | LOFI AMBIENT SONGS ! https://archive.org/details/loyalty-freak-music-lofi-ambient-songs | CC0 1.0 |
| sugar_and_coffee.mp3 | Sugar and coffee | Loyalty Freak Music (made for Lack of Color) | LOFI AMBIENT SONGS ! https://archive.org/details/loyalty-freak-music-lofi-ambient-songs | CC0 1.0 |
| this_pain_is_soft.mp3 | This pain is soft but here | Loyalty Freak Music | LOFI AMBIENT SONGS ! https://archive.org/details/loyalty-freak-music-lofi-ambient-songs | CC0 1.0 |
| soft_as_a_dry_pillow.mp3 | Soft as a dry pillow | Loyalty Freak Music | CHILL FOR REAL ! https://archive.org/details/loyalty-freak-music-chill-for-real | CC0 1.0 |
| happy_sadie.mp3 | Happy Sadie | Loyalty Freak Music | CHILL FOR REAL ! https://archive.org/details/loyalty-freak-music-chill-for-real | CC0 1.0 |
| once_more_with_you.mp3 | Once more with you | Loyalty Freak Music | MINIMAL AMBIENT BOUNCE https://archive.org/details/MINIMALAMBIENTBOUNCE | CC0 1.0 |
| old_key.mp3 | Old Key | Loyalty Freak Music | MINIMAL AMBIENT BOUNCE https://archive.org/details/MINIMALAMBIENTBOUNCE | CC0 1.0 |
| waiting_tttt.mp3 | Waiting TTTT | Loyalty Freak Music | MINIMAL AMBIENT BOUNCE https://archive.org/details/MINIMALAMBIENTBOUNCE | CC0 1.0 |
| traveling_in_your_mind.mp3 | Traveling in your mind | Loyalty Freak Music | TO CHILL AND STAY AWAKE https://archive.org/details/LoyaltyFreakMusicTOCHILLANDSTAYAWAKE20170923132621469 (FMA: https://freemusicarchive.org/music/Loyalty_Freak_Music/TO_CHILL_AND_STAY_AWAKE/) | CC0 1.0 |
| cliff_road_chill.mp3 | Cliff Road Chill | Komiku | https://archive.org/details/komiku-cliff-road-chill (FMA: https://freemusicarchive.org/music/Komiku/Helice_Awesome_Dance_Adventure_/cliff-road-chill/) | CC0 1.0 |

`--music synth` in `add_audio.py` renders an original ambient pad (numpy sine chords,
no samples, no third-party material) when a library track can't be used.

## Sources tried that didn't work from the cloud container (10/30)
- Pixabay Music: 403 from the network proxy.
- YouTube Audio Library: needs a signed-in YouTube Studio session, no direct download.
- FreePD.com: site closed.
- Wikimedia Commons (has the same CC0 Komiku / Loyalty Freak tracks): API and
  upload.wikimedia.org rate-limited the shared proxy IP (HTTP 429).

## Content ID note
CC0 tracks can still be registered to Content ID by third parties by mistake. If a Short
gets a claim on one of these, dispute it in YouTube Studio citing the CC0 item page above,
and move the track to the bottom of the rotation.

## AI voice (education Shorts)
`add_audio.py --tts-text` uses Piper TTS (local, free) with voice **en_US-norman-medium**
from https://huggingface.co/rhasspy/piper-voices (model card: dataset LibriVox recordings,
public domain). AI voice means `containsSyntheticMedia: true` on YouTube.
