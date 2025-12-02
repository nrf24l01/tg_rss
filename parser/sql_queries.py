"""SQL queries for user_group_media table operations"""

# Create table
CREATE_TABLE_USER_GROUP_MEDIA = """
CREATE TABLE IF NOT EXISTS user_group_media (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id BIGINT NOT NULL,
    group_id BIGINT NOT NULL,
    media BYTEA NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    message_id BIGINT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_user_group_media_user_id ON user_group_media(user_id);
CREATE INDEX IF NOT EXISTS idx_user_group_media_group_id ON user_group_media(group_id);
CREATE INDEX IF NOT EXISTS idx_user_group_media_created_at ON user_group_media(created_at);
"""

# Insert media record
INSERT_MEDIA = """
INSERT INTO user_group_media (user_id, group_id, media, description, message_id)
VALUES ($1, $2, $3, $4, $5)
RETURNING id;
"""

# Count records for a user-group pair
COUNT_RECORDS = """
SELECT COUNT(*) FROM user_group_media
WHERE user_id = $1 AND group_id = $2;
"""

# Delete oldest record for a user-group pair
DELETE_OLDEST = """
DELETE FROM user_group_media
WHERE id IN (
    SELECT id FROM user_group_media
    WHERE user_id = $1 AND group_id = $2
    ORDER BY created_at ASC
    LIMIT 1
);
"""

# Check if message already exists
CHECK_MESSAGE_EXISTS = """
SELECT id FROM user_group_media
WHERE user_id = $1 AND group_id = $2 AND message_id = $3;
"""
