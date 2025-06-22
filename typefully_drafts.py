"""
Typefully Draft Creation & Management

Handles all draft creation, thread management, content formatting,
and media attachments for Typefully integration.
"""

import re
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum

from agents.typefully_client import TypefullyClient, ValidationError

logger = logging.getLogger(__name__)


class ContentType(Enum):
    """Content types for draft creation"""
    SINGLE_TWEET = "single_tweet"
    THREAD = "thread"
    LONG_FORM = "long_form"


@dataclass
class TweetMetrics:
    """Metrics for tweet content analysis"""
    character_count: int
    word_count: int
    hashtag_count: int
    mention_count: int
    url_count: int
    estimated_display_chars: int


@dataclass
class ThreadPreview:
    """Preview of a thread before creation"""
    total_tweets: int
    tweets: List[str]
    total_characters: int
    estimated_read_time: str
    content_type: ContentType


class TypefullyDraftManager:
    """
    Comprehensive draft creation and management system
    
    Features:
    - Single tweet and thread creation
    - Automatic and manual content splitting
    - Rich text formatting
    - Content validation and optimization
    - Draft preview and analysis
    """
    
    # Twitter/X content limits
    MAX_TWEET_LENGTH = 280
    MAX_THREAD_LENGTH = 25  # Twitter's thread limit
    MAX_MEDIA_ITEMS = 4     # Max media per tweet
    
    def __init__(self, client: TypefullyClient):
        """Initialize draft manager"""
        self.client = client
        logger.info("Typefully draft manager initialized")
    
    def analyze_content(self, content: str) -> TweetMetrics:
        """Analyze content and return detailed metrics"""
        char_count = len(content)
        word_count = len(content.split())
        hashtag_count = len(re.findall(r'#\w+', content))
        mention_count = len(re.findall(r'@\w+', content))
        url_count = len(re.findall(r'https?://\S+', content))
        
        return TweetMetrics(
            character_count=char_count,
            word_count=word_count,
            hashtag_count=hashtag_count,
            mention_count=mention_count,
            url_count=url_count,
            estimated_display_chars=char_count
        )
    
    def get_content_type(self, content: str) -> ContentType:
        """Determine the best content type for given text"""
        metrics = self.analyze_content(content)
        
        if metrics.character_count <= self.MAX_TWEET_LENGTH:
            return ContentType.SINGLE_TWEET
        elif '\n\n\n\n' in content or metrics.character_count <= self.MAX_TWEET_LENGTH * 5:
            return ContentType.THREAD
        else:
            return ContentType.LONG_FORM
    
    def format_rich_text(self, content: str) -> str:
        """Apply rich text formatting for Twitter/X compatibility"""
        formatted = content
        
        # Bold: **text** or *text* -> Unicode bold
        formatted = re.sub(r'\*\*(.+?)\*\*', lambda m: ''.join(chr(ord(c) + 0x1D400 - ord('A')) if 'A' <= c <= 'Z' else chr(ord(c) + 0x1D41A - ord('a')) if 'a' <= c <= 'z' else c for c in m.group(1)), formatted)
        
        # Clean up any remaining markdown
        formatted = re.sub(r'[*_`]', '', formatted)
        
        return formatted
    
    def split_content_smart(self, content: str, max_length: int = None) -> List[str]:
        """Intelligently split content into tweets"""
        max_length = max_length or self.MAX_TWEET_LENGTH
        
        if len(content) <= max_length:
            return [content]
        
        # Split by sentences first
        sentences = re.split(r'(?<=[.!?])\s+', content)
        tweets = []
        current_tweet = ""
        
        for sentence in sentences:
            test_tweet = current_tweet + (" " if current_tweet else "") + sentence
            
            if len(test_tweet) <= max_length:
                current_tweet = test_tweet
            else:
                if current_tweet:
                    tweets.append(current_tweet.strip())
                
                # If sentence is too long, split by words
                if len(sentence) > max_length:
                    word_tweets = self._split_by_words(sentence, max_length)
                    tweets.extend(word_tweets[:-1])
                    current_tweet = word_tweets[-1] if word_tweets else ""
                else:
                    current_tweet = sentence
        
        if current_tweet:
            tweets.append(current_tweet.strip())
        
        # Add thread numbering
        if len(tweets) > 1:
            numbered_tweets = []
            for i, tweet in enumerate(tweets, 1):
                if i == 1:
                    numbered_tweets.append(f"{tweet} 🧵")
                else:
                    numbered_tweets.append(f"{i}/{len(tweets)} {tweet}")
            return numbered_tweets
        
        return tweets
    
    def _split_by_words(self, text: str, max_length: int) -> List[str]:
        """Split text by words when sentences are too long"""
        words = text.split()
        tweets = []
        current_tweet = ""
        
        for word in words:
            test_tweet = current_tweet + (" " if current_tweet else "") + word
            
            if len(test_tweet) <= max_length:
                current_tweet = test_tweet
            else:
                if current_tweet:
                    tweets.append(current_tweet)
                current_tweet = word
        
        if current_tweet:
            tweets.append(current_tweet)
        
        return tweets
    
    def preview_thread(self, content: str, auto_split: bool = True) -> ThreadPreview:
        """Generate a preview of how content will be split into a thread"""
        if auto_split:
            tweets = self.split_content_smart(content)
        else:
            tweets = [tweet.strip() for tweet in re.split(r'\n{4,}', content) if tweet.strip()]
        
        total_chars = sum(len(tweet) for tweet in tweets)
        content_type = self.get_content_type(content)
        
        # Estimate read time
        word_count = sum(len(tweet.split()) for tweet in tweets)
        read_time_minutes = word_count / 200
        
        if read_time_minutes < 1:
            read_time = f"{int(read_time_minutes * 60)} seconds"
        else:
            read_time = f"{read_time_minutes:.1f} minutes"
        
        return ThreadPreview(
            total_tweets=len(tweets),
            tweets=tweets,
            total_characters=total_chars,
            estimated_read_time=read_time,
            content_type=content_type
        )
    
    def create_single_draft(self, content: str, schedule_date: Optional[Union[str, datetime]] = None,
                          auto_retweet: bool = False, auto_plug: bool = False,
                          share: bool = False, account_id: Optional[str] = None) -> Dict[str, Any]:
        """Create a single tweet draft"""
        metrics = self.analyze_content(content)
        if metrics.character_count > self.MAX_TWEET_LENGTH:
            raise ValidationError(f"Content exceeds {self.MAX_TWEET_LENGTH} characters. Consider using create_thread() instead.")
        
        formatted_content = self.format_rich_text(content)
        
        logger.info(f"Creating single draft: {metrics.character_count} characters")
        
        return self.client.create_draft(
            content=formatted_content,
            threadify=False,
            share=share,
            schedule_date=schedule_date,
            auto_retweet_enabled=auto_retweet,
            auto_plug_enabled=auto_plug,
            account_id=account_id
        )
    
    def create_thread(self, content: str, manual_split: bool = False,
                     schedule_date: Optional[Union[str, datetime]] = None,
                     auto_retweet: bool = False, auto_plug: bool = False,
                     share: bool = False, account_id: Optional[str] = None) -> Dict[str, Any]:
        """Create a thread from content"""
        if manual_split:
            tweets = [tweet.strip() for tweet in re.split(r'\n{4,}', content) if tweet.strip()]
            
            for i, tweet in enumerate(tweets):
                if len(tweet) > self.MAX_TWEET_LENGTH:
                    raise ValidationError(f"Tweet {i+1} exceeds {self.MAX_TWEET_LENGTH} characters")
            
            thread_content = "\n\n\n\n".join(tweets)
        else:
            tweets = self.split_content_smart(content)
            
            if len(tweets) > self.MAX_THREAD_LENGTH:
                raise ValidationError(f"Thread too long: {len(tweets)} tweets (max: {self.MAX_THREAD_LENGTH})")
            
            thread_content = "\n\n\n\n".join(tweets)
        
        logger.info(f"Creating thread with {len(tweets)} tweets")
        
        return self.client.create_draft(
            content=thread_content,
            threadify=False,  # We've already formatted it
            share=share,
            schedule_date=schedule_date,
            auto_retweet_enabled=auto_retweet,
            auto_plug_enabled=auto_plug,
            account_id=account_id
        )
    
    def create_from_generated_content(self, posts: List[str], 
                                    content_type: ContentType = ContentType.SINGLE_TWEET,
                                    schedule_interval_minutes: int = 60,
                                    **kwargs) -> List[Dict[str, Any]]:
        """Create multiple drafts from generated content"""
        results = []
        base_time = datetime.now(timezone.utc)
        
        for i, post_content in enumerate(posts):
            try:
                # Calculate schedule time
                schedule_time = base_time.replace(minute=0, second=0, microsecond=0)
                schedule_time = schedule_time.replace(hour=schedule_time.hour + (i * schedule_interval_minutes // 60))
                schedule_time = schedule_time.replace(minute=(i * schedule_interval_minutes) % 60)
                
                if content_type == ContentType.SINGLE_TWEET:
                    result = self.create_single_draft(
                        content=post_content,
                        schedule_date=schedule_time.isoformat(),
                        **kwargs
                    )
                elif content_type == ContentType.THREAD:
                    result = self.create_thread(
                        content=post_content,
                        schedule_date=schedule_time.isoformat(),
                        **kwargs
                    )
                else:
                    result = self.create_thread(
                        content=post_content,
                        manual_split=False,
                        schedule_date=schedule_time.isoformat(),
                        **kwargs
                    )
                
                results.append(result)
                logger.info(f"Created draft {i+1}/{len(posts)}")
                
            except Exception as e:
                logger.error(f"Failed to create draft {i+1}: {e}")
                results.append({"error": str(e), "content": post_content})
        
        return results
    
    def validate_draft_content(self, content: str, content_type: ContentType = None) -> Dict[str, Any]:
        """Validate content for draft creation"""
        metrics = self.analyze_content(content)
        detected_type = self.get_content_type(content)
        
        validation = {
            "valid": True,
            "warnings": [],
            "errors": [],
            "recommendations": [],
            "metrics": metrics,
            "detected_type": detected_type.value
        }
        
        if metrics.character_count == 0:
            validation["errors"].append("Content cannot be empty")
            validation["valid"] = False
        
        if metrics.character_count > self.MAX_TWEET_LENGTH and detected_type == ContentType.SINGLE_TWEET:
            validation["warnings"].append(f"Content exceeds single tweet limit ({self.MAX_TWEET_LENGTH} chars)")
            validation["recommendations"].append("Consider creating a thread instead")
        
        if metrics.hashtag_count > 3:
            validation["warnings"].append(f"Many hashtags detected ({metrics.hashtag_count})")
            validation["recommendations"].append("Consider reducing hashtags for better engagement")
        
        if metrics.url_count > 2:
            validation["warnings"].append("Multiple URLs detected")
            validation["recommendations"].append("Consider shortening URLs or splitting content")
        
        if content_type and content_type != detected_type:
            validation["warnings"].append(f"Content better suited for {detected_type.value}")
        
        return validation
    
    def get_draft_stats(self) -> Dict[str, Any]:
        """Get statistics about recent draft creation"""
        try:
            recent_scheduled = self.client.get_recently_scheduled_drafts()
            recent_published = self.client.get_recently_published_drafts()
            
            return {
                "recently_scheduled": len(recent_scheduled),
                "recently_published": len(recent_published),
                "total_recent": len(recent_scheduled) + len(recent_published),
                "last_activity": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to get draft stats: {e}")
            return {"error": str(e)} 