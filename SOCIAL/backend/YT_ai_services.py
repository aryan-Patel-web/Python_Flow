"""
YouTube AI Services - Thumbnail Generation & Content Creation
Handles AI thumbnail generation with frame extraction and LLM integration
"""

import os
import asyncio
import logging
import tempfile
import subprocess
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from PIL import Image, ImageDraw, ImageFont
import httpx
import base64
from io import BytesIO

logger = logging.getLogger(__name__)

class YouTubeAIService:
    """AI service for YouTube thumbnail generation and content"""
    
    def __init__(self):
        # Primary LLM: Mistral
        self.mistral_api_key = os.getenv("MISTRAL_API_KEY")
        # Fallback LLM: Groq
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        
        # Check which services are available
        self.has_mistral = bool(self.mistral_api_key)
        self.has_groq = bool(self.groq_api_key)
        # self.has_ffmpeg = self._check_ffmpeg()
        # Force disable FFmpeg on Windows for now
        import platform
        self.has_ffmpeg = self._check_ffmpeg() if platform.system() != 'Windows' else False
        if platform.system() == 'Windows':
            logger.warning("FFmpeg disabled on Windows - using fallback frame generation")
        
        logger.info(f"YouTube AI Service initialized - Mistral: {self.has_mistral}, Groq: {self.has_groq}, FFmpeg: {self.has_ffmpeg}")
    
    def _check_ffmpeg(self) -> bool:
        """Check if FFmpeg is available"""
        try:
            subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
            return True
        except:
            logger.warning("FFmpeg not available - will use fallback methods")
            return False
    
    async def generate_thumbnail_options(
        self,
        video_url: str,
        video_title: str,
        style: str = "indian"
    ) -> Dict:
        """
        Main method: Generate 3 thumbnail variations
        Returns: {"success": bool, "thumbnails": [{"url": str, "text": str, "ctr_score": float}]}
        """
        try:
            logger.info(f"Generating thumbnails for: {video_title}")
            
            # Step 1: Extract frames from video
            frames = await self._extract_frames_with_fallback(video_url)
            
            if not frames or len(frames) == 0:
                return {
                    "success": False,
                    "error": "Failed to extract video frames"
                }
            
            # Step 2: Generate text overlays using LLM
            overlay_texts = await self._generate_overlay_texts_with_fallback(video_title, style)
            
            # Step 3: Create thumbnails with overlays
            thumbnails = []
            for i, (frame, text) in enumerate(zip(frames[:3], overlay_texts[:3])):
                thumbnail_data = await self._create_thumbnail_with_text(
                    frame, text, style, variation=i+1
                )
                
                thumbnails.append({
                    "url": thumbnail_data["url"],
                    "text": text,
                    "ctr_score": self._predict_ctr_score(text, style),
                    "variation": i+1,
                    "width": 1280,
                    "height": 720
                })
            
            return {
                "success": True,
                "thumbnails": thumbnails,
                "method": "ffmpeg" if self.has_ffmpeg else "fallback",
                "llm_used": "mistral" if self.has_mistral else ("groq" if self.has_groq else "mock")
            }
            
        except Exception as e:
            logger.error(f"Thumbnail generation failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _extract_frames_with_fallback(self, video_url: str) -> List[Image.Image]:
        """Extract frames with multiple fallback methods"""
        
        # Method 1: FFmpeg (fastest, most reliable)
        if self.has_ffmpeg:
            try:
                frames = await self._extract_frames_ffmpeg(video_url)
                if frames:
                    logger.info("Frames extracted using FFmpeg")
                    return frames
            except Exception as e:
                logger.warning(f"FFmpeg extraction failed: {e}")
        
        # Method 2: Manual frame extraction (PIL-based fallback)
        try:
            frames = await self._extract_frames_manual(video_url)
            if frames:
                logger.info("Frames extracted using manual method")
                return frames
        except Exception as e:
            logger.warning(f"Manual extraction failed: {e}")
        
        # Method 3: Generate solid color frames (last resort)
        logger.warning("Using fallback solid color frames")
        return self._generate_fallback_frames()
    
    async def _extract_frames_ffmpeg(self, video_url: str) -> List[Image.Image]:
        """Extract frames using FFmpeg"""
        try:
            # Download video temporarily
            temp_video = await self._download_video(video_url)
            
            # Get video duration
            duration = self._get_video_duration_ffmpeg(temp_video)
            
            # Calculate timestamps (20%, 50%, 80%)
            timestamps = [duration * 0.2, duration * 0.5, duration * 0.8]
            
            frames = []
            for i, timestamp in enumerate(timestamps):
                # output_path = tempfile.mktemp(suffix=f'_frame_{i}.jpg')
                # Windows-safe temp file
                import platform
                if platform.system() == 'Windows':
                    output_path = os.path.join(tempfile.gettempdir(), f'frame_{i}_{int(datetime.now().timestamp())}.jpg')
                else:
                    output_path = tempfile.mktemp(suffix=f'_frame_{i}.jpg')
                
                # FFmpeg command
                cmd = [
                    'ffmpeg',
                    '-ss', str(timestamp),
                    '-i', temp_video,
                    '-vframes', '1',
                    '-q:v', '2',
                    '-y',
                    output_path
                ]
                
                subprocess.run(cmd, capture_output=True, check=True, timeout=30)
                
                # Load frame
                frame = Image.open(output_path)
                frames.append(frame)
                
                # Cleanup
                os.unlink(output_path)
            
            # Cleanup temp video
            os.unlink(temp_video)
            
            return frames
            
        except Exception as e:
            logger.error(f"FFmpeg frame extraction failed: {e}")
            raise
    
    def _get_video_duration_ffmpeg(self, video_path: str) -> float:
        """Get video duration using FFprobe"""
        try:
            cmd = [
                'ffprobe',
                '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                video_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            return float(result.stdout.strip())
        except:
            return 30.0  # Default 30 seconds
    
    async def _extract_frames_manual(self, video_url: str) -> List[Image.Image]:
        """Manual frame extraction fallback (downloads video, extracts via PIL)"""
        try:
            # For videos under 10MB, download and process
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.head(video_url)
                content_length = int(response.headers.get('content-length', 0))
                
                if content_length > 10 * 1024 * 1024:  # >10MB
                    raise Exception("Video too large for manual extraction")
                
                # Download
                response = await client.get(video_url)
                temp_video = tempfile.mktemp(suffix='.mp4')
                
                with open(temp_video, 'wb') as f:
                    f.write(response.content)
                
                # Try to extract using any available method
                # This is a placeholder - in production, use moviepy or cv2
                frames = self._generate_fallback_frames()
                
                os.unlink(temp_video)
                return frames
                
        except Exception as e:
            logger.error(f"Manual extraction failed: {e}")
            raise
    
    def _generate_fallback_frames(self) -> List[Image.Image]:
        """Generate solid color frames as last resort"""
        colors = ['#FF6B6B', '#4ECDC4', '#FFE66D']
        frames = []
        
        for color in colors:
            img = Image.new('RGB', (1280, 720), color)
            frames.append(img)
        
        return frames
    
    async def _download_video(self, video_url: str) -> str:
        """Download video to temp file"""
        try:
            async with httpx.AsyncClient(timeout=60, follow_redirects=True) as client:
                response = await client.get(video_url)
                
                if response.status_code == 200:
                    temp_file = tempfile.mktemp(suffix='.mp4')
                    with open(temp_file, 'wb') as f:
                        f.write(response.content)
                    return temp_file
                else:
                    raise Exception(f"Download failed: {response.status_code}")
                    
        except Exception as e:
            logger.error(f"Video download failed: {e}")
            raise
    
    async def _generate_overlay_texts_with_fallback(
        self, 
        video_title: str, 
        style: str
    ) -> List[str]:
        """Generate text overlays with LLM fallback"""
        
        # Try primary: Mistral
        if self.has_mistral:
            try:
                texts = await self._generate_texts_mistral(video_title, style)
                if texts and len(texts) >= 3:
                    logger.info("Overlay texts generated using Mistral")
                    return texts
            except Exception as e:
                logger.warning(f"Mistral text generation failed: {e}")
        
        # Fallback 1: Groq
        if self.has_groq:
            try:
                texts = await self._generate_texts_groq(video_title, style)
                if texts and len(texts) >= 3:
                    logger.info("Overlay texts generated using Groq")
                    return texts
            except Exception as e:
                logger.warning(f"Groq text generation failed: {e}")
        
        # Fallback 2: Mock generation
        logger.warning("Using mock text generation")
        return self._generate_mock_texts(video_title)
    
    async def _generate_texts_mistral(self, video_title: str, style: str) -> List[str]:
        """Generate texts using Mistral API"""
        try:
            prompt = f"""Generate 3 YouTube thumbnail text overlays for: "{video_title}"

Style: {style}
Requirements:
- Maximum 5 words each
- Bold, attention-grabbing
- Include numbers if relevant
- Variation 1: Question format
- Variation 2: Benefit-driven
- Variation 3: Curiosity gap

Return ONLY 3 texts, one per line, no numbering."""

            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    "https://api.mistral.ai/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.mistral_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "mistral-small-latest",
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": 100,
                        "temperature": 0.9
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    content = data["choices"][0]["message"]["content"]
                    texts = [line.strip() for line in content.strip().split('\n') if line.strip()]
                    return texts[:3]
                else:
                    raise Exception(f"Mistral API error: {response.status_code}")
                    
        except Exception as e:
            logger.error(f"Mistral generation failed: {e}")
            raise
    
    async def _generate_texts_groq(self, video_title: str, style: str) -> List[str]:
        """Generate texts using Groq API"""
        try:
            prompt = f"""Generate 3 YouTube thumbnail text overlays for: "{video_title}"

Style: {style}
Requirements:
- Maximum 5 words each
- Bold, attention-grabbing
- Include numbers if relevant

Return ONLY 3 texts, one per line."""

            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.groq_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "mixtral-8x7b-32768",
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": 100,
                        "temperature": 0.9
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    content = data["choices"][0]["message"]["content"]
                    texts = [line.strip() for line in content.strip().split('\n') if line.strip()]
                    return texts[:3]
                else:
                    raise Exception(f"Groq API error: {response.status_code}")
                    
        except Exception as e:
            logger.error(f"Groq generation failed: {e}")
            raise
    
    def _generate_mock_texts(self, video_title: str) -> List[str]:
        """Generate mock texts as last resort"""
        return [
            f"WHY {video_title[:15].upper()}?",
            f"SECRETS OF {video_title[:12].upper()}",
            f"SHOCKING {video_title[:15].upper()}"
        ]
    
    async def _create_thumbnail_with_text(
        self,
        base_image: Image.Image,
        text: str,
        style: str,
        variation: int
    ) -> Dict:
        """Create thumbnail with text overlay"""
        try:
            # Resize to YouTube thumbnail size
            thumbnail = base_image.resize((1280, 720), Image.Resampling.LANCZOS)
            draw = ImageDraw.Draw(thumbnail)
            
            # Load font (fallback to default if not found)
            try:
                # Try Windows font paths first
                import platform
                if platform.system() == 'Windows':
                    font = ImageFont.truetype("C:\\Windows\\Fonts\\arialbd.ttf", 80)
                else:
                    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 80)
            except:
                font = ImageFont.load_default()


            # try:
            #     font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 80)
            # except:
            #     font = ImageFont.load_default()
            



            # Calculate text position
            text_bbox = draw.textbbox((0, 0), text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            
            x = (1280 - text_width) // 2
            y = 550  # Bottom center
            
            # Draw background rectangle
            padding = 20
            draw.rectangle(
                [x - padding, y - padding, x + text_width + padding, y + text_height + padding],
                fill=(0, 0, 0, 200)
            )
            
            # Draw text with outline
            outline_color = "black"
            text_color = "yellow" if style == "indian" else "white"
            
            # Outline
            for adj in range(-2, 3):
                for adj2 in range(-2, 3):
                    draw.text((x+adj, y+adj2), text, font=font, fill=outline_color)
            
            # Main text
            draw.text((x, y), text, font=font, fill=text_color)
            
            # Convert to base64 data URL
            buffered = BytesIO()
            thumbnail.save(buffered, format="JPEG", quality=95)
            img_str = base64.b64encode(buffered.getvalue()).decode()
            data_url = f"data:image/jpeg;base64,{img_str}"
            
            return {
                "url": data_url,
                "format": "data_url"
            }
            
        except Exception as e:
            logger.error(f"Thumbnail creation failed: {e}")
            raise
    
    def _predict_ctr_score(self, text: str, style: str) -> float:
        """Predict CTR score based on text analysis"""
        score = 50.0
        
        # Factors that increase CTR
        if any(char.isdigit() for char in text):
            score += 15
        if '?' in text:
            score += 10
        if len(text.split()) <= 5:
            score += 10
        if any(word in text.upper() for word in ['SECRET', 'TRICK', 'HACK', 'FREE', 'WHY', 'HOW']):
            score += 15
        if style == "indian":
            score += 5
        
        return min(score, 95.0)