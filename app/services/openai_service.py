"""
OpenAI integration service for AI processing and response generation.
"""

from openai import AsyncOpenAI
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class OpenAIService:
    """Service for AI processing using OpenAI API"""
    
    def __init__(self, api_key: str):
        """
        Initialize OpenAI service.
        
        Args:
            api_key: OpenAI API key
        """
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = "gpt-4o-mini"
    
    async def generate_brief(
        self, 
        transcript: str,
        previous_brief: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Generate meeting briefing from transcript.
        
        Args:
            transcript: Meeting transcript text
            previous_brief: Previous briefing for context
            
        Returns:
            Dict containing brief and key points
        """
        try:
            system_prompt = """You are a meeting assistant. Generate concise briefings from meeting transcripts.
            
Your briefing should include:
1. Main topics being discussed
2. Key decisions made
3. Action items mentioned
4. Current discussion focus

Keep it concise and informative."""
            
            user_prompt = f"Transcript:\n{transcript}\n\nGenerate a brief meeting summary."
            
            if previous_brief:
                user_prompt = f"Previous brief:\n{previous_brief}\n\n{user_prompt}\n\nUpdate the brief with new information."
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            brief_text = response.choices[0].message.content
            
            # Extract key points
            key_points = await self._extract_key_points(brief_text)
            
            return {
                "brief": brief_text,
                "key_points": key_points
            }
            
        except Exception as e:
            logger.error(f"Error generating brief: {e}")
            raise
    
    async def _extract_key_points(self, brief: str) -> List[str]:
        """Extract key points from brief"""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Extract 3-5 key bullet points from this meeting brief. Return only the bullet points, one per line."
                    },
                    {"role": "user", "content": brief}
                ],
                temperature=0.3,
                max_tokens=200
            )
            
            points_text = response.choices[0].message.content
            points = [p.strip("- •") for p in points_text.split("\n") if p.strip()]
            return points[:5]
            
        except Exception as e:
            logger.error(f"Error extracting key points: {e}")
            return []
    
    async def generate_response(
        self, 
        question: str, 
        context: str
    ) -> str:
        """
        Generate response to user question based on meeting context.
        
        Args:
            question: User's question
            context: Meeting transcript/context
            
        Returns:
            AI-generated response text
        """
        try:
            system_prompt = """You are an AI assistant in a live meeting. Answer questions based on the meeting discussion.
            
Guidelines:
- Be concise and natural
- Base answers on the meeting context provided
- If information isn't in the context, say so politely
- Keep responses suitable for speaking aloud in a meeting
- Aim for 2-3 sentences"""
            
            user_prompt = f"""Meeting context:
{context}

Question: {question}

Provide a natural, concise response suitable for speaking in the meeting."""
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=150
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise
    
    async def analyze_speakers(self, transcript: str) -> List[str]:
        """
        Extract list of speakers from transcript.
        
        Args:
            transcript: Meeting transcript
            
        Returns:
            List of speaker names/identifiers
        """
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Extract unique speaker names/identifiers from this transcript. Return as a comma-separated list."
                    },
                    {"role": "user", "content": transcript}
                ],
                temperature=0.3,
                max_tokens=100
            )
            
            speakers_text = response.choices[0].message.content
            speakers = [s.strip() for s in speakers_text.split(",") if s.strip()]
            return speakers
            
        except Exception as e:
            logger.error(f"Error analyzing speakers: {e}")
            return []
