# ID mappings extracted from the SpaceHaven game library (library/haven + library/texts)
#
# Each ``*_DATA`` dict maps a game object ID to ``(english_name, text_id)`` where
# ``text_id`` is the corresponding entry in ``library/texts`` for localization via
# ``src.texts_loader.game_texts``.  A ``text_id`` of 0 means no entry exists and
# the English name is always used.  Use ``game_texts.localize_id(DATA, id)`` to
# resolve the localized name.

# Default crew schedule/section bitmasks used by game-generated human crew.
# Required for normal AI routines (work, sleep, etc.).
DEFAULT_SCHEDULE_P0: str = "1188386"
DEFAULT_SCHEDULE_P1: str = "0"
DEFAULT_SCHEDULE_P2: str = "285212672"
DEFAULT_SEC_S0: str = "0"
DEFAULT_SEC_S1: str = "286331153"
DEFAULT_SEC_S2: str = "4369"


# Character attribute IDs (attrId on <attr> elements inside <pers>).
# Value: (english_name, texts_file_entry_id)  — 0 means no texts entry
ATTRIBUTE_DATA: dict[int, tuple[str, int]] = {
    210: ('Bravery', 210),
    212: ('Zest', 212),
    213: ('Intelligence', 213),
    214: ('Perception', 214),
}

# Skill IDs (skillId on <skill> elements inside <pers>).
# Value: (english_name, texts_file_entry_id)  — 0 means no texts entry
SKILL_DATA: dict[int, tuple[str, int]] = {
    2: ('Mining', 1414),
    3: ('Botany', 1415),
    4: ('Construction', 1416),
    5: ('Industry', 1417),
    6: ('Medical', 1420),
    7: ('Gunner', 1422),
    8: ('Shielding', 1424),
    9: ('Operations', 1425),
    10: ('Weapons', 1427),
    12: ('Carry', 1428),
    13: ('Unknown (unused)', 0),
    14: ('Navigation', 1423),
    16: ('Research', 3851),
    22: ('Piloting', 1413),
}

# Custom editor-only skill presets
# Maps: preset name -> {skill_id: (starting_level, max_level)}
CUSTOM_SKILL_PRESETS: dict[str, dict[int, tuple[int, int]]] = {
    "Jack of All Trades": {
        2: (2, 7),  # Mining
        3: (2, 7),  # Botany
        4: (2, 7),  # Construction
        5: (2, 7),  # Industry
        6: (2, 7),  # Medical
        7: (1, 6),  # Gunner
        8: (1, 6),  # Shielding
        9: (2, 7),  # Operations
        10: (1, 6),  # Weapons
        12: (2, 7),  # Carry
        13: (0, 1),  # Unknown (unused)
        14: (2, 7),  # Navigation
        16: (1, 6),  # Research
        22: (1, 6),  # Piloting
    },
    "Builder": {
        2: (1, 5),  # Mining
        3: (1, 4),  # Botany
        4: (4, 9),  # Construction
        5: (3, 8),  # Industry
        6: (1, 4),  # Medical
        7: (0, 2),  # Gunner
        8: (0, 2),  # Shielding
        9: (2, 7),  # Operations
        10: (0, 2),  # Weapons
        12: (2, 6),  # Carry
        13: (0, 1),  # Unknown (unused)
        14: (1, 6),  # Navigation
        16: (1, 4),  # Research
        22: (0, 2),  # Piloting
    },
    "Medic Scientist": {
        2: (1, 4),  # Mining
        6: (4, 9),  # Medical
        7: (0, 2),  # Gunner
        8: (0, 2),  # Shielding
        9: (2, 7),  # Operations
        10: (0, 2),  # Weapons
        12: (2, 6),  # Carry
        13: (0, 1),  # Unknown (unused)
        14: (1, 5),  # Navigation
        16: (4, 9),  # Research
        22: (0, 2),  # Piloting
        3: (2, 7),  # Botany
        4: (1, 5),  # Construction
        5: (1, 5),  # Industry
    },
    "Security Pilot": {
        2: (0, 2),  # Mining
        3: (0, 2),  # Botany
        4: (1, 4),  # Construction
        5: (1, 4),  # Industry
        6: (1, 4),  # Medical
        7: (3, 8),  # Gunner
        8: (3, 8),  # Shielding
        9: (2, 6),  # Operations
        10: (4, 9),  # Weapons
        14: (3, 9),  # Navigation
        12: (2, 6),  # Carry
        13: (0, 1),  # Unknown (unused)
        16: (0, 3),  # Research
        22: (4, 10),  # Piloting
    },
    "Industrial Miner": {
        2: (4, 10),  # Mining
        3: (1, 4),  # Botany
        4: (2, 6),  # Construction
        5: (4, 9),  # Industry
        6: (1, 4),  # Medical
        7: (0, 2),  # Gunner
        8: (0, 2),  # Shielding
        9: (2, 6),  # Operations
        10: (0, 2),  # Weapons
        12: (3, 8),  # Carry
        13: (0, 1),  # Unknown (unused)
        14: (1, 5),  # Navigation
        16: (1, 4),  # Research
        22: (0, 2),  # Piloting
    },
    "Agricultural Specialist": {
        2: (1, 4),  # Mining
        3: (4, 10),  # Botany
        4: (2, 6),  # Construction
        5: (2, 6),  # Industry
        6: (2, 6),  # Medical
        7: (0, 2),  # Gunner
        8: (0, 2),  # Shielding
        9: (2, 6),  # Operations
        10: (0, 2),  # Weapons
        12: (2, 6),  # Carry
        13: (0, 1),  # Unknown (unused)
        14: (1, 5),  # Navigation
        16: (3, 8),  # Research
        22: (0, 2),  # Piloting
    },
}

# Backstory IDs (bsid on <pers> elements) — the character's pre-game profession/
# background. Cosmetic; affects starting skill minimums and mood factor weights.
# Value: (english_name, texts_file_entry_id)  — 0 means no texts entry
BACKSTORY_DATA: dict[int, tuple[str, int]] = {
    1763: ('Police officer', 660),
    1764: ('Nurse', 661),
    1765: ('Doctor', 662),
    1766: ('Salesperson', 663),
    1767: ('Cook', 664),
    1768: ('Material mover', 665),
    1769: ('Engineer', 666),
    1770: ('Security guard', 667),
    1771: ('Construction laborer', 668),
    1772: ('Sheriff', 669),
    1773: ('Lawyer', 670),
    1774: ('Medical assistant', 671),
    1775: ('Bartender', 672),
    1776: ('Teacher', 673),
    1777: ('Computer programmer', 674),
    1778: ('Welder', 675),
    1779: ('Firefighter', 676),
    1780: ('Telemarketer', 677),
    1781: ('Lab technician', 678),
    1782: ('Chemical engineer', 679),
    1783: ('Airline pilot', 680),
    1784: ('Fighter pilot', 681),
    1785: ('Driller', 682),
    1786: ('Mining technician', 683),
    1787: ('Geologist', 684),
    1788: ('Farmer', 685),
    1789: ('Scientist', 2240),
    1790: ('Blacksmith', 686),
    1791: ('Navigator', 687),
    1792: ('Florist', 0),
    3101: ('Game Developer', 4620),
    3102: ('Astronaut', 4622),
    3103: ('Psychologist', 4624),
    3104: ('Comedian', 4626),
    3105: ('Brewmaster', 4628),
    3106: ('Electrician', 4630),
    3107: ('Prizefighter', 4632),
    3108: ('Athlete', 4634),
}

# Personality trait IDs (traitId on <trait> elements inside <pers>).
# Value: (english_name, texts_file_entry_id)  — 0 means no texts entry
TRAIT_DATA: dict[int, tuple[str, int]] = {
    191: ('Hero', 216),
    655: ('Wimp', 413),
    656: ('Clumsy', 414),
    1034: ('Moody', 567),
    1035: ('Smart', 572),
    1036: ('Bloodlust', 574),
    1037: ('Antisocial', 576),
    1038: ('Needy', 578),
    1039: ('Fast learner', 580),
    1040: ('Lazy', 582),
    1041: ('Hard working', 584),
    1042: ('Psychopath', 586),
    1043: ('Peace-loving', 588),
    1044: ('Iron-willed', 590),
    1045: ('Spacefarer', 592),
    1046: ('Confident', 594),
    1047: ('Neurotic', 596),
    1048: ('Charming', 598),
    1533: ('Iron stomach', 939),
    1534: ('Nyctophilia', 941),
    1535: ('Minimalist', 943),
    1560: ('Talkative', 995),
    1562: ('Gourmand', 999),
    2082: ('Alien lover', 2047),
}

# Active condition/status effect IDs (conditionId on <condition> elements inside <pers>).
# Value: (english_name, texts_file_entry_id)  — 0 means no texts entry
CONDITION_DATA: dict[int, tuple[str, int]] = {
    193: ('Panicked', 217),
    194: ('Scared', 218),
    713: ('Frostbite', 405),
    714: ('First-degree burn', 406),
    715: ('Wound', 408),
    751: ('Blast injury', 435),
    1003: ('Crawler bite', 500),
    1033: ('Ate without table', 565),
    1053: ('Feeling a little hungry', 600),
    1058: ('Feeling somewhat unsafe.', 643),
    1059: ('Slept on the floor.', 649),
    1060: ('Holding it in.', 651),
    1061: ("It's so dark on this spaceship.", 653),
    1062: ('Ate the meat of a human being.', 655),
    1063: ('Wearing spacesuit', 657),
    1064: ('Feeling adventurous.', 689),
    1065: ('Feeling meaningful.', 691),
    1066: ('Feeling loved.', 693),
    1096: ('Shat pants', 779),
    1108: ('Unconscious', 781),
    1109: ('Starvation', 412),
    1112: ('Low oxygen', 409),
    1118: ('CO2 condition', 486),
    1119: ('Hazardous gas', 485),
    1120: ('Smoke condition', 487),
    1121: ('Low body temperature', 410),
    1122: ('High body temperature', 411),
    1123: ('Ate too much', 788),
    1124: ('Ate monster meat', 790),
    1125: ('Ate spoiled food', 792),
    1127: ('Lonely', 807),
    1430: ('Cocooned', 830),
    1550: ('Did something I love', 961),
    1561: ('Black eye', 997),
    1563: ('Did something I dislike', 1001),
    1581: ('Minor discomfort', 1013),
    1582: ('Moderate discomfort', 1014),
    1583: ('Major discomfort', 1015),
    1584: ('Feeling a little unsafe', 1019),
    1585: ('Fearful', 1020),
    1586: ('Terrified', 1021),
    1587: ('Feeling left out', 1025),
    1588: ('Feeling isolated and lonely', 1026),
    1589: ('Feeling completely alone and unloved', 1027),
    1590: ('Low energy', 1031),
    1591: ('Feeling fatigued', 1033),
    1592: ('Extremely fatigued', 1035),
    1593: ('Feeling slightly hungry', 1037),
    1594: ('Feeling hungry', 1039),
    1595: ('Feeling very hungry', 1041),
    1596: ('Some health problems', 1043),
    1597: ('Concerning health problems', 1045),
    1598: ('Serious health problems', 1047),
    1600: ('Having a mental breakdown', 1049),
    1622: ('Heard a funny joke', 1097),
    1623: ('Someone was mean to me', 1099),
    1624: ('Got comforted', 1101),
    1625: ('Got rejected', 1103),
    1626: ('Someone thanked me', 1105),
    1648: ('Cryo sleep', 1238),
    1649: ('Wall cocoon', 1236),
    1739: ('Spacesuit fatigue', 1385),
    1957: ('Wound', 408),
    2055: ('Resting', 1890),
    2056: ('Resting in medical bed', 1892),
    2057: ('Open wound', 1893),
    2080: ('Aliens haunt me in my dreams', 2043),
    2081: ('I was held as a prisoner', 2045),
    2083: ('Stockholm syndrome', 2049),
    2246: ('Working comfortably', 2281),
    2247: ('Resting comfortably', 2283),
    2248: ('Working uncomfortably', 2285),
    2417: ('Prisoner recruitment', 3529),
    2482: ('Concussion', 3696),
    2490: ('Disorientation', 3707),
    2491: ('Lost appetite', 3709),
    2492: ('Insomnia', 3711),
    2493: ('Unable to work', 3713),
    2494: ('Psychosis', 3715),
    2495: ('Aggressive behavior', 3717),
    2496: ('Schizophrenia', 3719),
    2497: ('Urge to destroy', 3721),
    2498: ('Full mental breakdown', 9428),
    2499: ('Attempted suicide', 3728),
    2500: ('Poisoned', 3730),
    2512: ('Saw a captive crew member', 3822),
    2664: ('Nausea', 3909),
    2667: ('Protein deficiency', 3913),
    2668: ('Fatty acids deficiency', 3915),
    2669: ('Craving for carbohydrates', 3917),
    2670: ('Vitamin deficiency anemia', 3919),
    2728: ('Wound', 408),
    2729: ('Hauler slash', 4651),
    2798: ('Received an electric shock', 4155),
    2843: ('I was held as a slave', 4239),
    3090: ('Burned hands', 4604),
    3091: ('I messed up', 4606),
    3092: ('Injured', 4608),
    3093: ('Vision loss', 4610),
    3094: ('Inhaled toxic fumes', 4612),
    3095: ('Exposed to loud noise', 4614),
    3118: ('Spore infection', 4660),
    3120: ('Spore eruption', 4662),
    3121: ('Feeling ill', 4664),
    3133: ('Chronic wound', 4693),
    3136: ('Broken arm', 4698),
    3137: ('Knocked unconscious', 4700),
    3160: ('Unconscious', 781),
    3164: ('Interstellar travel sickness', 4758),
    3194: ('Refusing to work (Uncomfortable environment)', 4828),
    3195: ('I rebelled (Uncomfortable environment)', 4830),
    3307: ('Minor comfort', 4993),
    3308: ('Moderate comfort', 4994),
    3309: ('Major comfort', 4995),
    3310: ('Uncomfortable sleep', 4997),
    3311: ('Sleeping comfortably', 4999),
    3312: ('Uncomfortable leisure space', 5001),
    3313: ('Good leisure space', 5003),
    3314: ('Ate a great meal', 5014),
    3315: ('Feeling sad', 5016),
    3321: ('Feeling Aggressive (Minor mental break)', 5018),
    3322: ('Destructive behavior (Major mental break)', 5051),
    3323: ('Pyromania (Major mental break)', 5053),
    3324: ('Interrupted sleep (No privacy)', 5058),
    3325: ('Sleeping with privacy', 5060),
    3327: ('No entertainment', 5062),
    3328: ('Feeling claustrophobic (No hull windows)', 5064),
    3329: ('Feeling energetic', 5066),
    3330: ('Extremely frustrated', 5076),
    3332: ('Had a good chat with a friend', 5078),
    3333: ('Shared my feelings with a good friend', 5080),
    3334: ('Connected with my best friend', 5082),
    3335: ('Sleep deprived', 5084),
    3337: ('In a good mood', 5086),
    3338: ('In a great mood', 5088),
    3339: ('In a fantastic mood', 5090),
    3340: ('No one to talk to', 5092),
    3341: ('Missing my friend', 5095),
    3342: ('Missing my lover', 5097),
    3343: ('My friend died', 5099),
    3344: ('My best friend died', 5101),
    3345: ('My lover died', 5103),
    3346: ('I think my friend might be dead', 5105),
    3347: ('I think my lover might be dead', 5107),
    3348: ('My enemy is not bothering me', 5109),
    3349: ('I think my enemy might be dead', 5111),
    3350: ('My enemy is dead', 5113),
    3351: ('Panicking', 5115),
    3352: ('Refusing to work (Minor mental break)', 5117),
    3353: ('Unconscious (Major mental break)', 5119),
    3354: ('Saboteur (Extreme mental break)', 5121),
    3361: ('No decorations', 5128),
    3368: ('Drinking binge (Minor mental break)', 5139),
    3369: ('Gaming binge (Minor mental break)', 5141),
    3370: ('Intoxicated (Alcohol)', 5143),
    3371: ('Hungover (Alcohol)', 5145),
    3380: ('Lost my leader', 5171),
    3385: ('Sleeping together with my lover', 5258),
    3440: ('Post-surgery fatigue', 5353),
    3442: ('Post-surgery rest', 5356),
    3445: ('Wound', 408),
    3446: ('Wound', 408),
    3447: ('Burn wound', 5392),
    3448: ('Wound', 408),
    3465: ('Healing boosted', 5435),
    3467: ('Groggy', 5437),
    3481: ('Had an unpleasant conversation', 5469),
    3660: ('Wound', 408),
    3699: ('Wound', 408),
    3700: ('Wound', 408),
    3927: ('Under the influence of ISP', 7566),
    3928: ('ISP side effect: Insomnia', 7579),
    3929: ('ISP side effect: Tremor', 7582),
    3930: ('ISP side effect: Lost appetite', 7584),
    3951: ('Feeling weird sensations', 7626),
    3952: ('Resting in an advanced medical bed', 7628),
    3971: ('Stunned', 7655),
    4008: ('In pain', 7674),
    4010: ('I took painkillers', 7676),
    4011: ('I used a Combat Stimulant', 7678),
    4013: ('Drug side effect: Insomnia', 7684),
    4014: ('Drug side effect: Tremor', 7682),
    4015: ('Drug side effect: Lost appetite', 7680),
    4016: ('Drug side effect: Brain fog', 7686),
    4017: ('Drug side effect: Melancholy', 7688),
    4018: ('Drug side effect: Fatigue', 7690),
    4019: ('Drug side effect: Anxiety', 7692),
    4021: ('I took some mood stimulants', 7696),
    4023: ('CSP stage: euphoria', 7700),
    4026: ('I ingested some alien enzyme', 7704),
    4034: ('Sedated', 7724),
    4042: ('CSP stage: Excitement', 7731),
    4043: ('CSP stage: Crash', 7732),
    4074: ('I studied', 7772),
    4075: ('Burn wound from a flamethrower', 7859),
    4079: ('An alien parasite is attached to my face', 7848),
    4080: ('Bruised throat', 7850),
    4082: ('Feeling a little unsafe', 1019),
    4302: ('Siren World Awareness', 8045),
    4303: ('Siren World Aftermath', 8047),
    4633: ('I received medical treatment', 9387),
    4644: ('Scar', 9426),
}

# Storage item IDs (elementaryId / mid on <s> elements inside <inv>).
# Elementary resources use eid in the save file; physical items use mid.
# Value: (english_name, texts_file_entry_id)  — 0 means no texts entry
STORAGE_DATA: dict[int, tuple[str, int]] = {
    15: ('Root vegetables', 61),
    16: ('Water', 64),
    34: ('Power', 3455),
    40: ('Ice', 72),
    63: ('Oxygen', 3472),
    64: ('CO2', 3457),
    71: ('Bio Matter', 77),
    73: ('Heat', 3469),
    77: ('Smoke', 3453),
    127: ('Rubble', 100),
    157: ('Base Metals', 184),
    158: ('Energium', 109),
    162: ('Infrablock', 108),
    169: ('Noble Metals', 190),
    170: ('Carbon', 191),
    171: ('Raw Chemicals', 197),
    172: ('Hyperium', 198),
    173: ('Electronics Component', 199),
    174: ('Energy rod', 200),
    175: ('Plastics', 201),
    176: ('Chemicals', 202),
    177: ('Fabrics', 203),
    178: ('Hyperfuel', 204),
    179: ('Processed Food', 196),
    706: ('Fruits', 422),
    707: ('Artificial meat', 423),
    712: ('Space food', 429),
    930: ('Techblock', 477),
    971: ('Hazardous Gas', 484),
    984: ('Monster meat', 488),
    985: ('Human meat', 490),
    1397: ('Food group', 817),
    1445: ('Building tools', 836),
    1759: ('Hull Block', 1393),
    1858: ('Credits', 1564),
    1873: ('Infra Scrap', 1698),
    1874: ('Soft Scrap', 1696),
    1886: ('Hull Scrap', 1724),
    1919: ('Energy block', 1771),
    1920: ('Superblock', 1773),
    1921: ('Soft block', 1775),
    1922: ('Steel Plates', 1778),
    1924: ('Optronics Component', 1780),
    1925: ('Quantronics Component', 1782),
    1926: ('Energy Cell', 1784),
    1932: ('Fibers', 1786),
    1946: ('Tech Scrap', 1800),
    1947: ('Energy Scrap', 1802),
    2053: ('Medical Supplies', 1888),
    2058: ('IV Fluid', 1897),
    2452: ('Water Vapor', 3630),
    2475: ('Fertilizer', 3635),
    2657: ('Nuts and seeds', 3899),
    2715: ('Explosive ammunition', 268),
    3196: ('Advanced Power', 4836),
    3366: ('Mild Alcohol', 5136),
    3378: ('Grains and Hops', 5160),
    3419: ('Augmentation Parts', 5320),
    3512: ('Exotic ore', 5531),
    3513: ('Basic ore', 5533),
    4027: ('Alien Organs', 7706),
    4028: ('Human Organs', 7708),
    725: ('Rifle', 7857),
    728: ('SMG', 502),
    729: ('Shotgun', 504),
    760: ('Pistol', 7855),
    1152: ('Sentry gun X1', 5262),
    1954: ('Human Corpse', 1807),
    3069: ('Laser Rifle', 5374),
    3070: ('Laser Pistol', 5372),
    3071: ('Plasma Clustergun', 5378),
    3072: ('Plasma Rifle', 5376),
    3077: ('Hauler Corpse', 4588),
    3079: ('Human Corpse (player)', 4599),
    3384: ('Armored Vest', 5252),
    3386: ('Remote Control', 5260),
    3388: ('Oxygen Tank', 5442),
    3711: ('Evolving Alien Core Remains', 5965),
    3712: ('Alien Hive Core Remains', 5964),
    3960: ('Flamethrower', 5295),
    3961: ('Stun Rifle', 7640),
    3962: ('Stun Pistol', 7638),
    3967: ('Explosive Grenade Launcher', 7644),
    3968: ('Basic scope', 7647),
    3969: ('Tactical Grip', 7649),
    4005: ('Painkillers', 7668),
    4006: ('Combat Stimulant', 7670),
    4007: ('Bandage', 7672),
    4030: ('Nano Wound Dressing', 7716),
    4040: ('Small Breaching Charge', 7728),
    4065: ('Space Suit Oxygen Extender', 7735),
    4076: ('Incendiary Grenade Launcher', 7861),
    4078: ('Alien Parasite Corpse', 7846),
    4106: ('Infester Corpse', 7902),
}

# Entity type IDs (objId on <e> elements) for characters and creatures.
CHARACTER_TYPE_IDS: dict[int, str] = {
    89: "Human/Android",
    989: "Crawler",
    994: "Alien Hive Core Egg",
    1426: "Alien Hive Core",
    1427: "Hauler",
    1429: "Hauler Egg",
    2874: "Logistics Bot",
    2888: "Salvage Bot",
    3657: "Hamster (Flybot)",
    3682: "Chimp (Walkerbot)",
    4108: "Alien Parasite",
    4298: "Hallucination",
}

# Craft/vehicle type IDs (objId on <c> elements inside <crafts>).
CRAFT_IDS: dict[int, str] = {
    20: "Shuttle",
    39: "Miner",
    2786: "Fighter",
    3491: "Builder",
    3531: "Cargo Shuttle",
    3641: "Rogue bot Sentry Drone",
    3642: "Rogue bot Attack Drone",
    3644: "Rogue bot Scout",
    3668: "Pony (Dropship)",
    3683: "Infester",
    3750: "Asteroid",
    3751: "Asteroid",
    3752: "Asteroid",
    3753: "Asteroid",
    3754: "Asteroid",
    3755: "Asteroid",
    4195: "Miner",
    4196: "Cargo Shuttle",
    4503: "Shuttle",
    4534: "Cargo Shuttle",
}

# Research technology IDs extracted from library/haven + library/texts (EN).
# Value: (english_name, texts_file_entry_id)  — 0 means no texts entry
TECH_DATA: dict[int, tuple[str, int]] = {
    2532: ('Scanner', 2276),
    2533: ('Shield Generator', 2182),
    2534: ('Energy Turret', 2307),
    2538: ('Large Storage', 186),
    2539: ('Autopsy Table', 1177),
    2559: ('Medical Bed', 157),
    2560: ('Grow Bed with Light', 3574),
    2561: ('CO2 Producer', 1609),
    2563: ('Arcade Machine', 1078),
    2564: ('Basic Entertainment', 7870),
    2565: ('Solar Panel', 2184),
    2566: ('X2 Power Generator', 3864),
    2567: ('X3 Power Generator', 3865),
    2568: ('Power Capacity Node', 1749),
    2569: ('Item Fabricator', 154),
    2570: ('Micro-Weaver', 1819),
    2571: ('Assembler', 1787),
    2572: ('Energy Refinery', 482),
    2573: ('Chemical Refinery', 474),
    2574: ('Water Collector', 3626),
    2575: ('Advanced Assembler', 1832),
    2576: ('Composter', 3632),
    2577: ('Hypersleep Chamber', 1241),
    2581: ('Basic', 3869),
    2583: ('Hyperium Hyperdrive', 3867),
    2584: ('Chemical', 3877),
    2585: ('Advanced', 3870),
    2586: ('Optronic', 3871),
    2587: ('Quantum', 3872),
    2589: ('Weapons Console', 2252),
    2590: ('Shields Console', 2254),
    2591: ('Rocket Turret', 442),
    2592: ('Energy Turret (mk2)', 2307),
    2594: ('X1 Power Generator', 137),
    2595: ('X1 Hyperdrive', 267),
    2601: ('Targeting Jammer', 4012),
    2605: ('Laser Weapons', 5380),
    2606: ('Plasma Weapons', 5381),
    2607: ('Surgical Enhancement Facility', 5314),
    2609: ('Implanted Rebreather', 5298),
    2610: ('Ocular Implant', 5300),
    2611: ('Synthetic Stomach Lining', 5302),
    2612: ('Metal Refinery', 478),
    2618: ('Fabrics', 3881),
    2619: ('Fibers', 1786),
    2622: ('Bulletproof Vest', 5251),
    2623: ('Botany', 3879),
    2626: ('Advanced Nutrition', 3883),
    2627: ('Space Food', 429),
    2628: ('Artificial Meat', 423),
    2629: ('Alcohol Beverage Machine', 5134),
    2630: ('Grains and Hops', 5160),
    2694: ('Optronics Fabricator', 1828),
    2696: ('X1 Couch', 895),
    2847: ('Enslavement Facility', 4169),
    3024: ('Logistics Robot Station', 4343),
    3025: ('Salvage Robot Station', 4374),
    3112: ('Recycler', 160),
    3114: ('Research Lab', 3852),
    3115: ('Research Workbench', 4572),
    3116: ('Research Experiment Table', 4654),
    3119: ('Navigation Console', 2250),
    3122: ('Operations Console', 2258),
    3124: ('Crawler', 4592),
    3125: ('Hauler', 4593),
    3127: ('Robotics 01', 4676),
    3128: ('Industry 01', 4678),
    3129: ('Industry 02', 4680),
    3130: ('Botany 02', 4682),
    3417: ('Armored Vest', 5252),
    3420: ('Anatomical Augmentation', 5322),
    3421: ('Neural Augmentation', 5323),
    3422: ('Nanotech Augmentation', 5324),
    3423: ('Prefrontal Microcontroller', 5318),
    3464: ('Sentry Gun X1', 5262),
    3704: ('Alien Hive Core', 5955),
    3705: ('Evolving Alien Core', 5957),
    3706: ('Advanced Nutrition 02', 6030),
    3707: ('Hamster (Flybot)', 5916),
    3708: ('Chimp (Walkerbot)', 5959),
    3709: ('X2 Hypersleep Tank', 5972),
    3710: ('Rogue Bot Architecture', 5974),
    3970: ('Advanced Medical Bed', 7629),
    3973: ('Stun Weapons', 7657),
    3974: ('Weapon Attachments 1', 7658),
    4024: ('Alien Enzyme', 7702),
    4032: ('Nano Wound Dressing', 7716),
    4092: ('Stimulants', 7882),
    4093: ('Advanced Disassembly', 7884),
    4132: ('Learning Computer', 7762),
    4134: ('Advanced Learning System', 7867),
    4529: ('Combat Robot Station', 8992),
}

# Sorted name->id lookup for UI combo boxes
STORAGE_BY_NAME: dict[str, int] = {
    v[0]: k for k, v in sorted(STORAGE_DATA.items(), key=lambda x: x[1][0])
}
TRAIT_BY_NAME: dict[str, int] = {
    v[0]: k for k, v in sorted(TRAIT_DATA.items(), key=lambda x: x[1][0])
}

# Storage module capacities extracted from library/haven <stores capacity="..."> elements.
# Key: module type ID (attribute "m" on parent <e> element in save file).
# Value: max total item quantity for that container type (0 = unlimited / not defined).
STORAGE_MODULE_CAPACITIES: dict[int, int] = {
    23: 50,
    82: 50,
    469: 5,
    789: 250,
    912: 0,
    2271: 5,
    2707: 5,
    2782: 5,
    3063: 20,
    3065: 20,
    3636: 5,
    3923: 8,
    3978: 1,
    3982: 1,
    4304: 5,
    4365: 50,
    4367: 250,
    4630: 5,
}

# Human-readable names for storage module types, derived from library/haven.
# Tuple: (english_name, texts_file_entry_id).  text_id=0 means no game-text entry.
STORAGE_MODULE_DATA: dict[int, tuple[str, int]] = {
    23: ("Small Storage", 1344),    # storageTile1
    82: ("Small Storage", 1344),    # name_tid=1344
    469: ("Shield Generator", 2182),  # shieldGenBase4 ammo reserve
    789: ("Large Storage", 186),    # storage2f
    912: ("Starter Storage", 0),    # storage1F, unlimited (no game-text entry)
    2271: ("Energy Turret", 2307),  # turret1Base2 ammo reserve
    2707: ("Energy Turret", 2307),  # turret1Base2 variant
    2782: ("Rocket Turret", 442),   # turret4Base2 ammo reserve
    3063: ("Body Storage", 4595),   # corpsesOnly: monster+human
    3065: ("Robot Storage", 4597),  # corpsesOnly: android+robot
    3636: ("Point Defense Turret", 5911),  # turretPoint1base2 ammo reserve
    3923: ("Medical Cabinet", 7726),       # name_tid=7726
    3978: ("Hidden Vent", 0),              # hiddenVentOpen, cap=1 (no game-text entry)
    3982: ("Hidden Stash", 0),             # hiddenObject1Open, cap=1 (no game-text entry)
    4304: ("Point Defense Turret", 5911),  # tactical projectile reserve
    4365: ("Small Storage", 1344),         # name_tid=1344, solar variant
    4367: ("Large Storage", 186),          # solar variant
    4630: ("Point Defense Turret", 5911),  # tactical projectile reserve (variant)
}

# Composite room module types that embed a storage bay in their linked list.
# Key: composite module type ID ("m" on parent <e>).
# Value: {linked-list index -> storage module type ID}.
# The linked-list index matches the "ind" attribute on <l> elements in the save file.
COMPOSITE_STORAGE_MODULES: dict[int, dict[int, int]] = {
    470: {1: 469},  # Shield Generator room
    632: {3: 789},  # Large Storage room
    1073: {3: 789},  # Large Storage room (variant)
    2242: {4: 2271},  # Energy Turret room
    2708: {4: 2707},  # Energy Turret room (variant)
    2783: {0: 2782},  # Rocket Turret room
    3062: {3: 3063},  # Body Storage room
    3068: {1: 3065},  # Robot Storage room
    3638: {0: 3636},  # Point Defense room
    4306: {0: 4304},  # Point Defense room (variant)
    4366: {3: 4367},  # Large Storage room (DLC)
    4629: {0: 4630},  # Point Defense room (DLC variant)
}

# Ship tile module IDs (attribute "m" on <e> tile elements inside a <ship>).
# Hull blocks form the outer shell; walls divide interior space.
HULL_TILE_IDS: frozenset[str] = frozenset(
    {
        "38",
        "46",
        "47",
        "206",
        "1144",
        "1149",
        "1711",
        "1713",
        "1794",
        "2758",
        "2759",
        "2760",
        "2762",
        "2763",
        "3029",
        "3031",
    }
)

WALL_TILE_IDS: frozenset[str] = frozenset(
    {
        "31",
        "43",
        "44",
        "48",
        "115",
        "122",
        "423",
        "425",
        "426",
        "428",
        "438",
        "2757",
        "2764",
        "2765",
        "2767",
        "2768",
        "2769",
        "2770",
        "2771",
        "2772",
        "2861",
        "2862",
        "2863",
        "2864",
        "2866",
    }
)

DOOR_TILE_IDS: frozenset[str] = frozenset({"25", "424", "905", "2755"})
ENGINE_TILE_IDS: frozenset[str] = frozenset({"2655", "851"})
# All module type IDs that represent storage (direct storage module or a composite room that embeds one)
STORAGE_TILE_IDS: frozenset[str] = frozenset(
    str(k) for k in (*STORAGE_MODULE_CAPACITIES, *COMPOSITE_STORAGE_MODULES)
)

# Timeline event type IDs (type attribute on <e> elements in timeline.xml).
TIMELINE_EVENT_NAMES: dict[int, str] = {
    1: "New Crew Member",
    2: "Crew Member Died",
    3: "Derelict Explored",
    4: "Mission Completed",
    5: "Trades Completed",
    6: "New Galaxy",
    7: "Quest Completed",
    8: "Research Completed",
}

# Character vital stat XML tag names (child elements of <pers> carrying a "v" attribute).
STAT_TAGS: tuple[str, ...] = (
    "Health",
    "Food",
    "Rest",
    "Comfort",
    "Oxygen",
    "Mood",
    "Temperature",
)

