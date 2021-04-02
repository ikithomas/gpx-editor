import numpy as np
import random


# general a large array of target to be consumed
def random_target_speeds(n, base=10, width_scale=1, height_scale=1):
    results = [base] * n

    # smallest flustration
    results = map(
        lambda x, y: x + y,
        results,
        flustrate(n, int(n/100 * width_scale), 0.1 * height_scale, 1000)
    )

    # medium flustration
    results = map(
        lambda x, y: x + y,
        results,
        flustrate(n, int(n/20 * width_scale), 0.15 * height_scale, 100)
    )

    # high flustration
    results = map(
        lambda x, y: x + y,
        results,
        flustrate(n, int(n/5 * width_scale), 0.2 * height_scale, 10)
    )

    return list(results)


def flustrate(n, w, h, t):
    results = [0] * n

    # upward wave
    for i in range(t):
        position = random.randint(0, n - w)
        wave = upward_wave(w, h)
        for j in range(len(wave)):
            results[position + j] += wave[j]

    # downward wave
    for i in range(t):
        position = random.randint(0, n - w)
        wave = downward_wave(w, h)
        for j in range(len(wave)):
            results[position + j] += wave[j]

    return results

# produce an upward wave wi
def upward_wave(w, h):
    x = np.linspace(0, np.pi, w)
    return np.sin(x) * h

def downward_wave(w, h):
    x = np.linspace(np.pi, np.pi *2, w)
    return np.sin(x) * h
