CREATE TABLE IF NOT EXISTS guilds (
    id NUMERIC PRIMARY KEY,

    log_channel NUMERIC DEFAULT NULL,
    level_channel NUMERIC DEFAULT NULL,
    ping_user BOOL NOT NULL DEFAULT false,

    allow_commands BOOL NOT NULL DEFAULT true,
    disabled_commands TEXT[] NOT NULL DEFAULT '{}',

    premium_end TIMESTAMP DEFAULT NULL,

    qa_enabled BOOL NOT NULL DEFAULT true,
    qa_freeze TEXT NOT NULL DEFAULT '❄️',
    qa_force TEXT NOT NULL DEFAULT '🔒',
    qa_unforce TEXT NOT NULL DEFAULT '🔓',
    qa_trash TEXT NOT NULL DEFAULT '🗑️',
    qa_recount TEXT NOT NULL DEFAULT '🔃',
    qa_save TEXT NOT NULL DEFAULT '📥',

    prefixes VARCHAR(8)[] NOT NULL DEFAULT '{"sb!"}',

    xp_cooldown_on BOOL NOT NULL DEFAULT true,
    xp_cooldown SMALLINT DEFAULT 3,
    xp_cooldown_per SMALLINT DEFAULT 60,

    stack_pos_roles BOOL NOT NULL DEFAULT false,
    stack_xp_roles BOOL NOT NULL DEFAULT false,

    locale TEXT NOT NULL DEFAULT 'en_US'
);

CREATE TABLE IF NOT EXISTS users (
    id NUMERIC PRIMARY KEY,
    is_bot BOOL NOT NULL,
    votes SMALLINT NOT NULL DEFAULT 0,

    credits INT NOT NULL DEFAULT 0,
    donation_total INT NOT NULL DEFAULT 0,
    last_patreon_total INT NOT NULL DEFAULT 0,
    patron_status patron_status NOT NULL DEFAULT 'no',
    last_known_monthly INT NOT NULL DEFAULT 0,

    locale TEXT NOT NULL DEFAULT 'en_US',
    public BOOL NOT NULL DEFAULT true
);

CREATE TABLE IF NOT EXISTS autoredeem (
    user_id NUMERIC NOT NULL,
    guild_id NUMERIC NOT NULL,
    enabled_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users (id)
        ON DELETE CASCADE,
    FOREIGN KEY (guild_id) REFERENCES guilds (id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS members (
    user_id NUMERIC NOT NULL,
    guild_id NUMERIC NOT NULL,

    stars_given INT NOT NULL DEFAULT 0,
    stars_received INT NOT NULL DEFAULT 0,

    xp INT NOT NULL DEFAULT 0,
    level SMALLINT NOT NULL DEFAULT 0,

    FOREIGN KEY (user_id) REFERENCES users (id)
        ON DELETE CASCADE,
    FOREIGN KEY (guild_id) REFERENCES guilds (id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS starboards (
    id NUMERIC PRIMARY KEY,
    guild_id NUMERIC NOT NULL,

    webhook_url TEXT DEFAULT NULL,

    -- Appearance:
    color TEXT DEFAULT NULL,
    display_emoji TEXT DEFAULT '⭐',
    ping BOOL NOT NULL DEFAULT False,
    nicknames BOOL NOT NULL DEFAULT False,
    use_webhook BOOL NOT NULL DEFAULT false,
    webhook_name VARCHAR(32) DEFAULT NULL,
    webhook_avatar TEXT DEFAULT NULL,

    -- Requirements:
    required SMALLINT NOT NULL DEFAULT 3,
    required_remove SMALLINT NOT NULL DEFAULT 0,
    star_emojis TEXT[] DEFAULT '{⭐}',
    self_star BOOL NOT NULL DEFAULT False,
    allow_bots BOOL NOT NULL DEFAULT True,
    images_only BOOL NOT NULL DEFAULT False,

    regex TEXT NOT NULL DEFAULT '',
    exclude_regex TEXT NOT NULL DEFAULT '',

    channel_bl NUMERIC[] NOT NULL DEFAULT '{}',
    channel_wl NUMERIC[] NOT NULL DEFAULT '{}',

    -- Behaviour:
    autoreact BOOL NOT NULL DEFAULT True,
    remove_invalid BOOL NOT NULL DEFAULT True,
    link_deletes BOOL NOT NULL DEFAULT False,
    link_edits BOOL NOT NULL DEFAULT True,
    no_xp BOOL NOT NULL DEFAULT False,
    explore BOOL NOT NULL DEFAULT True,

    FOREIGN KEY (guild_id) REFERENCES guilds (id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS aschannels (
    id NUMERIC PRIMARY KEY,
    guild_id NUMERIC NOT NULL,

    emojis TEXT[] DEFAULT '{⭐}',
    min_chars SMALLINT NOT NULL DEFAULT 0,
    require_image BOOL NOT NULL DEFAULT False,
    regex TEXT NOT NULL DEFAULT '',
    exclude_regex TEXT NOT NULL DEFAULT '',

    delete_invalid BOOL NOT NULL DEFAULT False,

    FOREIGN KEY (guild_id) REFERENCES guilds (id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS permgroups (
    id SERIAL PRIMARY KEY,
    guild_id NUMERIC NOT NULL,
    index SMALLINT NOT NULL,
    name VARCHAR(32) NOT NULL,

    starboards NUMERIC[] DEFAULT '{}',
    channels NUMERIC[] DEFAULT '{}',

    FOREIGN KEY (guild_id) REFERENCES guilds (id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS permroles (
    permgroup_id BIGINT NOT NULL,
    role_id NUMERIC NOT NULL,
    index SMALLINT NOT NULL,

    allow_commands BOOL DEFAULT NULL,
    on_starboard BOOL DEFAULT NULL,
    give_stars BOOL DEFAULT NULL,
    gain_xp BOOL DEFAULT NULL,
    pos_roles BOOL DEFAULT NULL,
    xp_roles BOOL DEFAULT NULL,

    FOREIGN KEY (permgroup_id) REFERENCES permgroups (id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS xproles (
    role_id NUMERIC PRIMARY KEY,
    guild_id NUMERIC NOT NULL,
    required SMALLINT NOT NULL,

    FOREIGN KEY (guild_id) REFERENCES guilds (id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS posroles (
    role_id NUMERIC PRIMARY KEY,
    guild_id NUMERIC NOT NULL,
    max_users SMALLINT NOT NULL,

    FOREIGN KEY (guild_id) REFERENCES guilds (id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS members_posroles (
    role_id NUMERIC NOT NULL,
    user_id NUMERIC NOT NULL,
    guild_id NUMERIC NOT NULL,

    unique (role_id, user_id),

    FOREIGN KEY (role_id) REFERENCES posroles (role_id)
        ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users (id)
        ON DELETE CASCADE,
    FOREIGN KEY (guild_id) REFERENCES guilds (id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS messages (
    id NUMERIC PRIMARY KEY,
    guild_id NUMERIC NOT NULL,
    channel_id NUMERIC NOT NULL,
    author_id NUMERIC,

    is_nsfw BOOL NOT NULL,

    forced NUMERIC[] NOT NULL DEFAULT '{}',
    trashed BOOL NOT NULL DEFAULT false,
    frozen BOOL NOT NULL DEFAULT false,

    trash_reason TEXT DEFAULT NULL,

    FOREIGN KEY (guild_id) REFERENCES guilds (id)
        ON DELETE CASCADE,
    FOREIGN KEY (author_id) REFERENCES users (id)
        ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS starboard_messages (
    id NUMERIC PRIMARY KEY,
    orig_id NUMERIC NOT NULL,
    starboard_id NUMERIC NOT NULL,

    points SMALLINT NOT NULL DEFAULT 0,

    FOREIGN KEY (orig_id) REFERENCES messages (id)
        ON DELETE CASCADE,
    FOREIGN KEY (starboard_id) REFERENCES starboards (id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS reactions (
    id SERIAL PRIMARY KEY,
    emoji TEXT NOT NULL,
    message_id NUMERIC NOT NULL,

    FOREIGN KEY (message_id) REFERENCES messages (id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS reaction_users (
    reaction_id INT NOT NULL,
    user_id NUMERIC NOT NULL,

    FOREIGN KEY (reaction_id) REFERENCES reactions (id)
        ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users (id)
        ON DELETE CASCADE
);