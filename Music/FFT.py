import numpy as np
import pickle
from scipy.io import wavfile

chunk_size = 4096


def CooleyTukey(x: list, num=chunk_size, interval=1):
    out = list()
    if num == 1:
        out = [x[0]]
    else:
        out[:int(num/2)] = CooleyTukey(x, int(num/2), 2 * interval)
        out[int(num/2):] = CooleyTukey(x[interval:], int(num/2), 2 * interval)
        for i in range(0, int(num/2)):
            temp = out[i]
            out[i] = temp + np.power(np.e, (-2 * np.pi * 1j * i)/num) * out[i + int(num/2)]
            out[i + int(num/2)] = temp - np.power(np.e, (-2 * np.pi * 1j * i)/num) * out[i + int(num/2)]
    return out


def read(wav_name):
    return np.asarray(wavfile.read(wav_name)[1])


def prepare(input_file):
    return split(stereo_to_mono(input_file))


def stereo_to_mono(input_file):
    return np.sum(input_file, axis=1)


def split(input_file):
    return np.reshape(input_file[:-(len(input_file) % chunk_size)], (-1, chunk_size))


def save_signatures(s):
    file = open('signatures.pkl', 'wb+')
    pickle.dump(s, file)


def load_signatures():
    try:
        file = open('signatures.pkl', 'rb')
    except FileNotFoundError:
        return dict()
    return pickle.load(file)


def index_song(filepath, song):
    audio = read(filepath)
    signed_audio = sign_audio(audio)
    for signature in signed_audio:
        add_signature(signature, song)


def sign_audio(audio):
    audio = prepare(audio)
    return [sign_chunk(chunk) for chunk in audio]


def sign_chunk(chunk):
    freqs = (30, 40, 80, 120, 180, 300)
    dft = [abs(j) for j in np.fft.fft(chunk)]
    index = list()
    for i in range(0, len(freqs)-1):
        index.append(np.argmax(dft[freqs[i]: freqs[i+1]]))
    return index


def add_signature(signature, song):
    signatures = loaded_signatures
    signatures.setdefault(str(signature), set()).add(song)
    # save_signatures(signatures)


def get_matches(audio):
    signatures = sign_audio(audio)
    matches = list()
    for signature in signatures:
        for match in get_signature_matches(signature):
            matches.append(match)
    return matches


def get_signature_matches(signature):
    signatures = loaded_signatures
    if str(signature) in signatures:
        return signatures[str(signature)]
    return ""


if __name__ == "__main__":
    # index_song("The Weeknd - Often.wav", "The Weeknd - Often")
    # print(get_matches(read("The Weeknd - Often.wav")))
    # import os
    loaded_signatures = load_signatures()
    # files = [f for f in os.listdir('/media/shrub/Secondary Hard Drive/Storage/Music/wavs') if os.path.isfile(os.path.j
    # oin('/media/shrub/Secondary Hard Drive/Storage/Music/wavs', f))]
    # for song in files:
    #     print(song[0:-4])
    #     index_song('/media/shrub/Secondary Hard Drive/Storage/Music/wavs/' + song, song[0:-4])
    # save_signatures(loaded_signatures)
    matched = get_matches(read("/media/shrub/Secondary Hard Drive/Storage/Music/wavs/04 - SAD!.wav"))
    print(max(set(matched), key=matched.count))



