
from backend.quiz import QuizGenerator
from backend.summarize import YouTubeVideoSummarizer
from typing import Tuple
from langchain_core.messages.ai import AIMessage
from youtube_transcript_api import YouTubeTranscriptApi
import re
class ModelCalling:
    def __init__(self):
        pass
    
    def load_transcript(self,url: str) -> str | None:

        pattern = r'(?:v=|\/)([0-9A-Za-z_-]{11})'
        match = re.search(pattern, url)
        if match:
            video_id = match.group(1)
            try:
                captions = YouTubeTranscriptApi().fetch(video_id,languages=['en','hi']).snippets
                data = [f"{item.text} ({item.start})" for item in captions]
                return " ".join(data)
            except Exception as e:
                print(f"❌ Error fetching transcript: {e}")
                return None
    
    def generate_summary(self, url: str ,api_key : str) -> Tuple[AIMessage, "VideoSummary", dict]:
        
        summarizer = YouTubeVideoSummarizer(api_key)
        transcripts = self.load_transcript(url=url)
        response, parsed_output, summary = summarizer.summarize_video(transcripts)
        return response, parsed_output, summary
    
    def generate_quiz(self , url : str , api_key : str) :
        
        quiz_gen = QuizGenerator(api_key)
        transcripts = self.load_transcript(url=url)
        response = quiz_gen.generate_quiz(transcripts)
        return response
    