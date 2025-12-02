import asyncio
import uuid
from datetime import timezone
import asyncpg
import argparse
from pathlib import Path
from telethon import TelegramClient, events
from config import *
from sql_queries import *
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
db_pool = None


async def init_db():
    """Initialize database connection pool and create tables"""
    global db_pool
    logger.info("Initializing database connection...")
    db_pool = await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=10)
    
    async with db_pool.acquire() as conn:
        await conn.execute(CREATE_TABLE_USER_GROUP_MEDIA)
        logger.info("Database tables initialized successfully")


async def save_media_to_db(conn, user_id, group_id, media_bytes, description, message_id):
    """Save media to database with MESSAGES_LIMIT constraint"""
    try:
        # Check if message already exists
        existing = await conn.fetchval(CHECK_MESSAGE_EXISTS, user_id, group_id, message_id)
        if existing:
            logger.info(f"Message {message_id} already exists, skipping...")
            return
        
        # Count current records for this user-group pair
        count = await conn.fetchval(COUNT_RECORDS, user_id, group_id)
        
        # If limit reached, delete oldest record
        if count >= MESSAGES_LIMIT:
            await conn.execute(DELETE_OLDEST, user_id, group_id)
            logger.info(f"Deleted oldest record for user {user_id}, group {group_id}")
        
        # Insert new media record
        record_id = await conn.fetchval(INSERT_MEDIA, user_id, group_id, media_bytes, description, message_id)
        logger.info(f"Saved media {record_id} for user {user_id}, group {group_id}")
        
    except Exception as e:
        logger.error(f"Error saving media: {e}")
        raise


async def is_user_allowed(sender_id, sender_username):
    """Check if user is in USERS_TO_RSS list"""
    if not sender_id:
        return False
    
    # Check by ID
    if sender_id in USERS:
        return True
    
    # Check by username
    if sender_username:
        username_clean = sender_username.lower()
        for user in USERS:
            if isinstance(user, str) and user.lower() == username_clean:
                return True
    
    return False


async def parse_and_save_media(entity, entity_id, is_user=False):
    """Parse messages with media from a chat and save to database"""
    try:
        logger.info(f"Parsing media from {'user' if is_user else 'group'} {entity_id}...")
        
        messages_count = 0
        skipped_count = 0
        
        async for message in client.iter_messages(entity, limit=None):
            # Check if message has media (photo, document, video, etc.)
            if not message.media:
                continue
            
            try:
                # Determine sender info
                sender_id = message.sender_id if message.sender_id else 0
                
                # Get sender entity to check username
                sender_username = None
                if sender_id:
                    try:
                        sender = await message.get_sender()
                        if sender and hasattr(sender, 'username'):
                            sender_username = sender.username
                    except:
                        pass
                
                # For groups: only save messages from users in USERS list
                if not is_user:
                    if not await is_user_allowed(sender_id, sender_username):
                        skipped_count += 1
                        continue
                
                # Try to download media as bytes
                media_bytes = await message.download_media(file=bytes)
                
                if media_bytes:
                    # Get description (caption)
                    description = message.message or ""
                    
                    # Determine user_id and group_id
                    if is_user:
                        user_id = entity_id
                        group_id = entity_id  # For user chats, group_id = user_id
                    else:
                        # For group messages, use sender id
                        user_id = sender_id
                        group_id = entity_id
                    
                    # Save to database
                    async with db_pool.acquire() as conn:
                        await save_media_to_db(
                            conn, 
                            user_id, 
                            group_id, 
                            media_bytes, 
                            description, 
                            message.id
                        )
                    
                    messages_count += 1
                    
                    # Stop if we reached the limit
                    if messages_count >= MESSAGES_LIMIT:
                        logger.info(f"Reached MESSAGES_LIMIT ({MESSAGES_LIMIT}), stopping...")
                        break
                    
            except Exception as e:
                logger.error(f"Error processing message {message.id}: {e}")
                continue
        
        logger.info(f"Processed {messages_count} messages with media from {'user' if is_user else 'group'} {entity_id} (skipped {skipped_count})")
        
    except Exception as e:
        logger.error(f"Error parsing media from {'user' if is_user else 'group'} {entity_id}: {e}")


async def main():
    """Main function to parse all groups and users"""
    try:
        # Initialize database
        await init_db()
        
        # Connect to Telegram
        await client.start()
        logger.info("Connected to Telegram")
        
        # Parse groups
        for group in GROUPS:
            try:
                entity = await client.get_entity(group)
                entity_id = entity.id
                await parse_and_save_media(entity, entity_id, is_user=False)
            except Exception as e:
                logger.error(f"Error processing group {group}: {e}")
        
        # Parse users
        for user in USERS:
            try:
                entity = await client.get_entity(user)
                entity_id = entity.id
                await parse_and_save_media(entity, entity_id, is_user=True)
            except Exception as e:
                logger.error(f"Error processing user {user}: {e}")
        
        logger.info("Parsing completed successfully")
        
    except Exception as e:
        logger.error(f"Error in main: {e}")
        raise
    finally:
        # Close connections
        if db_pool:
            await db_pool.close()
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())

