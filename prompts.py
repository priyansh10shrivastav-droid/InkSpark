"""Prompt templates for InkSpark blog post generation."""


def build_prompt(topic: str, tone: str, word_count: int) -> str:
    """Build the prompt for generating a structured blog post.

    Args:
        topic: The subject of the blog post.
        tone: The tone of writing (e.g. Friendly, Formal).
        word_count: Target approximate word count.

    Returns:
        The formatted prompt instruction string.
    """
    return f"""You are a skilled blog writer. Write a blog post about: {topic}.
Tone: {tone}.
Length: about {word_count} words.
Structure the post exactly like this, using Markdown:
# [A catchy title]
## Introduction
(2 to 3 short paragraphs)
## [Section heading 1]
## [Section heading 2]
## [Section heading 3]
(Use 3 or 4 sections in total, each with 2 to 3 short paragraphs)
## Conclusion
(1 to 2 paragraphs with a clear takeaway)
Rules: use simple, clear English. Avoid filler phrases such as 'in today's fast-paced world'. Do not add a preamble or any text before the title. Do not add a list of sources."""
