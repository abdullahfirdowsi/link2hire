"""
MongoDB service for data persistence.
Handles all database operations for conversations and job entries.
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from bson import ObjectId
from pymongo.errors import DuplicateKeyError, PyMongoError

from backend.config import settings
from backend.models.job_model import Conversation, JobEntry, ConversationState


logger = logging.getLogger(__name__)


class MongoDBService:
    """
    Service for MongoDB operations.
    Uses Motor for async MongoDB access.
    """
    
    def __init__(self):
        """Initialize MongoDB client and database."""
        self.client: Optional[AsyncIOMotorClient] = None
        self.db: Optional[AsyncIOMotorDatabase] = None
        self._connected = False
    
    async def connect(self):
        """Establish connection to MongoDB."""
        if self._connected:
            return
        
        try:
            logger.info("Connecting to MongoDB...")
            self.client = AsyncIOMotorClient(
                settings.mongodb_connection_string,
                serverSelectionTimeoutMS=5000
            )
            
            # Verify connection
            await self.client.admin.command('ping')
            
            self.db = self.client[settings.mongodb_database_name]
            self._connected = True
            
            # Create indexes
            await self._create_indexes()
            
            logger.info("MongoDB connected successfully")
        
        except Exception as e:
            logger.error(f"MongoDB connection failed: {str(e)}")
            raise
    
    async def disconnect(self):
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            self._connected = False
            logger.info("MongoDB disconnected")
    
    async def _create_indexes(self):
        """Create database indexes for performance."""
        try:
            # Conversations collection indexes
            conversations = self.db[settings.mongodb_collection_conversations]
            await conversations.create_index("conversation_id", unique=True)
            await conversations.create_index("state")
            await conversations.create_index("created_at")
            
            # Jobs collection indexes
            jobs = self.db[settings.mongodb_collection_jobs]
            await jobs.create_index("conversation_id")
            await jobs.create_index("posted_to_sheets")
            await jobs.create_index("posted_to_linkedin")
            await jobs.create_index("created_at")
            await jobs.create_index([("extracted_data.company", 1)])
            
            logger.info("Database indexes created successfully")
        
        except Exception as e:
            logger.warning(f"Index creation warning: {str(e)}")
    
    # ==================== Conversation Operations ====================
    
    async def save_conversation(self, conversation: Conversation) -> Dict[str, Any]:
        """
        Save a new conversation to database.
        
        Args:
            conversation: Conversation object to save
            
        Returns:
            Saved conversation document
            
        Raises:
            DuplicateKeyError: If conversation_id already exists
        """
        try:
            collection = self.db[settings.mongodb_collection_conversations]
            
            conversation_dict = conversation.dict(by_alias=True, exclude={"id"})
            conversation_dict["created_at"] = datetime.utcnow()
            conversation_dict["updated_at"] = datetime.utcnow()
            
            result = await collection.insert_one(conversation_dict)
            conversation_dict["_id"] = str(result.inserted_id)
            
            logger.info(f"Conversation saved: {conversation.conversation_id}")
            return conversation_dict
        
        except DuplicateKeyError:
            logger.error(f"Duplicate conversation_id: {conversation.conversation_id}")
            raise
        except Exception as e:
            logger.error(f"Failed to save conversation: {str(e)}")
            raise
    
    async def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """
        Retrieve conversation by ID.
        
        Args:
            conversation_id: Conversation identifier
            
        Returns:
            Conversation object or None if not found
        """
        try:
            collection = self.db[settings.mongodb_collection_conversations]
            doc = await collection.find_one({"conversation_id": conversation_id})
            
            if doc:
                doc["_id"] = str(doc["_id"])
                return Conversation(**doc)
            
            logger.warning(f"Conversation not found: {conversation_id}")
            return None
        
        except Exception as e:
            logger.error(f"Failed to retrieve conversation: {str(e)}")
            raise
    
    async def update_conversation(self, conversation: Conversation) -> bool:
        """
        Update existing conversation.
        
        Args:
            conversation: Updated conversation object
            
        Returns:
            True if updated successfully
        """
        try:
            collection = self.db[settings.mongodb_collection_conversations]
            
            conversation_dict = conversation.dict(by_alias=True, exclude={"id"})
            conversation_dict["updated_at"] = datetime.utcnow()
            
            result = await collection.update_one(
                {"conversation_id": conversation.conversation_id},
                {"$set": conversation_dict}
            )
            
            if result.modified_count > 0:
                logger.info(f"Conversation updated: {conversation.conversation_id}")
                return True
            
            logger.warning(f"Conversation not modified: {conversation.conversation_id}")
            return False
        
        except Exception as e:
            logger.error(f"Failed to update conversation: {str(e)}")
            raise
    
    async def get_conversations_by_state(
        self,
        state: ConversationState,
        limit: int = 100
    ) -> List[Conversation]:
        """
        Get conversations by state.
        
        Args:
            state: Conversation state to filter by
            limit: Maximum number of results
            
        Returns:
            List of conversations
        """
        try:
            collection = self.db[settings.mongodb_collection_conversations]
            cursor = collection.find({"state": state.value}).limit(limit)
            
            conversations = []
            async for doc in cursor:
                doc["_id"] = str(doc["_id"])
                conversations.append(Conversation(**doc))
            
            logger.info(f"Retrieved {len(conversations)} conversations with state {state}")
            return conversations
        
        except Exception as e:
            logger.error(f"Failed to retrieve conversations by state: {str(e)}")
            raise
    
    # ==================== Job Entry Operations ====================
    
    async def save_job_entry(self, job_entry: JobEntry) -> Dict[str, Any]:
        """
        Save a new job entry to database.
        
        Args:
            job_entry: JobEntry object to save
            
        Returns:
            Saved job entry document
        """
        try:
            collection = self.db[settings.mongodb_collection_jobs]
            
            job_dict = job_entry.dict(by_alias=True, exclude={"id"})
            job_dict["created_at"] = datetime.utcnow()
            job_dict["updated_at"] = datetime.utcnow()
            
            result = await collection.insert_one(job_dict)
            job_dict["_id"] = str(result.inserted_id)
            
            logger.info(f"Job entry saved: {job_dict['_id']}")
            return job_dict
        
        except Exception as e:
            logger.error(f"Failed to save job entry: {str(e)}")
            raise
    
    async def get_job_entry(self, job_id: str) -> Optional[JobEntry]:
        """
        Retrieve job entry by ID.
        
        Args:
            job_id: Job entry identifier
            
        Returns:
            JobEntry object or None if not found
        """
        try:
            collection = self.db[settings.mongodb_collection_jobs]
            query = {"_id": ObjectId(job_id)} if ObjectId.is_valid(job_id) else {"_id": job_id}
            doc = await collection.find_one(query)
            
            if doc:
                doc["_id"] = str(doc["_id"])
                return JobEntry(**doc)
            
            logger.warning(f"Job entry not found: {job_id}")
            return None
        
        except Exception as e:
            logger.error(f"Failed to retrieve job entry: {str(e)}")
            raise
    
    async def update_job_entry(self, job_entry: JobEntry) -> bool:
        """
        Update existing job entry.
        
        Args:
            job_entry: Updated job entry object
            
        Returns:
            True if updated successfully
        """
        try:
            collection = self.db[settings.mongodb_collection_jobs]
            
            job_dict = job_entry.dict(by_alias=True, exclude={"id"})
            job_dict["updated_at"] = datetime.utcnow()
            query = {"_id": ObjectId(job_entry.id)} if job_entry.id and ObjectId.is_valid(job_entry.id) else {"_id": job_entry.id}
            
            result = await collection.update_one(
                query,
                {"$set": job_dict}
            )
            
            if result.modified_count > 0:
                logger.info(f"Job entry updated: {job_entry.id}")
                return True
            
            logger.warning(f"Job entry not modified: {job_entry.id}")
            return False
        
        except Exception as e:
            logger.error(f"Failed to update job entry: {str(e)}")
            raise
    
    async def get_job_entries_by_conversation(
        self,
        conversation_id: str
    ) -> List[JobEntry]:
        """
        Get all job entries for a conversation.
        
        Args:
            conversation_id: Conversation identifier
            
        Returns:
            List of job entries
        """
        try:
            collection = self.db[settings.mongodb_collection_jobs]
            cursor = collection.find({"conversation_id": conversation_id})
            
            job_entries = []
            async for doc in cursor:
                doc["_id"] = str(doc["_id"])
                job_entries.append(JobEntry(**doc))
            
            logger.info(f"Retrieved {len(job_entries)} job entries for conversation {conversation_id}")
            return job_entries
        
        except Exception as e:
            logger.error(f"Failed to retrieve job entries: {str(e)}")
            raise
    
    async def get_unposted_jobs(self, limit: int = 50) -> List[JobEntry]:
        """
        Get job entries not yet posted to LinkedIn.
        
        Args:
            limit: Maximum number of results
            
        Returns:
            List of unposted job entries
        """
        try:
            collection = self.db[settings.mongodb_collection_jobs]
            cursor = collection.find({"posted_to_linkedin": False}).limit(limit)
            
            job_entries = []
            async for doc in cursor:
                doc["_id"] = str(doc["_id"])
                job_entries.append(JobEntry(**doc))
            
            logger.info(f"Retrieved {len(job_entries)} unposted jobs")
            return job_entries
        
        except Exception as e:
            logger.error(f"Failed to retrieve unposted jobs: {str(e)}")
            raise


# Singleton instance
_mongodb_service_instance = None


def get_mongodb_service() -> MongoDBService:
    """Get or create singleton MongoDB service instance."""
    global _mongodb_service_instance
    if _mongodb_service_instance is None:
        _mongodb_service_instance = MongoDBService()
    return _mongodb_service_instance
