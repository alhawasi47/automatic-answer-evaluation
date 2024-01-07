import requests

def ocr_space_text_extraction(filename, language='eng'):
    
    api_key = ''
    payload = {
        'apikey': api_key,
        'language': language,
        'OCREngine': '2',  # Use OCR engine that supports special characters
    }
    with open(filename, 'rb') as f:
        r = requests.post('https://api.ocr.space/parse/image',
                          files={filename: f},
                          data=payload)

    result = r.json()
    if result['IsErroredOnProcessing'] is False:
        parsed_text = result['ParsedResults'][0]['ParsedText']
        return parsed_text
    else:
        error_message = result['ErrorMessage']
        print(f"Error: {error_message}")
        return None


