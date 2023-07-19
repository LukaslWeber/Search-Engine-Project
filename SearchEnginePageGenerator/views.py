import os
from django.shortcuts import render
from django.http import HttpResponse
# from tensorflow_tts.inference import TFAutoModel, AutoConfig, AutoTokenizer
# import tensorflow as tf
import speech_recognition as sr
from gtts import gTTS

#from Ranker import Ranker
#TODO
# path = 'data_files'
# index = os.path.join(path, 'forward_index.joblib')
# index_inverted = os.path.join(path, 'inverted_index.joblib')
# index_embedding = os.path.join(path, 'embedding_index.joblib')
# ranker = Ranker(index, index_inverted, index_embedding)

# # Instantiate the Tacotron 2 model
# tacotron2_config = AutoConfig.from_pretrained("tensorspeech/tts-tacotron2-ljspeech-en")
# tacotron2 = TFAutoModel.from_pretrained("tensorspeech/tts-tacotron2-ljspeech-en", config=tacotron2_config)


# Create your views here.
def open_mainview(request):
    context = {'name': 'Lukas'}
    return render(request, 'mainview.html', context)


def search(request):
    query = str(request.GET.get('queryField'))
    print(f"Query is: {query}")

    # Check if the current query matches the stored query in the session
    stored_query = request.session.get('query', '')
    if query != stored_query:
        # The query has changed, so remove the stored search results from the session
        request.session.pop('search_results', None)

    #Check if results are already stored in the session
    if 'search_results' not in request.session:
        print("Generating results")
        # TODO: results = ranker.rank(query, )
        results = [("https://theuselessweb.com/", "result 1 website text"),
                   ("https://theuselessweb.com/", "result 2 website text"),
                   ("https://theuselessweb.com/", "result 3 website text"),
                   ("https://theuselessweb.com/", "result 4 website text"),
                   ("https://theuselessweb.com/", "result 5 website text"),
                   ("https://theuselessweb.com/", "result 6 website text"),
                   ("https://theuselessweb.com/", "result 7 website text"),
                   ("https://theuselessweb.com/", "result 8 website text"),
                   ("https://theuselessweb.com/", "result 9 website text"),
                   ("https://theuselessweb.com/", "result 1 website text"),
                   ("https://theuselessweb.com/", "result 1 website text"),
                   ("https://theuselessweb.com/", "result 1 website text"),
                   ("https://theuselessweb.com/", "result 1 website text"),
                   ("https://theuselessweb.com/", "result 1 website text"),
                   ("https://theuselessweb.com/", "result 1 website text")]
        # Store search results and query in the session
        request.session['search_results'] = results
        request.session['query'] = query
    else:
        results = request.session['search_results']

    # Perform search operation based on the query
    results_per_page = 11
    start_index = int(request.GET.get('start_index', 0))
    previous_start_index = start_index - results_per_page
    limited_results = results[start_index: start_index + results_per_page]
    show_more = start_index + results_per_page < len(results)
    show_previous = start_index >= results_per_page
    remaining_elements = len(results) - (start_index + results_per_page)
    audio_files = []
    for i, result in enumerate(limited_results):
        website_text = result[1]
        tts = gTTS(text=website_text, lang="en")
        tts.save(os.path.join("data_files", f"{i}.mp3"))
    #     tokenizer = AutoTokenizer.from_pretrained("tensorspeech/tts-tacotron2-ljspeech-en")
    #     input_ids = tokenizer(website_text, return_tensors="tf")["input_ids"]
    #     audio = tacotron2.inference(input_ids, speed_ratios=[1.0])
    #     audio_path = os.path.join("data_files", f"audio_{i}.wav")
    #     tf.audio.write_wav(audio_path, audio[0], sample_rate=22050)
    #     audio_files.append(audio_path)


    if 'text_to_speech' in request.GET:
        # Get the index of the result to convert to speech
        result_index = int(request.GET['text_to_speech'])

        # Retrieve the website text
        website_text = results[result_index][1]

        # Instantiate the tokenizer
        tokenizer = AutoTokenizer.from_pretrained("tensorspeech/tts-tacotron2-ljspeech-en")

        # Tokenize the input text
        input_ids = tokenizer(website_text, return_tensors="tf")["input_ids"]

        # Perform text-to-speech synthesis
        mel_outputs, _, _ = tacotron2.inference(input_ids)
        audio = tacotron2.inference(input_ids, speed_ratios=[1.0])
        audio_path = "data_files/audio.wav"
        tf.audio.write_wav(audio_path, audio[0], sample_rate=22050)

        with open(audio_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='audio/wav')
            response['Content-Disposition'] = 'attachment; filename="audio.wav"'
            return response

    context = {
        'query': query,
        'search_results': limited_results,
        'start_index': start_index + results_per_page,
        'previous_start_index': previous_start_index,
        'show_more': show_more,
        'show_previous': show_previous,
        'remaining_elements': remaining_elements,
        'audio_files': audio_files
    }
    print(f"Full results are: ")
    print(results)
    print(context)
    return render(request, 'searchview.html', context)
