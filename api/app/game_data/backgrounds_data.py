# Path: api/app/game_data/backgrounds_data.py

# This list contains predefined background data based on SRD 5.1
PREDEFINED_BACKGROUNDS = [
    {
        "name": "Acolyte",
        "description": "You have spent your life in the service of a temple to a specific god or pantheon of gods. You act as an intermediary between the realm of the holy and the mortal world, performing sacred rites and offering sacrifices in order to conduct worshipers into the presence of the divine.",
        "skill_proficiencies": ["Insight", "Religion"],
        "tool_proficiencies": None,
        "languages": "Two of your choice",
        "equipment": "A holy symbol (a gift to you when you entered the priesthood), a prayer book or prayer wheel, 5 sticks of incense, vestments, a set of common clothes, and a belt pouch containing 15 gp.",
        "feature": {
            "name": "Shelter of the Faithful",
            "desc": "As an acolyte, you command the respect of those who share your faith, and you can perform the religious ceremonies of your deity. You and your adventuring companions can expect to receive free healing and care at a temple, shrine, or other established presence of your faith, though you must provide any material components needed for spells. Those who share your religion will support you (but only you) at a modest lifestyle."
        }
    },
    {
        "name": "Criminal",
        "description": "You are an experienced criminal with a history of breaking the law. You have spent a lot of time among other criminals and still have contacts within the criminal underworld.",
        "skill_proficiencies": ["Deception", "Stealth"],
        "tool_proficiencies": "One type of gaming set, thieves' tools",
        "languages": None,
        "equipment": "A crowbar, a set of dark common clothes including a hood, and a belt pouch containing 15 gp.",
        "feature": {
            "name": "Criminal Contact",
            "desc": "You have a reliable and trustworthy contact who acts as your liaison to a network of other criminals. You know how to get messages to and from your contact, even over great distances; specifically, you know the local messengers, corrupt caravan masters, and seedy sailors who can deliver messages for you."
        }
    },
    {
        "name": "Sage",
        "description": "You spent years learning the lore of the multiverse. You scoured manuscripts, studied scrolls, and listened to the greatest experts on the subjects that interest you. Your efforts have made you a master in your fields of study.",
        "skill_proficiencies": ["Arcana", "History"],
        "tool_proficiencies": None,
        "languages": "Two of your choice",
        "equipment": "A bottle of black ink, a quill, a small knife, a letter from a dead colleague posing a question you have not yet been able to answer, a set of common clothes, and a belt pouch containing 10 gp.",
        "feature": {
            "name": "Researcher",
            "desc": "When you attempt to learn or recall a piece of lore, if you do not know that information, you often know where and from whom you can obtain it. Usually, this information comes from a library, scriptorium, university, or a sage or other learned person or creature. Your DM might rule that the knowledge you seek is secreted away in an almost inaccessible place, or that it simply cannot be found."
        }
    }
]