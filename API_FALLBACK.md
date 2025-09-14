# API FALLBACK SYSTEM

## Multiple API Support Added:

### Primary: Groq API
- Model: `llama-3.1-8b-instant`
- Free tier available
- Fast responses

### Fallback: OpenAI API  
- Model: `gpt-3.5-turbo`
- Reliable but paid
- Better Railway compatibility

## Environment Variables Needed:

```bash
GROQ_API_KEY=your_groq_key_here
OPENAI_API_KEY=your_openai_key_here  # Optional fallback
```

## How it works:
1. **Try Groq first** - If successful, use Groq
2. **If Groq fails** - Automatically try OpenAI
3. **If both fail** - Use hardcoded question bank

## To get OpenAI API key:
1. Go to https://platform.openai.com/api-keys
2. Create new API key
3. Add to Railway environment variables

This should resolve the connection issues!