"""
Koda Prompt Assist — transforms spoken thoughts into well-structured LLM prompts.

When users speak naturally ("I need help writing a Python script that reads CSV
files and removes duplicate rows based on email"), this module restructures it
into a clear, effective prompt with context, constraints, and format guidance.

Works in two modes:
  1. Template-based (offline, always available) — detects intent and applies
     structured prompt templates with best-practice framing.
  2. LLM-refined (optional, requires Ollama) — uses a local model to further
     polish the structured prompt.
"""

import re
import logging

logger = logging.getLogger("koda")

# ============================================================
# INTENT DETECTION
# ============================================================

# Keywords that signal each category.
# Checked in priority order — more specific intents first, broad "code" last.
_INTENT_PATTERNS = [
    ("debug", [
        r"\b(debug|fix(?:ing)?|error|bug|crash\w*|broken|not working|issue|traceback|exception)\b",
        r"\b(fails?|failing|broke|doesn't work|won't work|can't get|slow)\b",
        r"\breturns? (undefined|null|none|wrong|unexpected|nothing|empty)\b",
        r"\b(why is .* (slow|failing|broken|wrong))",
        r"\b(instead of|expected .* (but|got))\b",
    ]),
    ("explain", [
        r"\b(explain|what is|what are|how does|how do|why does|why do|tell me about)\b",
        r"\b(difference between|compare|understand|meaning|concept|definition)\b",
        r"\bhow .* works?\b",
    ]),
    ("review", [
        r"\b(review|evaluate|assess|audit|improve|optimize|refactor)\b",
        r"\b(code review|pull request|pr\b|feedback on|look at .* code|check .* (code|for))",
    ]),
    ("write", [
        r"\b(draft|compose|email|message|letter|document|blog|article|post)\b",
        r"\b(rewrite|rephrase|summarize|summary|translate)\b",
        r"\bwrite .* (email|message|letter|document|blog|article)\b",
    ]),
    ("code", [
        r"\b(create|build|code|script|function|class|program|implement|develop)\b",
        r"\bwrite .* (code|script|function|class|program|app|component|module)\b",
        r"\b(algorithm|data structure|regex|query|sql|database)\b",
        r"\b(python|javascript|typescript|java|rust|go|html|css|react|api|endpoint)\b",
    ]),
]


def detect_intent(text):
    """Detect the user's intent from their speech.

    Returns one of: 'debug', 'code', 'explain', 'review', 'write', 'general'.
    """
    lower = text.lower()
    for intent, patterns in _INTENT_PATTERNS:
        for pattern in patterns:
            if re.search(pattern, lower):
                return intent
    return "general"


# ============================================================
# CONTEXT EXTRACTION
# ============================================================

def _extract_language(text):
    """Try to detect a programming language from the speech."""
    lang_map = {
        r"\bpython\b": "Python",
        r"\bjavascript\b": "JavaScript",
        r"\btypescript\b": "TypeScript",
        r"\bjava\b": "Java",
        r"\bc\+\+\b": "C++",
        r"\bc sharp\b|c#": "C#",
        r"\brust\b": "Rust",
        r"\bgo\b(?:lang)?\b": "Go",
        r"\bruby\b": "Ruby",
        r"\bphp\b": "PHP",
        r"\bswift\b": "Swift",
        r"\bsql\b": "SQL",
        r"\bhtml\b": "HTML/CSS",
        r"\breact\b": "React",
        r"\bnode\b": "Node.js",
    }
    lower = text.lower()
    for pattern, name in lang_map.items():
        if re.search(pattern, lower):
            return name
    return None


def _clean_for_prompt(text):
    """Light cleanup of speech for embedding in a prompt."""
    # Remove leading filler
    text = re.sub(r"^(okay|ok|so|um|uh|well|like|basically|alright|hey|hi)\s*,?\s*",
                  "", text, flags=re.IGNORECASE)
    # Remove trailing filler
    text = re.sub(r"\s*(please|thanks|thank you|if you can|if possible)\s*\.?\s*$",
                  "", text, flags=re.IGNORECASE)
    # Collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()
    # Ensure it ends with punctuation
    if text and text[-1] not in ".!?":
        text += "."
    return text


# ============================================================
# PROMPT TEMPLATES
# ============================================================

def _template_code(cleaned, language):
    """Structure a code request into a clear prompt."""
    lang_line = f"\n\nLanguage: {language}" if language else ""
    return (
        f"{cleaned}{lang_line}\n\n"
        "Requirements:\n"
        "- Write complete, working code\n"
        "- Include brief comments for clarity\n"
        "- Handle edge cases\n"
        "- Follow best practices and conventions"
    )


def _template_debug(cleaned, language):
    """Structure a debug request into a clear prompt."""
    lang_line = f"\n\nLanguage/stack: {language}" if language else ""
    return (
        f"I need help debugging an issue.\n\n"
        f"Problem: {cleaned}{lang_line}\n\n"
        "Please:\n"
        "1. Identify the likely root cause\n"
        "2. Explain why it's happening\n"
        "3. Provide the fix with code\n"
        "4. Suggest how to prevent it in the future"
    )


def _template_explain(cleaned, language):
    """Structure an explanation request."""
    return (
        f"{cleaned}\n\n"
        "Please explain:\n"
        "- What it is and why it matters\n"
        "- How it works (with examples)\n"
        "- Common pitfalls or misconceptions\n"
        "- When to use it vs alternatives"
    )


def _template_review(cleaned, language):
    """Structure a code review request."""
    lang_line = f"\n\nLanguage: {language}" if language else ""
    return (
        f"{cleaned}{lang_line}\n\n"
        "Review for:\n"
        "- Bugs or logic errors\n"
        "- Security vulnerabilities\n"
        "- Performance issues\n"
        "- Code clarity and maintainability\n"
        "- Best practice violations\n\n"
        "Prioritize findings by severity."
    )


def _template_write(cleaned, language):
    """Structure a writing/drafting request."""
    return (
        f"{cleaned}\n\n"
        "Guidelines:\n"
        "- Match the appropriate tone and formality\n"
        "- Be clear and concise\n"
        "- Structure with logical flow\n"
        "- Proofread for grammar and clarity"
    )


def _template_general(cleaned, language):
    """Structure a general request with good prompt practices."""
    return (
        f"{cleaned}\n\n"
        "Please be specific and thorough in your response. "
        "If you need clarification on anything, ask before proceeding."
    )


_TEMPLATES = {
    "code": _template_code,
    "debug": _template_debug,
    "explain": _template_explain,
    "review": _template_review,
    "write": _template_write,
    "general": _template_general,
}


# ============================================================
# LLM REFINEMENT (optional)
# ============================================================

_REFINE_SYSTEM_PROMPT = (
    "You are a prompt engineering expert. The user dictated a request by voice "
    "and it has been lightly structured. Your job is to refine it into an "
    "excellent prompt that will get the best response from an AI assistant.\n\n"
    "Rules:\n"
    "- Keep the user's original intent exactly\n"
    "- Add clarity and structure where helpful\n"
    "- Don't add requirements the user didn't ask for\n"
    "- Don't be verbose — clear and concise wins\n"
    "- Output ONLY the refined prompt, nothing else\n"
    "- Don't wrap in quotes or add meta-commentary"
)


def _llm_refine(structured_prompt, config):
    """Use a local LLM to further refine the structured prompt."""
    try:
        import ollama
        llm_model = config.get("prompt_assist", {}).get("model",
                    config.get("llm_polish", {}).get("model", "phi3:mini"))
        response = ollama.chat(
            model=llm_model,
            messages=[
                {"role": "system", "content": _REFINE_SYSTEM_PROMPT},
                {"role": "user", "content": structured_prompt},
            ],
        )
        result = response["message"]["content"].strip()
        return result if result else structured_prompt
    except Exception as e:
        logger.warning("Prompt assist LLM refinement failed: %s", e)
        return structured_prompt


# ============================================================
# MAIN ENTRY POINT
# ============================================================

def refine_prompt(raw_speech, config):
    """Transform raw speech into a well-structured LLM prompt.

    Args:
        raw_speech: The raw transcribed text from Whisper.
        config: Koda config dict.

    Returns:
        A refined, structured prompt string ready to paste into an LLM.
    """
    if not raw_speech or not raw_speech.strip():
        return raw_speech

    # Step 1: Light cleanup
    cleaned = _clean_for_prompt(raw_speech)
    if not cleaned:
        return raw_speech

    # Step 2: Detect intent
    intent = detect_intent(raw_speech)  # use raw speech for better detection
    language = _extract_language(raw_speech)

    logger.debug("Prompt assist: intent=%s, language=%s", intent, language)

    # Step 3: Apply template
    template_fn = _TEMPLATES.get(intent, _template_general)
    structured = template_fn(cleaned, language)

    # Step 4: Optional LLM refinement
    pa_config = config.get("prompt_assist", {})
    if pa_config.get("llm_refine", False):
        structured = _llm_refine(structured, config)

    logger.debug("Prompt assist output: %r", structured[:200])
    return structured
