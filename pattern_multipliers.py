# import numpy as np
# import matplotlib.pyplot as plt
# from typing import Tuple

# def ease_in_out(current_time, start_value, change_in_value, duration):
#     current_time /= duration / 2
#     if current_time < 1:
#         return change_in_value / 2 * current_time * current_time + start_value
#     current_time -= 1
#     return -change_in_value / 2 * (current_time * (current_time - 2) - 1) + start_value

# def ease_out(current_time, start_value, change_in_value, duration):
#     current_time /= duration
#     return -change_in_value * current_time * (current_time - 2) + start_value

# def ease_in_cubic(current_time, start_value, change_in_value, duration):
#     current_time /= duration
#     return change_in_value * current_time * current_time * current_time + start_value

# def ease_in_out(current_time, start_value, change_in_value, duration):
#     current_time /= duration / 2
#     if current_time < 1:
#         return change_in_value / 2 * current_time * current_time + start_value
#     current_time -= 1
#     return -change_in_value / 2 * (current_time * (current_time - 2) - 1) + start_value

# duration = 20
# x = np.linspace(0, duration, 1000)
# y = [ease_in_out(t, 1, 1, duration) for t in x]

# fig, ax = plt.subplots()
# ax.plot(x, y)
# ax.set_title('Ease In Ease Out')
# plt.show()


# duration = 20
# x = np.linspace(0, duration, 1000)
# y = [ease_out(t, 1, 1, duration) for t in x]

# fig, ax = plt.subplots()
# ax.plot(x, y)
# ax.set_title('Ease Out')
# plt.show()


# duration = 20
# x = np.linspace(0, duration, 1000)
# y = [ease_in_cubic(t, 1, 1, duration) for t in x]

# fig, ax = plt.subplots()
# ax.plot(x, y)
# ax.set_title('Ease In Cubic')
# plt.show()

import numpy as np

def nothing_but_theory_multiplier(nps, lower_bound=1, upper_bound=2, lower_clamp=2.5, upper_clamp=21.5):
    # 1.3 ~ 6.7 | 1.5 ~ 12
    def smoothstep(x):
        return x * x * (3 - (2 * x))

    t = (nps - lower_clamp) / (upper_clamp - lower_clamp)
    t = np.clip(t, 0, 1)
    return lower_bound + (upper_bound - lower_bound) * smoothstep(t)

def varying_streams(nps, lower_bound=1, upper_bound=2, lower_clamp=2.5, upper_clamp=20.5):
    def smoothstep(x):
        return x * x * (3 - (2 * x))

    t = (nps - lower_clamp) / (upper_clamp - lower_clamp)
    t = np.clip(t, 0, 1)
    return lower_bound + (upper_bound - lower_bound) * smoothstep(t)

def zig_zag_multiplier(nps, lower_bound=1, upper_bound=2, lower_clamp=6, upper_clamp=18):
    def ease_in_cubic(x):
        return x**4

    t = (nps - lower_clamp) / (upper_clamp - lower_clamp)
    t = np.clip(t, 0, 1)
    return lower_bound + (upper_bound - lower_bound) * ease_in_cubic(t)

def even_circle_multiplier(nps, lower_bound=1, upper_bound=1.55):
    def ease_in_out(x):
        return 3*x**2 - 2*x**3

    t = np.clip(nps / 30, 0, 1)
    return lower_bound + (upper_bound - lower_bound) * ease_in_out(t)

def skewed_circle_multiplier(nps, lower_bound=1, upper_bound=1.75):
    def ease_in_out(x):
        return 3*x**2 - 2*x**3

    t = np.clip(nps / 30, 0, 1)
    return lower_bound + (upper_bound - lower_bound) * ease_in_out(t)


def stream_multiplier(nps, lower_bound=1, upper_bound=1.3, lower_clamp=6.5, upper_clamp=12):
    def smoothstep(x):
        return x * x * (3 - (2 * x))

    t = (nps - lower_clamp) / (upper_clamp - lower_clamp)
    t = np.clip(t, 0, 1)
    return lower_bound + (upper_bound - lower_bound) * smoothstep(t)


def variable_stream_length_multiplier(num_notes, lower_bound=1.1, upper_bound=1.2, lower_clamp=6.5, upper_clamp=12):
    def smoothstep(x):
        return x * x * (3 - (2 * x))

    t = (num_notes - lower_clamp) / (upper_clamp - lower_clamp)
    t = np.clip(t, 0, 1)
    return lower_bound + (upper_bound - lower_bound) * smoothstep(t)

def zig_zag_length_multiplier(num_notes, lower_bound=1.0, upper_bound=1.2, lower_clamp=10, upper_clamp=30):
    def smoothstep(x):
        return x * x * (3 - (2 * x))

    t = (num_notes - lower_clamp) / (upper_clamp - lower_clamp)
    t = np.clip(t, 0, 1)
    return lower_bound + (upper_bound - lower_bound) * smoothstep(t)

if __name__ == "__main__":

    print(nothing_but_theory_multiplier(12))


    import matplotlib.pyplot as plt

    nps_values = np.linspace(1, 30, 1000)  # Generate 1000 equally spaced NPS values between 1 and 30
    
    even_circle = [even_circle_multiplier(nps) for nps in nps_values]

    skewed_values = [skewed_circle_multiplier(nps) for nps in nps_values]

    zig_zag_values = [zig_zag_multiplier(nps) for nps in nps_values]

    nbt_values = [nothing_but_theory_multiplier(nps) for nps in nps_values]
    stream_values = [stream_multiplier(nps) for nps in nps_values]
    variable_stream_values = [variable_stream_length_multiplier(nps) for nps in nps_values]

    zig_zag_length_values = [zig_zag_length_multiplier(nps) for nps in nps_values]


    plt.plot(nps_values, even_circle, label='Even Circle')
    plt.plot(nps_values, skewed_values, label='Skewed Circle')
    plt.plot(nps_values, zig_zag_values, label='Zig Zag')
    plt.plot(nps_values, nbt_values, label='Nothing but Theory')
    plt.plot(nps_values, stream_values, label='Single Streams')
    plt.plot(nps_values, variable_stream_values, label='Variable Stream (Multiplier for Num notes)')
    plt.plot(nps_values, zig_zag_length_values, label='Zig Zag (Multiplier for Num notes)')

    plt.xlabel('Note Speed (NPS)')
    plt.ylabel('Multiplier')
    plt.title('Multiplier vs Note Speed (NPS)')
    plt.grid()
    plt.legend()  # add a legend to the plot
    plt.show()