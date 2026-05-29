# ID mappings extracted from the SpaceHaven game library (library/haven + library/texts)
#
# Text IDs (``*_TEXT_IDS`` dicts below) map each game-object ID to the
# corresponding entry in ``library/texts``, which is loaded at runtime by
# ``src.texts_loader.game_texts``.  This enables the editor to display strings
# in the language selected by the user rather than always showing English.
# Game-object IDs that have no known text-file entry are omitted; the
# ``*_IDS`` dicts (with hardcoded English strings) serve as fallbacks.

# Default crew schedule/section bitmasks used by game-generated human crew.
# Required for normal AI routines (work, sleep, etc.).
DEFAULT_SCHEDULE_P0: str = "1188386"
DEFAULT_SCHEDULE_P1: str = "0"
DEFAULT_SCHEDULE_P2: str = "285212672"
DEFAULT_SEC_S0: str = "0"
DEFAULT_SEC_S1: str = "286331153"
DEFAULT_SEC_S2: str = "4369"

# Character attribute IDs (attrId on <attr> elements inside <pers>).
ATTRIBUTE_IDS: dict[int, str] = {
    210: "Bravery",
    212: "Zest",
    213: "Intelligence",
    214: "Perception",
}

# Skill IDs (skillId on <skill> elements inside <pers>).
SKILL_IDS: dict[int, str] = {
    2: "Mining",
    3: "Botany",
    4: "Construction",
    5: "Industry",
    6: "Medical",
    7: "Gunner",
    8: "Shielding",
    9: "Operations",
    10: "Weapons",
    12: "Carry",
    13: "Unknown (unused)",
    14: "Navigation",
    16: "Research",
    22: "Piloting",
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
# background. This is cosmetic and affects starting skill minimums and mood
# factor weights, but does NOT control which jobs the character performs on the
# ship (that is governed by <jobsetting> profession priorities).
BACKSTORY_IDS: dict[int, str] = {
    1763: "Police officer",
    1764: "Nurse",
    1765: "Doctor",
    1766: "Salesperson",
    1767: "Cook",
    1768: "Material mover",
    1769: "Engineer",
    1770: "Security guard",
    1771: "Construction laborer",
    1772: "Sheriff",
    1773: "Lawyer",
    1774: "Medical assistant",
    1775: "Bartender",
    1776: "Teacher",
    1777: "Computer programmer",
    1778: "Welder",
    1779: "Firefighter",
    1780: "Telemarketer",
    1781: "Lab technician",
    1782: "Chemical engineer",
    1783: "Airline pilot",
    1784: "Fighter pilot",
    1785: "Driller",
    1786: "Mining technician",
    1787: "Geologist",
    1788: "Farmer",
    1789: "Scientist",
    1790: "Blacksmith",
    1791: "Navigator",
    1792: "Florist",
    3101: "Game Developer",
    3102: "Astronaut",
    3103: "Psychologist",
    3104: "Comedian",
    3105: "Brewmaster",
    3106: "Electrician",
    3107: "Prizefighter",
    3108: "Athlete",
}

# Personality trait IDs (traitId on <trait> elements inside <pers>).
TRAIT_IDS: dict[int, str] = {
    191: "Hero",
    655: "Wimp",
    656: "Clumsy",
    1034: "Moody",
    1035: "Smart",
    1036: "Bloodlust",
    1037: "Antisocial",
    1038: "Needy",
    1039: "Fast learner",
    1040: "Lazy",
    1041: "Hard working",
    1042: "Psychopath",
    1043: "Peace-loving",
    1044: "Iron-willed",
    1045: "Spacefarer",
    1046: "Confident",
    1047: "Neurotic",
    1048: "Charming",
    1533: "Iron stomach",
    1534: "Nyctophilia",
    1535: "Minimalist",
    1560: "Talkative",
    1562: "Gourmand",
    2082: "Alien lover",
}

# Active condition/status effect IDs (conditionId on <condition> elements inside <pers>).
CONDITION_IDS: dict[int, str] = {
    193: "Panicked",
    194: "Scared",
    713: "Frostbite",
    714: "First-degree burn",
    715: "Wound",
    751: "Blast injury",
    1003: "Crawler bite",
    1033: "Ate without table",
    1053: "Feeling a little hungry",
    1058: "Feeling somewhat unsafe.",
    1059: "Slept on the floor.",
    1060: "Holding it in.",
    1061: "It's so dark on this spaceship.",
    1062: "Ate the meat of a human being.",
    1063: "Wearing spacesuit",
    1064: "Feeling adventurous.",
    1065: "Feeling meaningful.",
    1066: "Feeling loved.",
    1096: "Shat pants",
    1108: "Unconscious",
    1109: "Starvation",
    1112: "Low oxygen",
    1118: "CO2 condition",
    1119: "Hazardous gas",
    1120: "Smoke condition",
    1121: "Low body temperature",
    1122: "High body temperature",
    1123: "Ate too much",
    1124: "Ate monster meat",
    1125: "Ate spoiled food",
    1127: "Lonely",
    1430: "Cocooned",
    1550: "Did something I love",
    1561: "Black eye",
    1563: "Did something I dislike",
    1581: "Minor discomfort",
    1582: "Moderate discomfort",
    1583: "Major discomfort",
    1584: "Feeling a little unsafe",
    1585: "Fearful",
    1586: "Terrified",
    1587: "Feeling left out",
    1588: "Feeling isolated and lonely",
    1589: "Feeling completely alone and unloved",
    1590: "Low energy",
    1591: "Feeling fatigued",
    1592: "Extremely fatigued",
    1593: "Feeling slightly hungry",
    1594: "Feeling hungry",
    1595: "Feeling very hungry",
    1596: "Some health problems",
    1597: "Concerning health problems",
    1598: "Serious health problems",
    1600: "Having a mental breakdown",
    1622: "Heard a funny joke",
    1623: "Someone was mean to me",
    1624: "Got comforted",
    1625: "Got rejected",
    1626: "Someone thanked me",
    1648: "Cryo sleep",
    1649: "Wall cocoon",
    1739: "Spacesuit fatigue",
    1957: "Wound",
    2055: "Resting",
    2056: "Resting in medical bed",
    2057: "Open wound",
    2080: "Aliens haunt me in my dreams",
    2081: "I was held as a prisoner",
    2083: "Stockholm syndrome",
    2246: "Working comfortably",
    2247: "Resting comfortably",
    2248: "Working uncomfortably",
    2417: "Prisoner recruitment",
    2482: "Concussion",
    2490: "Disorientation",
    2491: "Lost appetite",
    2492: "Insomnia",
    2493: "Unable to work",
    2494: "Psychosis",
    2495: "Aggressive behavior",
    2496: "Schizophrenia",
    2497: "Urge to destroy",
    2498: "Full mental breakdown",
    2499: "Attempted suicide",
    2500: "Poisoned",
    2512: "Saw a captive crew member",
    2664: "Nausea",
    2667: "Protein deficiency",
    2668: "Fatty acids deficiency",
    2669: "Craving for carbohydrates",
    2670: "Vitamin deficiency anemia",
    2728: "Wound",
    2729: "Hauler slash",
    2798: "Received an electric shock",
    2843: "I was held as a slave",
    3090: "Burned hands",
    3091: "I messed up",
    3092: "Injured",
    3093: "Vision loss",
    3094: "Inhaled toxic fumes",
    3095: "Exposed to loud noise",
    3118: "Spore infection",
    3120: "Spore eruption",
    3121: "Feeling ill",
    3133: "Chronic wound",
    3136: "Broken arm",
    3137: "Knocked unconscious",
    3160: "Unconscious",
    3164: "Interstellar travel sickness",
    3194: "Refusing to work (Uncomfortable environment)",
    3195: "I rebelled (Uncomfortable environment)",
    3307: "Minor comfort",
    3308: "Moderate comfort",
    3309: "Major comfort",
    3310: "Uncomfortable sleep",
    3311: "Sleeping comfortably",
    3312: "Uncomfortable leisure space",
    3313: "Good leisure space",
    3314: "Ate a great meal",
    3315: "Feeling sad",
    3321: "Feeling Aggressive (Minor mental break)",
    3322: "Destructive behavior (Major mental break)",
    3323: "Pyromania (Major mental break)",
    3324: "Interrupted sleep (No privacy)",
    3325: "Sleeping with privacy",
    3327: "No entertainment",
    3328: "Feeling claustrophobic (No hull windows)",
    3329: "Feeling energetic",
    3330: "Extremely frustrated",
    3332: "Had a good chat with a friend",
    3333: "Shared my feelings with a good friend",
    3334: "Connected with my best friend",
    3335: "Sleep deprived",
    3337: "In a good mood",
    3338: "In a great mood",
    3339: "In a fantastic mood",
    3340: "No one to talk to",
    3341: "Missing my friend",
    3342: "Missing my lover",
    3343: "My friend died",
    3344: "My best friend died",
    3345: "My lover died",
    3346: "I think my friend might be dead",
    3347: "I think my lover might be dead",
    3348: "My enemy is not bothering me",
    3349: "I think my enemy might be dead",
    3350: "My enemy is dead",
    3351: "Panicking",
    3352: "Refusing to work (Minor mental break)",
    3353: "Unconscious (Major mental break)",
    3354: "Saboteur (Extreme mental break)",
    3361: "No decorations",
    3368: "Drinking binge (Minor mental break)",
    3369: "Gaming binge (Minor mental break)",
    3370: "Intoxicated (Alcohol)",
    3371: "Hungover (Alcohol)",
    3380: "Lost my leader",
    3385: "Sleeping together with my lover",
    3440: "Post-surgery fatigue",
    3442: "Post-surgery rest",
    3445: "Wound",
    3446: "Wound",
    3447: "Burn wound",
    3448: "Wound",
    3465: "Healing boosted",
    3467: "Groggy",
    3481: "Had an unpleasant conversation",
    3660: "Wound",
    3699: "Wound",
    3700: "Wound",
    3927: "Under the influence of ISP",
    3928: "ISP side effect: Insomnia",
    3929: "ISP side effect: Tremor",
    3930: "ISP side effect: Lost appetite",
    3951: "Feeling weird sensations",
    3952: "Resting in an advanced medical bed",
    3971: "Stunned",
    4008: "In pain",
    4010: "I took painkillers",
    4011: "I used a Combat Stimulant",
    4013: "Drug side effect: Insomnia",
    4014: "Drug side effect: Tremor",
    4015: "Drug side effect: Lost appetite",
    4016: "Drug side effect: Brain fog",
    4017: "Drug side effect: Melancholy",
    4018: "Drug side effect: Fatigue",
    4019: "Drug side effect: Anxiety",
    4021: "I took some mood stimulants",
    4023: "CSP stage: euphoria",
    4026: "I ingested some alien enzyme",
    4034: "Sedated",
    4042: "CSP stage: Excitement",
    4043: "CSP stage: Crash",
    4074: "I studied",
    4075: "Burn wound from a flamethrower",
    4079: "An alien parasite is attached to my face",
    4080: "Bruised throat",
    4082: "Feeling a little unsafe",
    4302: "Siren World Awareness",
    4303: "Siren World Aftermath",
    4633: "I received medical treatment",
    4644: "Scar",
}

# Storage item IDs (elementaryId / mid on <s> elements inside <inv>).
STORAGE_IDS: dict[int, str] = {
    # Elementary resources (eid in game library)
    15: "Root vegetables",
    16: "Water",
    34: "Power",
    40: "Ice",
    63: "Oxygen",
    64: "CO2",
    71: "Bio Matter",
    73: "Heat",
    77: "Smoke",
    127: "Rubble",
    157: "Base Metals",
    158: "Energium",
    162: "Infrablock",
    169: "Noble Metals",
    170: "Carbon",
    171: "Raw Chemicals",
    172: "Hyperium",
    173: "Electronics Component",
    174: "Energy rod",
    175: "Plastics",
    176: "Chemicals",
    177: "Fabrics",
    178: "Hyperfuel",
    179: "Processed Food",
    706: "Fruits",
    707: "Artificial meat",
    712: "Space food",
    930: "Techblock",
    971: "Hazardous Gas",
    984: "Monster meat",
    985: "Human meat",
    1397: "Food group",
    1445: "Building tools",
    1759: "Hull Block",
    1858: "Credits",
    1873: "Infra Scrap",
    1874: "Soft Scrap",
    1886: "Hull Scrap",
    1919: "Energy block",
    1920: "Superblock",
    1921: "Soft block",
    1922: "Steel Plates",
    1924: "Optronics Component",
    1925: "Quantronics Component",
    1926: "Energy Cell",
    1932: "Fibers",
    1946: "Tech Scrap",
    1947: "Energy Scrap",
    2053: "Medical Supplies",
    2058: "IV Fluid",
    2452: "Water Vapor",
    2475: "Fertilizer",
    2657: "Nuts and seeds",
    2715: "Explosive ammunition",
    3196: "Advanced Power",
    3366: "Mild Alcohol",
    3378: "Grains and Hops",
    3419: "Augmentation Parts",
    3512: "Exotic ore",
    3513: "Basic ore",
    4027: "Alien Organs",
    4028: "Human Organs",
    # Physical items (mid in game library)
    725: "Rifle",
    728: "SMG",
    729: "Shotgun",
    760: "Pistol",
    1152: "Sentry gun X1",
    1954: "Human Corpse",
    3069: "Laser Rifle",
    3070: "Laser Pistol",
    3071: "Plasma Clustergun",
    3072: "Plasma Rifle",
    3077: "Hauler Corpse",
    3079: "Human Corpse (player)",
    3384: "Armored Vest",
    3386: "Remote Control",
    3388: "Oxygen Tank",
    3711: "Evolving Alien Core Remains",
    3712: "Alien Hive Core Remains",
    3960: "Flamethrower",
    3961: "Stun Rifle",
    3962: "Stun Pistol",
    3967: "Explosive Grenade Launcher",
    3968: "Basic scope",
    3969: "Tactical Grip",
    4005: "Painkillers",
    4006: "Combat Stimulant",
    4007: "Bandage",
    4030: "Nano Wound Dressing",
    4040: "Small Breaching Charge",
    4065: "Space Suit Oxygen Extender",
    4076: "Incendiary Grenade Launcher",
    4078: "Alien Parasite Corpse",
    4106: "Infester Corpse",
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
TECH_IDS: dict[int, str] = {
    2532: "Scanner",
    2533: "Shield Generator",
    2534: "Energy Turret",
    2538: "Large Storage",
    2539: "Autopsy Table",
    2559: "Medical Bed",
    2560: "Grow Bed with Light",
    2561: "CO2 Producer",
    2563: "Arcade Machine",
    2564: "Basic Entertainment",
    2565: "Solar Panel",
    2566: "X2 Power Generator",
    2567: "X3 Power Generator",
    2568: "Power Capacity Node",
    2569: "Item Fabricator",
    2570: "Micro-Weaver",
    2571: "Assembler",
    2572: "Energy Refinery",
    2573: "Chemical Refinery",
    2574: "Water Collector",
    2575: "Advanced Assembler",
    2576: "Composter",
    2577: "Hypersleep Chamber",
    2581: "Basic",
    2583: "Hyperium Hyperdrive",
    2584: "Chemical",
    2585: "Advanced",
    2586: "Optronic",
    2587: "Quantum",
    2589: "Weapons Console",
    2590: "Shields Console",
    2591: "Rocket Turret",
    2592: "Energy Turret (mk2)",
    2594: "X1 Power Generator",
    2595: "X1 Hyperdrive",
    2601: "Targeting Jammer",
    2605: "Laser Weapons",
    2606: "Plasma Weapons",
    2607: "Surgical Enhancement Facility",
    2609: "Implanted Rebreather",
    2610: "Ocular Implant",
    2611: "Synthetic Stomach Lining",
    2612: "Metal Refinery",
    2618: "Fabrics",
    2619: "Fibers",
    2622: "Bulletproof Vest",
    2623: "Botany",
    2626: "Advanced Nutrition",
    2627: "Space Food",
    2628: "Artificial Meat",
    2629: "Alcohol Beverage Machine",
    2630: "Grains and Hops",
    2694: "Optronics Fabricator",
    2696: "X1 Couch",
    2847: "Enslavement Facility",
    3024: "Logistics Robot Station",
    3025: "Salvage Robot Station",
    3112: "Recycler",
    3114: "Research Lab",
    3115: "Research Workbench",
    3116: "Research Experiment Table",
    3119: "Navigation Console",
    3122: "Operations Console",
    3124: "Crawler",
    3125: "Hauler",
    3127: "Robotics 01",
    3128: "Industry 01",
    3129: "Industry 02",
    3130: "Botany 02",
    3417: "Armored Vest",
    3420: "Anatomical Augmentation",
    3421: "Neural Augmentation",
    3422: "Nanotech Augmentation",
    3423: "Prefrontal Microcontroller",
    3464: "Sentry Gun X1",
    3704: "Alien Hive Core",
    3705: "Evolving Alien Core",
    3706: "Advanced Nutrition 02",
    3707: "Hamster (Flybot)",
    3708: "Chimp (Walkerbot)",
    3709: "X2 Hypersleep Tank",
    3710: "Rogue Bot Architecture",
    3970: "Advanced Medical Bed",
    3973: "Stun Weapons",
    3974: "Weapon Attachments 1",
    4024: "Alien Enzyme",
    4032: "Nano Wound Dressing",
    4092: "Stimulants",
    4093: "Advanced Disassembly",
    4132: "Learning Computer",
    4134: "Advanced Learning System",
    4529: "Combat Robot Station",
}

# Sorted name->id lookup for UI combo boxes
STORAGE_BY_NAME: dict[str, int] = {
    v: k for k, v in sorted(STORAGE_IDS.items(), key=lambda x: x[1])
}
TRAIT_BY_NAME: dict[str, int] = {
    v: k for k, v in sorted(TRAIT_IDS.items(), key=lambda x: x[1])
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

# Human-readable names for storage module types, derived from library/haven
# (aid graphics names + name text IDs + stores element structure).
STORAGE_MODULE_NAMES: dict[int, str] = {
    23: "Small Storage",  # storageTile1
    82: "Small Storage",  # name_tid=1344
    469: "Shield Generator",  # shieldGenBase4 ammo reserve
    789: "Large Storage",  # storage2f
    912: "Starter Storage",  # storage1F, unlimited
    2271: "Energy Turret",  # turret1Base2 ammo reserve
    2707: "Energy Turret",  # turret1Base2 variant
    2782: "Rocket Turret",  # turret4Base2 ammo reserve
    3063: "Body Storage",  # corpsesOnly: monster+human
    3065: "Robot Storage",  # corpsesOnly: android+robot
    3636: "Point Defense",  # turretPoint1base2 ammo reserve
    3923: "Medical Cabinet",  # name_tid=7726
    3978: "Hidden Vent",  # hiddenVentOpen, cap=1
    3982: "Hidden Stash",  # hiddenObject1Open, cap=1
    4304: "Point Defense",  # tactical projectile reserve
    4365: "Small Storage",  # name_tid=1344, solar variant
    4367: "Large Storage",  # solar variant
    4630: "Point Defense",  # tactical projectile reserve (variant)
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

# ---------------------------------------------------------------------------
# Text ID mappings (game object ID → library/texts entry ID)
# ---------------------------------------------------------------------------
# These are extracted from library/haven (tag: <name tid="..."/>) and allow
# src.texts_loader.game_texts to look up translated strings from the bundled
# data/library/texts file.  Items without a known text ID are absent; callers
# should fall back to the ``*_IDS`` English strings above.

# Backstory IDs (bsid on <pers>) → texts file entry ID.
BACKSTORY_TEXT_IDS: dict[int, int] = {
    1763: 660,   # Police officer
    1764: 661,   # Nurse
    1765: 662,   # Doctor
    1766: 663,   # Salesperson
    1767: 664,   # Cook
    1768: 665,   # Material mover
    1769: 666,   # Engineer
    1770: 667,   # Security guard
    1771: 668,   # Construction laborer
    1772: 669,   # Sheriff
    1773: 670,   # Lawyer
    1774: 671,   # Medical assistant
    1775: 672,   # Bartender
    1776: 673,   # Teacher
    1777: 674,   # Computer programmer
    1778: 675,   # Welder
    1779: 676,   # Firefighter
    1780: 677,   # Telemarketer
    1781: 678,   # Lab technician
    1782: 679,   # Chemical engineer
    1783: 680,   # Airline pilot
    1784: 681,   # Fighter pilot
    1785: 682,   # Driller
    1786: 683,   # Mining technician
    1787: 684,   # Geologist
    1788: 685,   # Farmer
    1789: 2240,  # Scientist
    1790: 686,   # Blacksmith
    1791: 687,   # Navigator
    3101: 4620,  # Game Developer
    3102: 4622,  # Astronaut
    3103: 4624,  # Psychologist
    3104: 4626,  # Comedian
    3105: 4628,  # Brewmaster
    3106: 4630,  # Electrician
    3107: 4632,  # Prizefighter
    3108: 4634,  # Athlete
}

# Personality trait IDs (traitId on <trait>) → texts file entry ID.
TRAIT_TEXT_IDS: dict[int, int] = {
    191: 216,    # Hero
    655: 413,    # Wimp
    656: 414,    # Clumsy
    1034: 567,   # Moody
    1035: 572,   # Smart
    1036: 574,   # Bloodlust
    1037: 576,   # Antisocial
    1038: 578,   # Needy
    1039: 580,   # Fast learner
    1040: 582,   # Lazy
    1041: 584,   # Hard working
    1042: 586,   # Psychopath
    1043: 588,   # Peace-loving
    1044: 590,   # Iron-willed
    1045: 592,   # Spacefarer
    1046: 594,   # Confident
    1047: 596,   # Neurotic
    1048: 598,   # Charming
    1533: 939,   # Iron stomach
    1534: 941,   # Nyctophilia
    1535: 943,   # Minimalist
    1560: 995,   # Talkative
    1562: 999,   # Gourmand
    2082: 2047,  # Alien lover
}

# Active condition IDs (conditionId on <condition>) → texts file entry ID.
CONDITION_TEXT_IDS: dict[int, int] = {
    193: 217,    194: 218,   713: 405,    714: 406,    715: 408,
    751: 435,    1003: 500,  1033: 565,   1053: 600,   1058: 643,
    1059: 649,   1060: 651,  1061: 653,   1062: 655,   1063: 657,
    1064: 689,   1065: 691,  1066: 693,   1096: 779,   1108: 781,
    1109: 412,   1112: 409,  1118: 486,   1119: 485,   1120: 487,
    1121: 410,   1122: 411,  1123: 788,   1124: 790,   1125: 792,
    1127: 807,   1430: 830,  1550: 961,   1561: 997,   1563: 1001,
    1581: 1013,  1582: 1014, 1583: 1015,  1584: 1019,  1585: 1020,
    1586: 1021,  1587: 1025, 1588: 1026,  1589: 1027,  1590: 1031,
    1591: 1033,  1592: 1035, 1593: 1037,  1594: 1039,  1595: 1041,
    1596: 1043,  1597: 1045, 1598: 1047,  1600: 1049,  1622: 1097,
    1623: 1099,  1624: 1101, 1625: 1103,  1626: 1105,  1648: 1238,
    1649: 1236,  1739: 1385, 1957: 408,   2055: 1890,  2056: 1892,
    2057: 1893,  2080: 2043, 2081: 2045,  2083: 2049,  2246: 2281,
    2247: 2283,  2248: 2285, 2417: 3529,  2482: 3696,  2490: 3707,
    2491: 3709,  2492: 3711, 2493: 3713,  2494: 3715,  2495: 3717,
    2496: 3719,  2497: 3721, 2498: 9428,  2499: 3728,  2500: 3730,
    2512: 3822,  2664: 3909, 2667: 3913,  2668: 3915,  2669: 3917,
    2670: 3919,  2728: 408,  2729: 4651,  2798: 4155,  2843: 4239,
    3090: 4604,  3091: 4606, 3092: 4608,  3093: 4610,  3094: 4612,
    3095: 4614,  3118: 4660, 3120: 4662,  3121: 4664,  3133: 4693,
    3136: 4698,  3137: 4700, 3160: 781,   3164: 4758,  3194: 4828,
    3195: 4830,  3307: 4993, 3308: 4994,  3309: 4995,  3310: 4997,
    3311: 4999,  3312: 5001, 3313: 5003,  3314: 5014,  3315: 5016,
    3321: 5018,  3322: 5051, 3323: 5053,  3324: 5058,  3325: 5060,
    3327: 5062,  3328: 5064, 3329: 5066,  3330: 5076,  3332: 5078,
    3333: 5080,  3334: 5082, 3335: 5084,  3337: 5086,  3338: 5088,
    3339: 5090,  3340: 5092, 3341: 5095,  3342: 5097,  3343: 5099,
    3344: 5101,  3345: 5103, 3346: 5105,  3347: 5107,  3348: 5109,
    3349: 5111,  3350: 5113, 3351: 5115,  3352: 5117,  3353: 5119,
    3354: 5121,  3361: 5128, 3368: 5139,  3369: 5141,  3370: 5143,
    3371: 5145,  3380: 5171, 3385: 5258,  3440: 5353,  3442: 5356,
    3445: 408,   3446: 408,  3447: 5392,  3448: 408,   3465: 5435,
    3467: 5437,  3481: 5469, 3660: 408,   3699: 408,   3700: 408,
    3927: 7566,  3928: 7579, 3929: 7582,  3930: 7584,  3951: 7626,
    3952: 7628,  3971: 7655, 4008: 7674,  4010: 7676,  4011: 7678,
    4013: 7684,  4014: 7682, 4015: 7680,  4016: 7686,  4017: 7688,
    4018: 7690,  4019: 7692, 4021: 7696,  4023: 7700,  4026: 7704,
    4034: 7724,  4042: 7731, 4043: 7732,  4074: 7772,  4075: 7859,
    4079: 7848,  4080: 7850, 4082: 1019,  4302: 8045,  4303: 8047,
    4633: 9387,  4644: 9426,
}

# Research technology IDs → texts file entry ID.
TECH_TEXT_IDS: dict[int, int] = {
    2532: 2276,  2533: 2182,  2534: 2307,  2538: 186,   2539: 1177,
    2559: 157,   2560: 3574,  2561: 1609,  2563: 1078,  2564: 7870,
    2565: 2184,  2566: 3864,  2567: 3865,  2568: 1749,  2569: 154,
    2570: 1819,  2571: 1787,  2572: 482,   2573: 474,   2574: 3626,
    2575: 1832,  2576: 3632,  2577: 1241,  2581: 3869,  2583: 3867,
    2584: 3877,  2585: 3870,  2586: 3871,  2587: 3872,  2589: 2252,
    2590: 2254,  2591: 442,   2592: 2307,  2594: 137,   2595: 267,
    2601: 4012,  2605: 5380,  2606: 5381,  2607: 5314,  2609: 5298,
    2610: 5300,  2611: 5302,  2612: 478,   2618: 3881,  2619: 1786,
    2622: 5251,  2623: 3879,  2626: 3883,  2627: 429,   2628: 423,
    2629: 5134,  2630: 5160,  2694: 1828,  2696: 895,   2847: 4169,
    3024: 4343,  3025: 4374,  3112: 160,   3114: 3852,  3115: 4572,
    3116: 4654,  3119: 2250,  3122: 2258,  3124: 4592,  3125: 4593,
    3127: 4676,  3128: 4678,  3129: 4680,  3130: 4682,  3417: 5252,
    3420: 5322,  3421: 5323,  3422: 5324,  3423: 5318,  3464: 5262,
    3704: 5955,  3705: 5957,  3706: 6030,  3707: 5916,  3708: 5959,
    3709: 5972,  3710: 5974,  3970: 7629,  3973: 7657,  3974: 7658,
    4024: 7702,  4032: 7716,  4092: 7882,  4093: 7884,  4132: 7762,
    4134: 7867,  4529: 8992,
}

# Storage item IDs → texts file entry ID.
# Elementary resources use the ``eid`` attribute in the save file;
# physical items use the ``mid`` attribute.
STORAGE_TEXT_IDS: dict[int, int] = {
    # Elementary resources (eid)
    15: 61,      16: 64,      34: 3455,    40: 72,      63: 3472,
    64: 3457,    71: 77,      73: 3469,    77: 3453,    127: 100,
    157: 184,    158: 109,    162: 108,    169: 190,    170: 191,
    171: 197,    172: 198,    173: 199,    174: 200,    175: 201,
    176: 202,    177: 203,    178: 204,    179: 196,    706: 422,
    707: 423,    712: 429,    930: 477,    971: 484,    984: 488,
    985: 490,    1397: 817,   1445: 836,   1759: 1393,  1858: 1564,
    1873: 1698,  1874: 1696,  1886: 1724,  1919: 1771,  1920: 1773,
    1921: 1775,  1922: 1778,  1924: 1780,  1925: 1782,  1926: 1784,
    1932: 1786,  1946: 1800,  1947: 1802,  2053: 1888,  2058: 1897,
    2452: 3630,  2475: 3635,  2657: 3899,  2715: 268,   3196: 4836,
    3366: 5136,  3378: 5160,  3419: 5320,  3512: 5531,  3513: 5533,
    4027: 7706,  4028: 7708,
    # Physical items (mid)
    725: 7857,   728: 502,    729: 504,    760: 7855,   1152: 5262,
    1954: 1807,  3069: 5374,  3070: 5372,  3071: 5378,  3072: 5376,
    3077: 4588,  3079: 4599,  3384: 5252,  3386: 5260,  3388: 5442,
    3711: 5965,  3712: 5964,  3960: 5295,  3961: 7640,  3962: 7638,
    3967: 7644,  3968: 7647,  3969: 7649,  4005: 7668,  4006: 7670,
    4007: 7672,  4030: 7716,  4040: 7728,  4065: 7735,  4076: 7861,
    4078: 7846,  4106: 7902,
}

# Text IDs for character attributes (attr_id matches text_id directly for these)
ATTRIBUTE_TEXT_IDS: dict[int, int] = {
    210: 210,  # Bravery
    212: 212,  # Zest
    213: 213,  # Intelligence
    214: 214,  # Perception
}

# Text IDs for crew skills (skill_id → text_id)
SKILL_TEXT_IDS: dict[int, int] = {
    2: 1414,   # Mining
    3: 1415,   # Botany
    4: 1416,   # Construction → "Construct" in EN
    5: 1417,   # Industry
    6: 1420,   # Medical
    7: 1422,   # Gunner
    8: 1424,   # Shielding
    9: 1425,   # Operations
    10: 1427,  # Weapons
    12: 1428,  # Carry → "Logistics" in EN
    14: 1423,  # Navigation
    16: 3851,  # Research
    22: 1413,  # Piloting
    # 13 (unknown/unused) has no text entry
}
