# -*- coding: utf-8 -*-
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from absl.testing import absltest
import pathlib

media = pathlib.Path(__file__).parents[1] / "third_party"


class UnitTests(absltest.TestCase):

    def test_tokens_context_window(self):
        # [START tokens_context_window]
        from google import genai

        client = genai.Client()
        model_info = client.models.get(model="gemini-2.0-flash")
        print(f"{model_info.input_token_limit=}")
        print(f"{model_info.output_token_limit=}")
        # ( e.g., input_token_limit=30720, output_token_limit=2048 )
        # [END tokens_context_window]

    def test_tokens_text_only(self):
        # [START tokens_text_only]
        from google import genai

        client = genai.Client()
        prompt = "The quick brown fox jumps over the lazy dog."

        # Count tokens using the new client method.
        total_tokens = client.models.count_tokens(
            model="gemini-2.0-flash", contents=prompt
        )
        print("total_tokens: ", total_tokens)
        # ( e.g., total_tokens: 10 )

        response = client.models.generate_content(
            model="gemini-2.0-flash", contents=prompt
        )

        # The usage_metadata provides detailed token counts.
        print(response.usage_metadata)
        # ( e.g., prompt_token_count: 11, candidates_token_count: 73, total_token_count: 84 )
        # [END tokens_text_only]

    def test_tokens_chat(self):
        # [START tokens_chat]
        from google import genai
        from google.genai import types

        client = genai.Client()

        chat = client.chats.create(
            model="gemini-2.0-flash",
            history=[
                types.Content(
                    role="user", parts=[types.Part(text="Hi my name is Bob")]
                ),
                types.Content(role="model", parts=[types.Part(text="Hi Bob!")]),
            ],
        )
        # Count tokens for the chat history.
        print(
            client.models.count_tokens(
                model="gemini-2.0-flash", contents=chat.get_history()
            )
        )
        # ( e.g., total_tokens: 10 )

        response = chat.send_message(
            message="In one sentence, explain how a computer works to a young child."
        )
        print(response.usage_metadata)
        # ( e.g., prompt_token_count: 25, candidates_token_count: 21, total_token_count: 46 )

        # You can count tokens for the combined history and a new message.
        extra = types.UserContent(
            parts=[
                types.Part(
                    text="What is the meaning of life?",
                )
            ]
        )
        history = chat.get_history()
        history.append(extra)
        print(client.models.count_tokens(model="gemini-2.0-flash", contents=history))
        # ( e.g., total_tokens: 56 )
        # [END tokens_chat]

    def test_tokens_multimodal_image_inline(self):
        # [START tokens_multimodal_image_inline]
        from google import genai
        import PIL.Image

        client = genai.Client()
        prompt = "Tell me about this image"
        your_image_file = PIL.Image.open(media / "organ.jpg")

        # Count tokens for combined text and inline image.
        print(
            client.models.count_tokens(
                model="gemini-2.0-flash", contents=[prompt, your_image_file]
            )
        )
        # ( e.g., total_tokens: 263 )

        response = client.models.generate_content(
            model="gemini-2.0-flash", contents=[prompt, your_image_file]
        )
        print(response.usage_metadata)
        # ( e.g., prompt_token_count: 264, candidates_token_count: 80, total_token_count: 345 )
        # [END tokens_multimodal_image_inline]

    def test_tokens_multimodal_image_file_api(self):
        # [START tokens_multimodal_image_file_api]
        from google import genai

        client = genai.Client()
        prompt = "Tell me about this image"
        your_image_file = client.files.upload(file=media / "organ.jpg")

        print(
            client.models.count_tokens(
                model="gemini-2.0-flash", contents=[prompt, your_image_file]
            )
        )
        # ( e.g., total_tokens: 263 )

        response = client.models.generate_content(
            model="gemini-2.0-flash", contents=[prompt, your_image_file]
        )
        print(response.usage_metadata)
        # ( e.g., prompt_token_count: 264, candidates_token_count: 80, total_token_count: 345 )
        # [END tokens_multimodal_image_file_api]

    def test_tokens_multimodal_video_audio_file_api(self):
        # [START tokens_multimodal_video_audio_file_api]
        from google import genai
        import time

        client = genai.Client()
        prompt = "Tell me about this video"
        your_file = client.files.upload(file=media / "Big_Buck_Bunny.mp4")

        # Wait for the video to be processed.
        while your_file.state.name == "PROCESSING":
            print("processing video...")
            time.sleep(5)
            your_file = client.files.get(name=your_file.name)

        print(
            client.models.count_tokens(
                model="gemini-2.0-flash", contents=[prompt, your_file]
            )
        )
        # ( e.g., total_tokens: 300 )

        response = client.models.generate_content(
            model="gemini-2.0-flash", contents=[prompt, your_file]
        )
        print(response.usage_metadata)
        # ( e.g., prompt_token_count: 301, candidates_token_count: 60, total_token_count: 361 )
        # [END tokens_multimodal_video_audio_file_api]

    def test_tokens_multimodal_pdf_file_api(self):
        # [START tokens_multimodal_pdf_file_api]
        from google import genai

        client = genai.Client()
        sample_pdf = client.files.upload(file=media / "test.pdf")
        token_count = client.models.count_tokens(
            model="gemini-2.0-flash",
            contents=["Give me a summary of this document.", sample_pdf],
        )
        print(f"{token_count=}")

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=["Give me a summary of this document.", sample_pdf],
        )
        print(response.usage_metadata)
        # [END tokens_multimodal_pdf_file_api]

    def test_tokens_cached_content(self):
        # [START tokens_cached_content]
        from google import genai
        from google.genai import types
        import time

        client = genai.Client()
        your_file = client.files.upload(file=media / "a11.txt")

        cache = client.caches.create(
            model="gemini-1.5-flash-001",
            config={
                "contents": ["Here the Apollo 11 transcript:", your_file],
                "system_instruction": None,
                "tools": None,
            },
        )

        # Create a prompt.
        prompt = "Please give a short summary of this file."

        # Count tokens for the prompt (the cached content is not passed here).
        print(client.models.count_tokens(model="gemini-2.0-flash", contents=prompt))
        # ( e.g., total_tokens: 9 )

        response = client.models.generate_content(
            model="gemini-1.5-flash-001",
            contents=prompt,
            config=types.GenerateContentConfig(
                cached_content=cache.name,
            ),
        )
        print(response.usage_metadata)
        # ( e.g., prompt_token_count: ..., cached_content_token_count: ..., candidates_token_count: ... )
        client.caches.delete(name=cache.name)
        # [END tokens_cached_content]

    # ValueError: system_instruction parameter is not supported in Gemini API.
    def test_tokens_system_instruction(self):
        # [START tokens_system_instruction]
        from google import genai
        from google.genai import types

        client = genai.Client()
        prompt = "The quick brown fox jumps over the lazy dog."

        base_count = client.models.count_tokens(
            model="gemini-2.0-flash", contents=prompt
        )
        print("total_tokens (no system instruction):", base_count)
        # ( e.g., total_tokens: 10 )

        # When using a system instruction, include it in the count tokens config.
        # TODO: Uncomment once the API stops failing

        # count_with_sys = client.models.count_tokens(
        #     model="gemini-2.0-flash",
        #     contents=prompt,
        #     config=types.CountTokensConfig(system_instruction="You are a cat. Your name is Neko.")
        # )
        # print("total_tokens (with system instruction):", count_with_sys)
        # ( e.g., total_tokens: 21 )
        # [END tokens_system_instruction]

    # ValueError: tools parameter is not supported in Gemini API.
    def test_tokens_tools(self):
        # [START tokens_tools]
        from google import genai
        from google.genai import types

        client = genai.Client()
        prompt = (
            "I have 57 cats, each owns 44 mittens, how many mittens is that in total?"
        )
        print(client.models.count_tokens(model="gemini-2.0-flash", contents=prompt))
        # ( e.g., total_tokens: 22 )

        # Define the function declarations for the arithmetic operations
        add_function = types.FunctionDeclaration(
            name="add",
            description="Return the sum of a and b",
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "a": types.Schema(
                        type="NUMBER",
                        description="The first number",
                    ),
                    "b": types.Schema(
                        type="NUMBER",
                        description="The second number",
                    ),
                },
                required=["a", "b"],
            ),
        )

        subtract_function = types.FunctionDeclaration(
            name="subtract",
            description="Return the difference of a and b (a - b)",
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "a": types.Schema(
                        type="NUMBER",
                        description="The first number",
                    ),
                    "b": types.Schema(
                        type="NUMBER",
                        description="The second number",
                    ),
                },
                required=["a", "b"],
            ),
        )

        multiply_function = types.FunctionDeclaration(
            name="multiply",
            description="Return the product of a and b",
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "a": types.Schema(
                        type="NUMBER",
                        description="The first number",
                    ),
                    "b": types.Schema(
                        type="NUMBER",
                        description="The second number",
                    ),
                },
                required=["a", "b"],
            ),
        )

        divide_function = types.FunctionDeclaration(
            name="divide",
            description="Return the quotient of a divided by b",
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "a": types.Schema(
                        type="NUMBER",
                        description="The numerator",
                    ),
                    "b": types.Schema(
                        type="NUMBER",
                        description="The denominator (must not be zero)",
                    ),
                },
                required=["a", "b"],
            ),
        )
        tools = [
            types.Tool(function_declarations=[add_function]),
            types.Tool(function_declarations=[subtract_function]),
            types.Tool(function_declarations=[multiply_function]),
            types.Tool(function_declarations=[divide_function]),
        ]

        # Count tokens when tools are included. Tools increase the token count.
        # TODO: Uncomment once the API stops failing
        # tokens_with_tools = client.models.count_tokens(
        #     model="gemini-2.0-flash",
        #     contents=prompt,
        #     config=types.CountTokensConfig(tools=tools)
        # )
        # print(tokens_with_tools)
        # ( e.g., total_tokens: 206 )
        # [END tokens_tools]


if __name__ == "__main__":
    absltest.main()
