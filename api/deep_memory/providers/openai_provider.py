from openai import OpenAI
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)


#=======================================================================
# OpenAI provider
#=======================================================================
class OpenAIProvider:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)


    #=======================================================================
    # Generates text using OpenAI's responses API
    #=======================================================================
    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
    def generate_text(self, prompt: str) -> str:
        try:
            response = self.client.responses.create(
                model="gpt-5.1",
                input=prompt,
                reasoning={"effort": "medium"}
            )
            return response.output_text.strip()
        except Exception as e:
            raise RuntimeError(f"Failed to generate text: {e}")


    #=======================================================================
    # Generates vector embeddings for the given text
    #=======================================================================
    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
    def generate_embedding(self, text: str) -> list[float]:
        try:
            response = self.client.embeddings.create(
                input=text,
                model="text-embedding-3-small"
            )
            return response.data[0].embedding
        except Exception as e:
            raise RuntimeError(f"Failed to generate embedding: {e}")


    #=======================================================================
    # Describes an image using OpenAI's vision API
    #=======================================================================
    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
    def describe_image(self, image_url: str, prompt: str = "Describe what is in this image.") -> str:
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {"url": image_url},
                            },
                        ],
                    }
                ],
                max_tokens=300,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise RuntimeError(f"Failed to describe image: {e}")