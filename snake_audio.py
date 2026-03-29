import math
from array import array

import pygame


def make_tone(frequency, duration_ms, volume=0.25, sample_rate=22050):
    total_samples = int(sample_rate * (duration_ms / 1000))
    attack = max(1, int(total_samples * 0.12))
    release = max(1, int(total_samples * 0.22))
    samples = array("h")

    for index in range(total_samples):
        if index < attack:
            envelope = index / attack
        elif index > total_samples - release:
            envelope = max(0.0, (total_samples - index) / release)
        else:
            envelope = 1.0

        wave = (
            math.sin((2 * math.pi * frequency * index) / sample_rate)
            + 0.35 * math.sin((2 * math.pi * frequency * 2 * index) / sample_rate)
        )
        samples.append(int(32767 * volume * envelope * wave * 0.7))

    return pygame.mixer.Sound(buffer=samples.tobytes())


def make_music_loop(sample_rate=22050):
    notes = [
        (196.00, 320),
        (246.94, 320),
        (293.66, 640),
        (220.00, 320),
        (246.94, 320),
        (329.63, 640),
        (174.61, 320),
        (220.00, 320),
        (261.63, 640),
    ]
    samples = array("h")

    for frequency, duration_ms in notes:
        total_samples = int(sample_rate * (duration_ms / 1000))
        attack = max(1, int(total_samples * 0.18))
        release = max(1, int(total_samples * 0.28))

        for index in range(total_samples):
            if index < attack:
                envelope = index / attack
            elif index > total_samples - release:
                envelope = max(0.0, (total_samples - index) / release)
            else:
                envelope = 1.0

            t = index / sample_rate
            wave = (
                math.sin(2 * math.pi * frequency * t)
                + 0.45 * math.sin(2 * math.pi * (frequency / 2) * t)
                + 0.20 * math.sin(2 * math.pi * (frequency * 1.5) * t)
            ) / 1.65
            samples.append(int(32767 * 0.11 * envelope * wave))

    return pygame.mixer.Sound(buffer=samples.tobytes())


def setup_audio():
    audio = {"enabled": False}
    try:
        pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
        audio["enabled"] = True
        audio["turn"] = make_tone(420, 70, 0.10)
        audio["eat"] = make_tone(760, 140, 0.18)
        audio["crash"] = make_tone(140, 320, 0.20)
        audio["music"] = make_music_loop()
        audio["music_channel"] = pygame.mixer.Channel(0)
        audio["sfx_channel"] = pygame.mixer.Channel(1)
        audio["music_channel"].set_volume(0.38)
        audio["sfx_channel"].set_volume(0.65)
    except pygame.error:
        return audio

    return audio


def start_music(audio):
    if audio.get("enabled") and not audio["music_channel"].get_busy():
        audio["music_channel"].play(audio["music"], loops=-1)


def play_sound(audio, name):
    if audio.get("enabled"):
        audio["sfx_channel"].play(audio[name])
