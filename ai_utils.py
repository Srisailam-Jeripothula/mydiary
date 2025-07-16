from transformers import pipeline

rewriter_pipe = pipeline(
    "text2text-generation",
    model="pszemraj/flan-t5-large-grammar-synthesis"
)

def polish_text(text):
    """
    One simple pass: grammar, spelling, punctuation, style.
    """

    result = rewriter_pipe(
        text,               # 👉 ONLY the raw text!
        max_length=150,
        num_beams=5,
        early_stopping=True
    )[0]['generated_text']

    return result
