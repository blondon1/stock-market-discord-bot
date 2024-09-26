from googletrans import Translator

translator = Translator()

def translate_to_spanish(text):
    try:
        translated = translator.translate(text, dest='es')
        return translated.text
    except Exception as e:
        print(f"Translation error: {e}")
        return text
