
import logging
import openai

import tiktoken


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# a 'close enough' to 4097 allowed (allow some buffer)
# @TODO figure out the more precice math on this
TOKEN_CHUNK_SIZE = 4000
COMPLETION_TOKEN_SIZE = 200


class OpenAiVideoSummarizer(object):

    def __init__(self, target_model: str, api_key: str):
        self.openai_api_key = api_key
        self.target_model = target_model
        self.encoding = tiktoken.encoding_for_model(self.target_model)

    def set_api_key(self, api_key: str):
        self.openai_api_key = api_key

    def get_tokens(self, text: str) -> list:
        tokens = self.encoding.encode(text)
        logger.info(f"Token count: {len(tokens)}")
        return tokens

    def generate_summary(self, text: str) -> tuple[str, str]:
        """
        Generate a summary of the provided text using OpenAI API
        """
        error = summary = ""
        summaries = []
        # Initialize the OpenAI API client
        openai.api_key = self.openai_api_key

        # Use GPT to generate a summary
        instructions = "Please summarize the provided text"
        # truncate the text
        text_chunks = []
        tokens = self.get_tokens(text)
        if  len(tokens) > TOKEN_CHUNK_SIZE-COMPLETION_TOKEN_SIZE:
            text_chunks = self.chunk_summary(tokens, TOKEN_CHUNK_SIZE-COMPLETION_TOKEN_SIZE)
            logger.info(f"Chunking text into {len(text_chunks)} chunks")
        else:
            text_chunks = [text]
            logger.info(f"Summary within allowed length of {TOKEN_CHUNK_SIZE} tokens, no chunking needed")
        try:
            for index, chunk in enumerate(text_chunks):
                logger.info(f"Generating summary for chunk {index+1} of {len(text_chunks)}...")
                response = self.get_summary(instructions, chunk)
                summaries.append(response.choices[0].message.content.strip())
            if len(summaries) > 1:
                # now get the summary of all the summaries combined
                logger.info(f"Generating summary for all summaries...")
                combined_summary = " ".join(summaries)
                logger.info(f"number of tokens in combined summary: {len(self.get_tokens(combined_summary))}")
                response = self.get_summary(instructions, combined_summary)
                summary = response.choices[0].message.content.strip()
            else:
                summary = summaries[0]
        except Exception as e:
            error = f"Unexpected error: {e}"

        # Return the generated summary
        return (error, summary)

    def get_summary(self, instructions, chunk):
        # link to the OpenAI API documentation
        # https://beta.openai.com/docs/api-reference/summarization
        response = openai.ChatCompletion.create(
                    model=self.target_model,
                    messages=[
                        {"role": "system", "content": instructions},
                        {"role": "user", "content": chunk}
                    ],
                    temperature=0.2,
                    n=1,
                    max_tokens=COMPLETION_TOKEN_SIZE,
                    presence_penalty=0,
                    frequency_penalty=0.1,
                )
        return response

    def chunk_summary(self, tokens: list, chunck_size: int) -> list[str]:
        """
        Chunk the provided list of tokens into chunck_size sized chunks
        """
        chunks = []
        for i in range(0, len(tokens), chunck_size):
            chunks.append(self.encoding.decode(tokens[i:i + chunck_size]))
        return chunks