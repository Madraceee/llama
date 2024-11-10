from langdetect import detect
from transliterate import translit
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate as indic_translit
import unidecode
from pypinyin import lazy_pinyin

def detect_language(text):
    try:
        return detect(text)
    except:
        return None

def transliterate_text(text):
    """
    Transliterates text based on the detected language.
    """
    language = detect_language(text)
    # Cyrillic scripts
    if language in ['ru', 'uk', 'bg', 'sr', 'mk', 'ky', 'kk', 'uz']:
        return translit(text, 'ru', reversed=True)
    
    # Arabic script
    elif language in ['ar', 'fa', 'ur', 'ps']:
        transliteration_map = {
            # Basic letters
            'ا': 'ā', 'ب': 'b', 'ت': 't', 'ث': 'th',
            'ج': 'j', 'ح': 'ḥ', 'خ': 'kh', 'د': 'd',
            'ذ': 'dh', 'ر': 'r', 'ز': 'z', 'س': 's',
            'ش': 'sh', 'ص': 'ṣ', 'ض': 'ḍ', 'ط': 'ṭ',
            'ظ': 'ẓ', 'ع': 'ʿ', 'غ': 'gh', 'ف': 'f',
            'ق': 'q', 'ك': 'k', 'ل': 'l', 'م': 'm',
            'ن': 'n', 'ه': 'h', 'و': 'w', 'ي': 'y',
            
            # Vowel marks
            'َ': 'a', 'ِ': 'i', 'ُ': 'u',
            'ً': 'an', 'ٍ': 'in', 'ٌ': 'un',
            'ْ': '', 'ّ': '',  
            
            # Special combinations
            'آ': 'ʾā', 'ة': 'h', 'ى': 'á',
            'ئ': 'ʾ', 'ؤ': 'ʾ', 'إ': 'ʾi',
            'أ': 'ʾa',
            
            # Dialectal variations
            'چ': 'ch', 'پ': 'p', 'ڤ': 'v',
            'گ': 'g', 'ژ': 'zh'
        }
        
        transliterated_text = ''.join(transliteration_map.get(char, char) for char in text)
        return transliterated_text


    # Devanagari script
    elif language in ['hi', 'mr', 'ne', 'sd']:
        return indic_translit(text, sanscript.DEVANAGARI, sanscript.ITRANS)

    # Bengali script
    elif language == 'bn':
        return indic_translit(text, sanscript.BENGALI, sanscript.ITRANS)

    # Tamil script
    elif language == 'ta':
        consonants = {
            'க': 'ka', 'ங': 'nga', 'ச': 'cha', 'ஞ': 'nja',
            'ட': 'ta', 'ண': 'na', 'த': 'tha', 'ந': 'na',
            'ப': 'pa', 'ம': 'ma', 'ய': 'ya', 'ர': 'ra',
            'ல': 'la', 'வ': 'va', 'ழ': 'zha', 'ள': 'la',
            'ற': 'ra', 'ன': 'na'
        }

        consonant_vowel_markers = {
            'க': 'k', 'ங': 'ng', 'ச': 'ch', 'ஞ': 'nj',
            'ட': 't', 'ண': 'n', 'த': 'th', 'ந': 'n',
            'ப': 'p', 'ம': 'm', 'ய': 'y', 'ர': 'r',
            'ல': 'l', 'வ': 'v', 'ழ': 'zh', 'ள': 'l',
            'ற': 'tr', 'ன': 'n'
        }

        vowels = {
            'அ': 'a', 'ஆ': 'aa', 'இ': 'i', 'ஈ': 'ii',
            'உ': 'uu', 'ஊ': 'uu', 'எ': 'e', 'ஏ': 'e',
            'ஐ': 'ai', 'ஒ': 'o', 'ஓ': 'oo', 'ஔ': 'au'
        }

        vowel_markers = {
            'ா': 'a', 'ி': 'i', 'ீ': 'ii', 'ு': 'uu',
            'ூ': 'uu', 'ெ': 'e', 'ே': 'e', 'ை': 'ai',
            'ொ': 'o', 'ோ': 'o', 'ௌ': 'au', '்': ''
        }

        special = {
            'ஃ': 'kh',
        }

        transliterated_text = ""
        i = 0
        while i < len(text):
            char = text[i]
            # Check if the character is a consonant
            if char in consonants:
                # If the consonant is followed by a vowel marker
                if i + 1 < len(text) and text[i + 1] in vowel_markers:
                    # Use the consonant_vowel_markers dictionary
                    transliterated_text += consonant_vowel_markers[char]
                    # Add the corresponding vowel sound
                    transliterated_text += vowel_markers[text[i + 1]]
                    # Skip the vowel marker in the next iteration
                    i += 1
                else:
                    # Use the consonants dictionary if no vowel marker follows
                    transliterated_text += consonants[char]

            # Check if the character is a vowel
            elif char in vowels:
                transliterated_text += vowels[char]

            # Handle special characters
            elif char in special:
                transliterated_text += special[char]

            else:
                # If character is not in any dictionary, add it as-is
                transliterated_text += char

            i += 1

        return transliterated_text

    # Telugu script
    elif language == 'te':
        return indic_translit(text, sanscript.TELUGU, sanscript.ITRANS)

    # Kannada script
    elif language == 'kn':
        return indic_translit(text, sanscript.KANNADA, sanscript.ITRANS)

    # Malayalam script
    elif language == 'ml':
        return indic_translit(text, sanscript.MALAYALAM, sanscript.ITRANS)

    # Gujarati script
    elif language == 'gu':
        return indic_translit(text, sanscript.GUJARATI, sanscript.ITRANS)

    # Odia script
    elif language == 'or':
        return indic_translit(text, sanscript.ORIYA, sanscript.ITRANS)

    # Chinese script (Pinyin)
    elif language in ['zh-cn', 'zh-tw']:
        return ' '.join(lazy_pinyin(text))

    # Greek script
    elif language == 'el':
        return unidecode.unidecode(text)

    # Tibetan script
    elif language == 'bo':
        return unidecode.unidecode(text)

    # Georgian script
    elif language == 'ka':
        return unidecode.unidecode(text)

    # Fallback for other scripts
    return unidecode.unidecode(text)