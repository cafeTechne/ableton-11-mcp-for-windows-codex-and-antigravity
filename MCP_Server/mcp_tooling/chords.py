#!/usr/bin/env python3

# Extended version of free-midi-chords progression database
# Original by Ludovic Drolez (2019-2025) - MIT License
# Extensions with cited sources added 2026

# ORIGINAL PROGRESSIONS (from ldrolez/free-midi-chords)
# ========================================================

prog_maj = [
    "I I IM-5 IM-5 IV IV V Vsus2 =Joyful Triumphant =Pop",
    "I I IV iii =Hopeful Nostalgic =Pop",
    "I I7 Idom7 I7 =Relaxed Playful =Blues",
    "I I7 Idom7 IV =Relaxed Nostalgic =Blues",
    "I iii IV vi =Romantic Nostalgic =Pop",
    "I iii vi Isus4 =Tender Spiritual =Pop Ballad",
    "I iii vi IV =Romantic Hopeful =Pop",
    "I IV ii V =Joyful Triumphant =Pop Rock",
    "I IV Isus2 IV =Peaceful Hopeful =Pop",
    "I IV V IV =Joyful Triumphant =Rock",
    "I IV V V =Joyful Excited =Rock",
    "I IV vi V =Joyful Hopeful =Pop",
    "I IV vii iii vi ii V I =Romantic Triumphant =Pop Ballad",
    "I V I IV =Joyful Playful =Pop Rock",
    "I V IV vi =Romantic Hopeful =Pop",
    "I V vi ii =Hopeful Romantic =Pop",
    "I V vi iii IV I IV V =Hopeful Joyful =Pop",
    "I V vi iii IV =Hopeful Joyful =Pop",
    "I V vi IV =Hopeful Romantic =Pop",
    "I V vi V =Hopeful Romantic =Pop",
    "I vi I IV =Tender Nostalgic =Pop",
    "I vi ii IV =Tender Nostalgic =Pop",
    "I vi ii V =Nostalgic Romantic =Pop",
    "I vi IV iii =Nostalgic Romantic =Pop",
    "I vi IV V =Romantic Hopeful =Pop",
    "I7 V7 viadd9 IV7 =Playful Joyful =Pop Funk",
    "ii IV V V =Hopeful =Pop",
    "ii IV vi V =Romantic =Pop",
    "ii V I I =Triumphant =Jazz",
    "ii V I IV =Hopeful Triumphant =Pop",
    "ii7 Vadd9 I7 I7 =Triumphant =Jazz",
    "iii vi IV I =Romantic Nostalgic =Pop",
    "iim7 V7 iiim7 vi7 iim7 V7 =Romantic Nostalgic =Jazz",
    "Isus2 I vi7 visus4 =Playful Romantic =Pop",
    "IV I ii vi =Nostalgic Peaceful =Pop",
    "IV I iii IV =Playful Joyful =Pop",
    "IV I IV6 Iadd9 =Relaxed Joyful =Pop",
    "IV I V vi =Joyful Romantic =Pop",
    "IV IV I V =Joyful Hopeful =Rock",
    "IV vi I V =Hopeful Romantic =Pop",
    "IV vi iii I =Nostalgic Playful =Pop",
    "IV vi IV vi =Nostalgic =Pop",
    "V I vi V =Hopeful Romantic =Pop",
    "V IV vi I =Hopeful Triumphant =Pop",
    "V vi IV I =Hopeful Romantic =Pop",
    "vi ii V I =Hopeful Romantic =Pop",
    "vi IV I V =Hopeful Romantic =Pop",
    "vi V IV V ii V I I =Triumphant Hopeful =Pop",
    "vi V IV V =Romantic Hopeful =Pop",
]

prog_min = [
    "i i iv iv v7 ii5 v v7 =Dark Mysterious",
    "i ii v i =Mysterious Triumphant",
    "i III iv VI =Nostalgic Romantic",
    "i III VII VI =Nostalgic Romantic",
    "i ii v III i ii v VII =Mysterious Dramatic",
    "i iv III VI =Nostalgic Romantic",
    "i iv v iv =Mysterious Sad",
    "i iv v v =Sad Lonely",
    "i iv VI v =Sad Hopeful",
    "i iv VII i =Sad Nostalgic",
    "i iv VII v i i ii V =Mysterious Surprised",
    "i v iv VII =Sad Rebellious",
    "i vdim iv VI =Dark Nostalgic",
    "i VI III VII i VI69 III7 VII =Mysterious Spiritual",
    "i VI III VII =Nostalgic Hopeful",
    "i VI iv ii =Sad Tender",
    "i VI iv III =Sad Nostalgic",
    "i VI iv v =Sad Hopeful",
    "i VI VII iv =Mysterious Nostalgic",
    "i VI VII v =Mysterious Rebellious",
    "i VI VII VII =Triumphant Rebellious",
    "i VII i v III VII i v i =Mysterious Surprised",
    "i VII i v =Mysterious Nostalgic",
    "i VII III VI =Rebellious Triumphant",
    "i VII v VI =Mysterious Hopeful",
    "i VII VI III iv VI VII i =Mysterious Surprised",
    "i VII VI III =Nostalgic Hopeful",
    "i VII VI iv =Sad Romantic",
    "i VII VI VII =Rebellious Triumphant",
    "i7 VI III7 VII6 i i7 III7 iv7 =Dark Nostalgic",
    "i7 VII VI7 iv7 =Nostalgic Romantic",
    "ii v i i =Peaceful Hopeful",
    "ii v i iv =Peaceful Nostalgic",
    "ii VI i iv =Sad Hopeful",
    "im7 ivsus4 v7 isus4 =Mysterious Tender",
    "iv i v VI =Nostalgic Hopeful",
    "iv III VII i =Nostalgic Mysterious",
    "iv III vsus4 VI iv i III VI =Nostalgic Mysterious",
    "iv v VI VII =Mysterious Rebellious",
    "iv VI v VII =Mysterious Hopeful",
    "iv VI VII i =Triumphant",
    "v i iv VII =Dark Rebellious",
    "v iv i i =Lonely",
    "v VI III i =Hopeful Nostalgic",
    "v VI v i =Sad",
    "VI i v III =Hopeful Nostalgic",
    "VI i v v =Sad",
    "VI III i v =Nostalgic Dark",
    "VI iv i v =Hopeful Tender",
    "VI VI i VII =Empowered",
    "VI VII i III =Triumphant Nostalgic",
    "VI VII v III =Rebellious Nostalgic",
    "VII iv v i =Mysterious Dark",
    "VII iv VII i =Spiritual",
]

prog_modal = [
    "bIIIM ii bIIM I =Mysterious Surprised",
    "bIIM bVIM biii bviim =Mysterious Surprised",
    "bIIM ivm biii im =Mysterious Dark",
    "bVIIM bIIM bIIIM im =Mysterious Rebellious",
    "bVIM bIIIM bVIIM IV I =Triumphant Mysterious",
    "bVIM bVIIm im bIIM =Mysterious Dark",
    "bVIM vi im bVIIM =Hopeful Mysterious",
    "bVIM7 ivmadd9 I I =Spiritual Nostalgic",
    "I7 bIdom7 III7 ii7 V7 =Playful Surprised",
    "I bIIIM bVIIM I =Triumphant Rebellious",
    "I bIIIM bVIIM IV =Triumphant Mysterious",
    "I bIIIM bVIM bVIIM =Triumphant Hopeful",
    "I bIIIM IV I =Romantic",
    "I bIIM I iii =Surprised Mysterious",
    "I bIIM7 bIIIM6 bIIM7 I im bVIIM bIIM =Surprised Mysterious",
    "I bVIIM bVIM bIIM =Triumphant Rebellious",
    "I bVIIM bVIM IV IVsus4 IV =Hopeful Nostalgic",
    "I bVIIM I I bVIM V =Triumphant Hopeful",
    "I bVIIM IV V =Joyful Triumphant",
    "I bVIM I bIIM =Surprised Mysterious",
    "I bVIM IV bIIIM bVIIM =Mysterious Nostalgic",
    "I I7 I9 IV ivm =Romantic Nostalgic",
    "I I7 Idom7 IV ivm I =Relaxed Nostalgic",
    "I I7 Idom7 IV ivm I ivm6 Vdom7 =Relaxed Romantic",
    "I IIIM vi V =Joyful Hopeful",
    "I IIM iii V6 =Surprised Triumphant",
    "I IIM IV I =Joyful Triumphant",
    "I IV bIIIM bVIM =Nostalgic Mysterious",
    "I IV bVIIM IV =Joyful Rebellious",
    "I IV V bVIIM =Triumphant Rebellious",
    "I ivm bIIIM bVIIM =Mysterious Nostalgic",
    "I V bVIIM IV =Triumphant Rebellious",
    "I V ivm bVIM =Surprised Mysterious",
    "I5 iii II5 #IVm IV5 vi V5 viim =Excited Triumphant",
    "ii bIIM I bVIIM =Mysterious Rebellious",
    "ii bVIIM7 I =Hopeful Triumphant",
    "ii IVM vm bVIIM =Mysterious Nostalgic",
    "IIIM V VIsus4 VIM I IIM =Triumphant Surprised",
    "im bIIIM bVIIM IV =Romantic Nostalgic",
    "im bIIIM bVIM V =Mysterious Triumphant",
    "im bIIIM IV bVIM =Mysterious Hopeful",
    "im bIIIsus2 IV IV =Mysterious Peaceful",
    "im bIIM bIIIM bIIM =Mysterious Dark",
    "im bIIM biim6 ivm =Mysterious Tender",
    "im bIIM im7 bviim =Mysterious Spiritual",
    "im bIIM ivm IIIM bIIM ivm IIIM IIIM =Mysterious Nostalgic",
    "im bIIM vm im7 =Mysterious Dark",
    "im bVIIM bIIM vm =Mysterious Rebellious",
    "im bviim bVIM bIIM =Mysterious Hopeful",
    "im bVIM ivm V =Triumphant",
    "im ii vm IV =Nostalgic Hopeful",
    "im ivm9 bIIM im vm ivm7 bIIM im7 =Mysterious Tender",
    "im ivm9 bIIM im =Mysterious Nostalgic",
    "im V bVIIM IV bVIM bIIIM ivm V =Mysterious Rebellious",
    "im VIM bi V =Mysterious Triumphant",
    "im VIM IIIM bIIM =Nostalgic Surprised",
    "im vm isus4 I =Hopeful Spiritual",
    "im vm bVIM bIIM =Mysterious Hopeful",
    "im vm ivm bIIM7 =Mysterious Dark",
    "IV V ii im bIIIM IV =Hopeful Nostalgic",
    "ivm bIIIM iim7 V =Mysterious Tender",
    "ivm im bviim bVIM =Dark",
    "vdim vdim ivm bIIIM =Fearful Mysterious",
    "vi bVIM bVIIM I =Hopeful Triumphant",
    "vi IV I IIM =Hopeful Peaceful",
    "vi viim V vi #IVdim V =Nostalgic Dark",
    "VIM bVIM im bVIIM =Surprised Rebellious",
    "bIIIM V7 I =Cadence",
    "bVIIM V7 I =Cadence",
    "im bVIIM IV im =Cadence",
    "ivm bIIIM bIIM I =Cadence",
    "ivm IIIM bIIM I =Cadence",
    "ivm bIIIM bVIM I =Cadence",
]

# NEW ADDITIONS WITH CITATIONS
# ========================================================

# JAZZ PROGRESSIONS
# Primary Sources: Wikipedia, Open Music Theory, Puget Sound, Free Jazz Lessons
prog_jazz = [
    # Basic ii-V-I (most fundamental jazz progression)
    "iim7 V7 IM7 =Jazz Sophisticated @Wikipedia:ii-V-I",
    "iim7 V7 IM7 IM7 =Jazz Romantic @OpenMusicTheory:ii-V-I",
    
    # Jazz turnarounds (ending phrases that return to tonic)
    "IM7 vim7 iim7 V7 =Jazz Nostalgic @Wikipedia:Turnaround",
    "I VI7 II7 V7 =Jazz Playful @Wikipedia:Turnaround",  # Dominant turnaround
    "IM7 vim7 iim7 bII7 =Jazz Smooth @Wikipedia:Turnaround",  # Tritone sub
    "iiim7 VI7 iim7 V7 =Jazz Sophisticated @PugetSound:Progressions",  # Extended turnaround
    "IM7 bIIIM7 bVIM7 bIIM7 =Jazz Dreamy @FreeJazzLessons:Turnarounds",  # "Lady Bird" changes
    "I bIIIdim7 ii V =Jazz Vintage @FreeJazzLessons:Turnarounds",  # Swing era diminished
    "I bIII7 II7 bII7 =Jazz Chromatic @FreeJazzLessons:Turnarounds",  # Tritone chain
    
    # Minor ii-V-i 
    "iim7b5 V7 im7 =Jazz Dark @OpenMusicTheory:ii-V-I",
    "iim7b5 V7b9 im7 =Jazz Mysterious @OpenMusicTheory:ii-V-I",
    
    # Autumn Leaves progression (diatonic cycle)
    "iim7 V7 IM7 IVM7 viim7b5 III7 vim7 vim7 =Jazz Nostalgic @LearnJazzStandards:AutumnLeaves",
    "iim7b5 V7 im7 im7 ivm7 VII7 IIIM7 VIM7 =Jazz Melancholic @JazzVideoLessons:AutumnLeaves",
]

# BLUES PROGRESSIONS  
# Sources: Wikipedia, LANDR, BassBuzz
prog_blues = [
    # Standard 12-bar blues
    "I7 I7 I7 I7 IV7 IV7 I7 I7 V7 IV7 I7 I7 =Blues Confident @Wikipedia:12-bar",
    
    # Quick change/Quick IV (IV in bar 2)
    "I7 IV7 I7 I7 IV7 IV7 I7 I7 V7 IV7 I7 I7 =Blues Driving @Wikipedia:12-bar",
    
    # Quick V (V in bar 2)
    "I7 V7 I7 I7 IV7 IV7 I7 I7 V7 IV7 I7 I7 =Blues Energetic @BassBuzz:12-bar",
    
    # Jazz blues (with ii-V substitutions)
    "I7 IV7 I7 VI7 iim7 V7 I7 VI7 iim7 V7 I7 V7 =Jazz-Blues Sophisticated @Wikipedia:12-bar",
    
    # Minor blues
    "im7 im7 im7 im7 ivm7 ivm7 im7 im7 bVI7 V7 im7 im7 =Blues Melancholic @LANDR:MinorBlues",
]

# POP/ROCK PROGRESSIONS
# Sources: Berklee, Musician's Toolshed, Fretwise
prog_pop = [
    # "Axis" progression (most popular pop progression)
    "I V vi IV =Pop Anthemic @MusiciansToolshed:AxisProgression",
    "I V vi IV =Rock Uplifting @Berklee:CommonProgressions",
    
    # Axis variations (same chords, different order)
    "vi IV I V =Pop Melancholic @Berklee:CommonProgressions",
    "IV I V vi =Pop Nostalgic @Fretwise:I-V-vi-IV",
    "IV vi I V =Pop Hopeful @PopChordProgressions",
    
    # Doo-wop/50s progression  
    "I vi IV V =Pop Nostalgic @Berklee:CommonProgressions",
    "I vi IV V =Doo-wop Romantic @Wikipedia:Turnaround",
    
    # 50s progression
    "I vim IV V =Rock-n-Roll Joyful @Berklee:CommonProgressions",
]

# PACHELBEL/CANON PROGRESSIONS
# Source: Berklee
prog_canon = [
    # Full Pachelbel Canon (used in 100s of songs)
    "I V vi iii IV I IV V =Classical Romantic @Berklee:Canon",
    
    # Shortened "Canon" used in pop
    "I V vi iii =Pop Nostalgic @Berklee:Canon",  # Green Day "Basket Case"
]

# ANDALUSIAN CADENCE (Flamenco/Metal/Rock)
# Sources: Wikipedia, Guitar Endeavor, Signals Music Studio, Guitar Lobby
prog_andalusian = [
    # Minor Andalusian cadence (i-bVII-bVI-V)
    "im bVII bVI V =Flamenco Passionate @Wikipedia:Andalusian",
    "im bVII bVI V =Metal Dark @SignalsMusicStudio:Andalusian", 
    "im bVII bVI V =Rock Melancholic @GuitarEndeavor:Andalusian",
    
    # Major version (descending)
    "vim V IV III =Pop Dramatic @Songtive:Andalusian",
    
    # Variation ending on bVII (Led Zeppelin style)
    "im bVII bVI bVII =Rock Driving @GuitarLobby:MinorProgressions",
]

# GOSPEL PROGRESSIONS
# Sources: Pianote, PianoGroove, Unison Audio, eMastered, Greg Howlett
prog_gospel = [
    # Gospel ii-V-I (fundamental gospel progression)
    "iim7 V7 I I =Gospel Uplifting @eMastered:GospelChords",
    
    # Gospel I-IV with chromatic iv
    "I I7 IV ivm =Gospel Nostalgic @Pianote:GospelProgressions",
    "I I7 IV ivm I =Gospel Emotional @PianoGroove:GospelIntros",
    
    # Gospel turnaround with secondary dominants
    "I VI7 iim7 V7 =Gospel Soulful @GregHowlett:SecondaryDominants",
    "IM7 III7 vim7 iim7 V7 I =Gospel Triumphant @Unison:GospelProgressions",
    
    # Gospel I-IV-V with chromatic passing
    "I IV #ivm7b5 V =Gospel Smooth @Pianote:GospelProgressions",  # Chromatic walkup
    
    # Gospel plagal (Amen) cadences
    "IV I =Gospel Peaceful @eMastered:GospelChords",
    "IV ivm I =Gospel Tender @Pianote:GospelProgressions",  # Double plagal
    
    # Gospel walk-up/walk-down
    "I I7 IV V7/IV V7 I =Gospel Bluesy @PSRTutorial:GospelWalkup",
]

# BOSSA NOVA PROGRESSIONS
# Sources: Learn Jazz Standards, Piano With Jonny, Bossa Nova Guitar, Musicogram
prog_bossa = [
    # "Jobim progression" (Girl from Ipanema A-section, Take the A Train)
    "IM7 IM7 II7 II7 iim7 V7 IM7 IM7 =Bossa-Nova Dreamy @PianoWithJonny:JobimProgression",
    "IM7 II7#11 iim7 bII7 IM7 IM7 =Bossa-Nova Smooth @LearnJazzStandards:BossaNovaProgressions",
    
    # Girl from Ipanema bridge (modulation sequence)
    "IVM7 V7 IV7 bIII7 IIIM7 VI7 iim7 V7 =Bossa-Nova Romantic @LearnJazzStandards:GirlFromIpanema",
    
    # Basic bossa ii-V-I with extensions
    "iim9 V13 IM9 =Bossa-Nova Sophisticated @BossaNovaGuitarre:Chords2",
    "iim9 V13 V7b13 IM9 =Bossa-Nova Elegant @BossaNovaGuitarre:Chords2",  # With voice leading
    
    # One Note Samba / Samba de Uma Nota Só
    "im7 im7 iim7b5 V7b9 =Bossa-Nova Melancholic @Musicogram:BossaProgressions",
]

# COUNTRY PROGRESSIONS
# Sources: eMastered, Guitar Chords Library, Powers of 10, Guitar Lobby
prog_country = [
    "I IV V =Country Joyful @eMastered:CountryProgressions",
    "I IV V I =Country Triumphant @GuitarChordsLibrary:Country",
    "I IV V IV =Country Driving @PowersOf10:Country",
    "I V vi IV =Country Anthemic @PowersOf10:Country",
    "I vi IV V =Country Nostalgic @PowersOf10:Country",
    "I I I I IV IV I I V IV I I =Country-Blues Traditional @eMastered:CountryProgressions",
    "I IV I IV V IV I V =Country Bouncy @GuitarChordsLibrary:Country",
    "I III IV I =Country Bright @GuitarMasterclass:Country-III-IV",
]

# REGGAE PROGRESSIONS
# Sources: Splice, Wayne & Wax, Unison Audio, Riffhard
prog_reggae = [
    "I iim =Reggae Laid-back @Splice:ReggaeProgressions",
    "I bVII =Reggae Groovy @Splice:ReggaeProgressions",
    "vim V =Reggae Dark @Splice:ReggaeProgressions",
    "I IV V =Reggae Confident @WayneAndWax:RootsRiddim",
    "I IV I V =Reggae Hypnotic @Unison:ReggaeProgressions",
    "I IV =Reggae Smooth @Unison:ReggaeProgressions",
    "I ii =Reggae Mellow @Riffhard:ReggaeGuitar",
]

# SKA PROGRESSIONS
# Sources: eHow UK, NYC Guitar School, Guitar Tricks
prog_ska = [
    "I IV V I =Ska Upbeat @eHow:SkaProgressions",
    "I iim V I =Ska Energetic @eHow:SkaProgressions",
    "I vim IV V I =Ska Joyful @eHow:SkaProgressions",
    "I iim IV V =Ska Driving @GuitarMasterclass:Ska",
]

# R&B / NEO-SOUL PROGRESSIONS
# Sources: eMastered, Pickup Music, ChordChord, Native Instruments, Music Gateway
prog_rnb_neosoul = [
    "iim7 V7 IM7 =Neo-Soul Sophisticated @eMastered:NeoSoul",
    "iim7 V7 IM7 VIM7 =R&B Smooth @ChordChord:RnBProgressions",
    "im9 ivm9 vm9 =Neo-Soul Jazzy @PickupMusic:NeoSoul",
    "I I7 IV ivm =R&B Emotional @ChordChord:RnBProgressions",
    "IM7 III7 vim7 iim7 V7 =Neo-Soul Complex @MusicGateway:NeoSoul",
    "iiim vim iim V =Neo-Soul Flowing @ChordChord:RnBProgressions",
    "IM9 IM9 =Neo-Soul Meditative @eMastered:NeoSoul",
    "I ivm IM7 =R&B Nostalgic @NativeInstruments:RnB",
]

# EDM / ELECTRONIC PROGRESSIONS
# Sources: LANDR, Native Instruments, Unison, Top Music Arts, Melodics
prog_edm = [
    "I V vim IV =EDM Euphoric @NativeInstruments:EDM",
    "vim IV I V =EDM Anthemic @TopMusicArts:EDM",
    "im VI iv VII =EDM Dark @Unison:EDMProgressions",
    "im bVII bVI V =EDM Intense @Unison:EDMProgressions",
    "I V vim iiim IV I IV V =EDM Epic @SideNoize:EDMProgressions",
    "im im =Techno Hypnotic @LANDR:EDM",
    "V I =House Powerful @LANDR:EDM",
    "I IV V IV =Deep-House Groovy @Samplesound:EDMProgressions",
    "I vim IV V =Trance Nostalgic @SideNoize:EDMProgressions",
]

# METAL PROGRESSIONS
# Sources: Pickup Music, Riffhard, Metal Mastermind, Fundamental Changes
prog_metal = [
    "im bVII bVI =Metal Aggressive @PickupMusic:MetalChords",
    "i bVII bVI bVII =Metal Driving @Riffhard:MetalProgressions",
    "i bII bIII bII =Metal Dark @FundamentalChanges:Phrygian",
    "im bIIM ivm =Metal Mysterious @MetalMastermind:Theory",
    "i5 i5 bVI5 bVII5 =Metal Heavy @PickupMusic:MetalChords",
    "i5 bIII5 bVI5 bVII5 =Metal Epic @Riffhard:MetalProgressions",
    "isus2 bVIsus2 bVIIsus2 =Djent Angular @PickupMusic:MetalChords",
    "i5 bV5 =Metal Dissonant @PickupMusic:MetalChords",
    "i bII III ivm =Prog-Metal Exotic @CreativeGuitarStudio:ProgMetal",
]

# CINEMATIC / EPIC PROGRESSIONS
# Sources: PianoWithJonny, Composer Focus, Spitfire Audio, Evenant
prog_cinematic = [
    # Hans Zimmer / Inception style (Dorian motion)
    "im vm VII IV =Cinematic Heroic @FilipeLeitao:Inception",
    "im bVI bIII bVII =Cinematic Epic @ComposerFocus:HansZimmer", # "Time" variation
    
    # Chromatic Mediants (Fantasy/Sci-Fi)
    "I bIII =Cinematic Fantasy @PianoWithJonny:Cinematic",
    "I bVI =Cinematic Wonder @PianoWithJonny:Cinematic",
    "im bviim =Cinematic Mystery @PianoWithJonny:Cinematic",
    
    # Epic / Trailer
    "i bVI bVII i =Cinematic Gladiator @FilipeLeitao:Gladiator",
    "im bVI bIII bVII =Cinematic Emotional @Landr:Interstellar",
    "i IV V i III VI i V V i =Cinematic SpaceOpera @Landr:StarWars", # Force Theme
    
    # Emotional / Poignant
    "vi IV I V =Cinematic Emotional @eMastered:Epic",
    "I iv I iv II vi i VI iv V =Cinematic Bittersweet @eMastered:LeiasTheme",
    "im VI v i VI III im =Cinematic Pirate @Landr:Pirates",
]

# LO-FI HIP HOP PROGRESSIONS
# Sources: Produce Like A Pro, LoFi Weekly, Unison Audio
prog_lofi = [
    # Jazz-influenced extensions
    "IM7 vim7 iim7 V7 =Lo-Fi Chill @RichardPryn:LofiChords",
    "IM9 vim9 iim9 V13 =Lo-Fi Jazzy @RichardPryn:LofiChords",
    "IM7 IVM7 =Lo-Fi Nostalgic @Unison:LofiProgressions",
    
    # Minor moods
    "im7 ivm7 =Lo-Fi Mellow @LoFiWeekly:Chords",
    "im9 ivm7 vm7 =Lo-Fi Night @LoFiWeekly:Chords",
    "im11 bVIIM11 bVIM11 vm11 =Lo-Fi Sad @YouTube:LofiTheory", # Descending minor 11s
    
    # Modal interchange
    "IM7 vim7 bVI7 V7 =Lo-Fi Dreamy @LoFiWeekly:Chords",
    "iim7 V7 IM7 ivm7 =Lo-Fi Sentimental @Unison:LofiProgressions",
    "IM9 G7#5 im11 IVM9 =Lo-Fi Complex @Unison:LofiProgressions",
    "im11 bIIm11 =Lo-Fi Parallel @YouTube:LofiTheory",
]

# Combine all progressions
prog_all_extended = {
    'major': prog_maj,
    'minor': prog_min,
    'modal': prog_modal,
    'jazz': prog_jazz,
    'blues': prog_blues,
    'pop': prog_pop,
    'canon': prog_canon,
    'andalusian': prog_andalusian,
    'gospel': prog_gospel,
    'bossa_nova': prog_bossa,
    'country': prog_country,
    'reggae': prog_reggae,
    'ska': prog_ska,
    'rnb_neosoul': prog_rnb_neosoul,
    'edm': prog_edm,
    'metal': prog_metal,
    'cinematic': prog_cinematic,
    'lofi': prog_lofi,
}

# SOURCES/CITATIONS
# ========================================================
SOURCES = {
    # Jazz theory sources
    '@Wikipedia:ii-V-I': 'Wikipedia - ii–V–I progression (2025)',
    '@Wikipedia:12-bar': 'Wikipedia - Twelve-bar blues (2026)',
    '@Wikipedia:Turnaround': 'Wikipedia - Turnaround (music) (2025)',
    '@Wikipedia:Andalusian': 'Wikipedia - Andalusian cadence (2026)',
    '@OpenMusicTheory:ii-V-I': 'Open Music Theory - ii–V–I progression (2021)',
    '@PugetSound:Progressions': 'Puget Sound Music Theory - Standard Chord Progressions',
    '@FreeJazzLessons:Turnarounds': 'Free Jazz Lessons - 4 Jazz Turnarounds (2023)',
    '@LearnJazzStandards:AutumnLeaves': 'Learn Jazz Standards - Autumn Leaves Chords (Aug 2024)',
    '@JazzVideoLessons:AutumnLeaves': 'Jazz Video Lessons - Autumn Leaves Guide (Nov 2025)',
    '@RichardPryn:LofiChords': 'Richard Pryn - Lofi Chords Theory (2024)',
    '@LoFiWeekly:Chords': 'LoFi Weekly - Chord Progressions Guide',
    '@YouTube:LofiTheory': 'YouTube - Lofi Hip Hop Music Theory',
    
    # Blues sources
    '@LANDR:MinorBlues': 'LANDR Blog - 12 Bar Blues Explained (2025)',
    '@BassBuzz:12-bar': 'BassBuzz Forum - Common 12-Bar Blues Progressions (2025)',
    
    # Pop/Rock sources
    '@MusiciansToolshed:AxisProgression': "Musician's Toolshed - I V vi IV: Ultimate Pop Progression (2020)",
    '@Berklee:CommonProgressions': 'Berklee Online - Common Chord Progressions (2025)',
    '@Berklee:Canon': 'Berklee Online - Pachelbel Canon Progression',
    '@Fretwise:I-V-vi-IV': 'Fretwise - Common Chord Progressions: I V vi IV (2024)',
    '@PopChordProgressions': 'From the Woodshed - Pop Chord Progressions (2011)',
    
    # Andalusian sources
    '@Songtive:Andalusian': 'Songtive Blog - Andalusian Cadence (2024)',
    '@SignalsMusicStudio:Andalusian': 'Signals Music Studio - Andalusian Cadence Power',
    '@GuitarEndeavor:Andalusian': 'Guitar Endeavor - Andalusian Chord Progression (2017)',
    '@GuitarLobby:MinorProgressions': 'Guitar Lobby - 17 Minor Chord Progressions (2024)',
    
    # Gospel sources
    '@Pianote:GospelProgressions': 'Pianote - Gospel Chord Progressions (Jun 2023)',
    '@PianoGroove:GospelIntros': 'PianoGroove - Common Gospel Chord Progressions (Jul 2025)',
    '@Unison:GospelProgressions': 'Unison Audio - Gospel Chord Progressions Guide (Oct 2024)',
    '@eMastered:GospelChords': 'eMastered - Gospel Chords: 7 Chords for Spiritual Music',
    '@GregHowlett:SecondaryDominants': 'Greg Howlett - Secondary Dominants in Hymns',
    '@PSRTutorial:GospelWalkup': 'PSR Tutorial - Gospel Technique #2: Walk On Up (2006)',
    
    # Bossa Nova sources
    '@LearnJazzStandards:GirlFromIpanema': 'Learn Jazz Standards - Girl From Ipanema Chords (Dec 2024)',
    '@LearnJazzStandards:BossaNovaProgressions': 'Learn Jazz Standards - 6 Bossa Nova Chord Progressions (Aug 2024)',
    '@PianoWithJonny:JobimProgression': 'Piano With Jonny - The Jobim Chord Progression (Jan 2024)',
    '@BossaNovaGuitarre:Chords2': 'Bossa Nova Gitarre - Bossa Nova Chords #2 (May 2024)',
    '@Musicogram:BossaProgressions': 'Musicogram - Bossa Nova Chord Progressions Guide',
    
    # Country sources
    '@eMastered:CountryProgressions': 'eMastered - Country Chord Progressions: A Beginner\'s Guide',
    '@GuitarChordsLibrary:Country': 'Guitar Chords Library - Essential Country Guitar Chord Progressions (Dec 2025)',
    '@PowersOf10:Country': 'Powers of 10 - Country Chord Progressions 2026 Guide (Oct 2025)',
    '@GuitarMasterclass:Country-III-IV': 'Guitar Masterclass - Country I-III-IV Progression (Sep 2023)',
    
    # Reggae sources
    '@Splice:ReggaeProgressions': 'Splice Blog - Reggae Chord Progressions: A Beginner\'s Guide (Dec 2025)',
    '@WayneAndWax:RootsRiddim': 'Wayne & Wax - Feel It In The One-Drop: A Roots Riddims Tutorial',
    '@Unison:ReggaeProgressions': 'Unison Audio - 11 Popular Reggae Chord Progressions (Sep 2024)',
    '@Riffhard:ReggaeGuitar': 'Riffhard - How to Get the Reggae Sound on a Guitar (Feb 2025)',
    
    # Ska sources
    '@eHow:SkaProgressions': 'eHow UK - Common Ska Progressions (Jul 2020)',
    '@NYCGuitarSchool:Ska': 'New York City Guitar School - An Intro To Ska Guitar (Oct 2024)',
    '@GuitarTricks:Ska': 'Guitar Tricks - Guitar Lessons: Ska Guitar 101',
    '@GuitarMasterclass:Ska': 'Guitar Masterclass - Ska Guitar Lesson (Apr 2011)',
    
    # R&B/Neo-Soul sources
    '@eMastered:NeoSoul': 'eMastered - Neo Soul Chord Progressions: A Beginner\'s Guide',
    '@PickupMusic:NeoSoul': 'Pickup Music - Neo-Soul Guitar Chords for Beginners',
    '@ChordChord:RnBProgressions': 'ChordChord - 7 Top R&B Chord Progressions for Soulful Tunes (Apr 2025)',
    '@NativeInstruments:RnB': 'Native Instruments Blog - 5 Tips for R&B Chord Progressions (Nov 2024)',
    '@MusicGateway:NeoSoul': 'Music Gateway - Neo Soul History & Famous Artists',
    
    # EDM sources
    '@LANDR:EDM': 'LANDR Blog - EDM, House & Techno Chord Progressions (Feb 2023)',
    '@NativeInstruments:EDM': 'Native Instruments Blog - 5 Essential EDM Chord Progressions (Sep 2023)',
    '@Unison:EDMProgressions': 'Unison Audio - 8 EDM Chord Progressions (Oct 2023)',
    '@TopMusicArts:EDM': 'Top Music Arts - 5 Most Used Chord Progressions in EDM',
    '@Melodics:EDM': 'Melodics - EDM Chord Progressions for Beginners',
    '@SideNoize:EDMProgressions': 'SideNoize - 7 Most Used EDM Chord Progressions',
    '@Samplesound:EDMProgressions': 'Samplesound - Popular Chord Progressions in EDM, Techno (Feb 2025)',
    
    # Metal sources
    '@PickupMusic:MetalChords': 'Pickup Music - Metal Guitar Chords: 8 Chords To Know',
    '@Riffhard:MetalProgressions': 'Riffhard - How to Read Guitar Chord Progressions (Feb 2025)',
    '@MetalMastermind:Theory': 'Metal Mastermind - Metal Music Theory For Beginners (Jan 2025)',
    '@FundamentalChanges:Phrygian': 'Fundamental Changes - The Phrygian Mode for Guitar (May 2018)',
    '@CreativeGuitarStudio:ProgMetal': 'Creative Guitar Studio - Progressive Metal Riff Building',

    # Cinematic
    '@FilipeLeitao:Inception': 'Filipe Leitao - Decoding Inception Score',
    '@ComposerFocus:HansZimmer': 'Composer Focus - Hans Zimmer Techniques',
    '@PianoWithJonny:Cinematic': 'Piano With Jonny - 3 Cinematic Chord Progressions',
    '@FilipeLeitao:Gladiator': 'Filipe Leitao - Gladiator Analysis',
    '@Landr:Interstellar': 'LANDR - Interstellar Chords',
    '@Landr:StarWars': 'LANDR - John Williams Style',
    '@eMastered:Epic': 'eMastered - Epic Chord Progressions',
    '@eMastered:LeiasTheme': 'eMastered - Film Score Progressions',
    '@Landr:Pirates': 'LANDR - Hans Zimmer Style',
}

# Rick Beato context ... (unchanged)

# GENRE/MOOD TAGS (expanded)
GENRES = [
    "Jazz", "Jazz-Blues", "Blues", "Rock", "Pop", "Metal", "Flamenco", 
    "Doo-wop", "Rock-n-Roll", "Classical", "Gospel", "Bossa-Nova",
    "Country", "Country-Blues", "Reggae", "Ska", "Neo-Soul", "R&B",
    "EDM", "House", "Techno", "Trance", "Deep-House", "Prog-Metal",
    "Djent", "Cinematic", "Lo-Fi", "Pop Rock", "Pop Ballad", "Pop Funk"
]

MOODS = [
    "Joyful", "Hopeful", "Romantic", "Nostalgic", "Peaceful",
    "Playful", "Relaxed", "Tender", "Triumphant", "Spiritual",
    "Excited", "Mysterious", "Sad", "Lonely", "Dark",
    "Rebellious", "Empowered", "Surprised", "Fearful", "Dramatic",
    "Anthemic", "Uplifting", "Melancholic", "Sophisticated", 
    "Confident", "Driving", "Energetic", "Passionate", "Dreamy",
    "Vintage", "Chromatic", "Smooth", "Soulful", "Emotional",
    "Bluesy", "Elegant", "Laid-back", "Groovy", "Mellow",
    "Bright", "Bouncy", "Hypnotic", "Jazzy", "Complex",
    "Flowing", "Meditative", "Euphoric", "Intense", "Epic",
    "Aggressive", "Heavy", "Angular", "Exotic", "Dissonant",
    "Heroic", "Wonder", "Mystery", "Bittersweet", "Chill", "Sentimental"
]

# Keep original chord type definitions
CHORD_TYPES_MAJ = {
    '': [0, 4, 7],
    'M': [0, 4, 7],
    'sus2': [0, 2, 7],
    'sus4': [0, 5, 7],
    '5': [0, 7],
    '6': [0, 4, 7, 9],
    '7': [0, 4, 7, 10],
    'dom7': [0, 4, 7, 10],
    '7-5': [0, 4, 6, 10],
    '7+5': [0, 4, 8, 10],
    '7sus4': [0, 5, 7, 10],
    'maj7': [0, 4, 7, 11],
    'M7': [0, 4, 7, 11],
    'M7+5': [0, 4, 8, 11],
    'add4': [0, 4, 5, 7],
    'add9': [0, 4, 7, 14],
    'sus4add9': [0, 5, 7, 14],
    '2': [0, 4, 7, 14],
    'add11': [0, 4, 7, 17],
    '69': [0, 4, 7, 9, 14],
    '9': [0, 4, 7, 10, 14],
    'maj9': [0, 4, 7, 11, 14],
    'M9': [0, 4, 7, 11, 14],
    '9sus4': [0, 5, 7, 10, 14],
    '7-9': [0, 4, 7, 10, 13],
    '7+11': [0, 4, 7, 10, 18],
    '7#11': [0, 4, 7, 10, 18],  # Alternative notation
    '13': [0, 4, 7, 10, 14, 21],
}

CHORD_TYPES_MIN = {
    'm': [0, 3, 7],
    'min': [0, 3, 7],
    'msus2': [0, 2, 7],
    'msus4': [0, 5, 7],
    'm6': [0, 3, 7, 9],
    'm7': [0, 3, 7, 10],
    'm7-5': [0, 3, 6, 10],
    'm7b5': [0, 3, 6, 10],  # Alternative notation
    'm7+5': [0, 3, 8, 10],
    '7sus4': [0, 5, 7, 10],
    'dim': [0, 3, 6],
    'dim6': [0, 3, 6, 9],
    'dim7': [0, 3, 6, 9],
    'mM7': [0, 3, 7, 11],
    'madd4': [0, 3, 5, 7],
    'madd9': [0, 3, 7, 14],
    'm9': [0, 3, 7, 10, 14],
    'sus4add9': [0, 5, 7, 14],
    'm69': [0, 3, 7, 9, 14],
    '9sus4': [0, 5, 7, 10, 14],
    'm7b9b5': [0, 3, 6, 10, 13],
    'm7add11': [0, 3, 7, 10, 17],
    'mM7add11': [0, 3, 7, 11, 17],
}

CHORD_TYPES = {**CHORD_TYPES_MAJ, **CHORD_TYPES_MIN}

# HELPER FUNCTIONS
def parse_progression(prog_str: str) -> tuple:
    """Parse progression with optional source citation."""
    parts = prog_str.split('=')
    chords = parts[0].strip().split()
    
    if len(parts) > 1:
        metadata = parts[1].strip().split('@')
        moods = metadata[0].strip().split()
        source = '@' + metadata[1] if len(metadata) > 1 else None
    else:
        moods = []
        source = None
    
    return chords, moods, source

def get_progressions_by_genre(genre: str) -> list:
    """Get all progressions tagged with a specific genre."""
    genre_lower = genre.lower()
    results = []
    
    for category, progressions in prog_all_extended.items():
        for prog_str in progressions:
            chords, moods, source = parse_progression(prog_str)
            if any(genre_lower in m.lower() for m in moods):
                results.append({
                    'chords': chords,
                    'moods': moods,
                    'source': source,
                    'category': category
                })
    
    return results

def get_progressions_by_mood(mood: str) -> list:
    """Get all progressions tagged with a specific mood."""
    mood_lower = mood.lower()
    results = []
    
    for category, progressions in prog_all_extended.items():
        for prog_str in progressions:
            chords, moods, source = parse_progression(prog_str)
            if any(mood_lower in m.lower() for m in moods):
                results.append({
                    'chords': chords,
                    'moods': moods,
                    'source': source,
                    'category': category
                })
    
    return results

def get_source_citation(source_key: str) -> str:
    """Get full citation for a source."""
    return SOURCES.get(source_key, "Unknown source")

def get_all_progressions_by_category(category: str = None) -> list:
    """Get all progressions, optionally filtered by category."""
    if category:
        progs = prog_all_extended.get(category, [])
        return [parse_progression(p) for p in progs]
    
    results = []
    for cat, progs in prog_all_extended.items():
        for prog_str in progs:
            chords, moods, source = parse_progression(prog_str)
            results.append({
                'chords': chords,
                'moods': moods,
                'source': source,
                'category': cat
            })
    return results

if __name__ == "__main__":
    # Example usage
    print("=== Extended Chord Progression Database ===\n")
    
    print(f"Total progressions by category:")
    for category, progs in prog_all_extended.items():
        print(f"  {category}: {len(progs)}")
    
    total = sum(len(p) for p in prog_all_extended.values())
    print(f"\nTotal: {total} progressions")
    print(f"Total sources cited: {len(SOURCES)}")
    print(f"Total genres: {len(GENRES)}")
    print(f"Total moods: {len(MOODS)}")
    
    print("\n=== Example: Country Progressions ===")
    country_progs = get_progressions_by_genre("Country")
    for prog in country_progs[:5]:
        print(f"{' '.join(prog['chords'])}")
        print(f"  Moods: {', '.join(prog['moods'])}")
        if prog['source']:
            print(f"  Source: {get_source_citation(prog['source'])}")
        print()
    
    print("\n=== Example: EDM Progressions ===")
    edm_progs = get_progressions_by_genre("EDM")
    for prog in edm_progs[:3]:
        print(f"{' '.join(prog['chords'])}")
        print(f"  Moods: {', '.join(prog['moods'])}")
        if prog['source']:
            print(f"  Source: {get_source_citation(prog['source'])}")
        print()
    
    print("\n=== Example: Searching by Mood (Dark) ===")
    dark_progs = get_progressions_by_mood("Dark")
    print(f"Found {len(dark_progs)} progressions tagged 'Dark'")
    for prog in dark_progs[:3]:
        print(f"{' '.join(prog['chords'])} ({prog['category']})")
        print(f"  Moods: {', '.join(prog['moods'])}")
        print()