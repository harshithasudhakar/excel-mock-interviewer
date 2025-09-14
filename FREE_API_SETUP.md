# FREE API FALLBACK SYSTEM

## Now Using FREE APIs Only:

### Primary: Groq API (FREE)
- Model: `llama-3.1-8b-instant`
- Free tier: 14,400 requests/day
- Fast responses

### Fallback: Hugging Face (FREE)
- Model: `microsoft/DialoGPT-medium`
- Completely free
- No rate limits

## Environment Variables:

```bash
GROQ_API_KEY=your_groq_key_here
HF_TOKEN=your_huggingface_token_here  # Optional, can work without
```

## To get FREE Hugging Face token:
1. Go to https://huggingface.co/settings/tokens
2. Create new token (free account)
3. Add as `HF_TOKEN` in Railway environment

## How it works:
1. **Try Groq first** - Primary free API
2. **If Groq fails** - Try Hugging Face (also free)
3. **If both fail** - Use hardcoded question bank

**Both APIs are completely FREE!** 🎉