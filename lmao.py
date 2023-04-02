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

def multiplier(nps, lower_bound=1, upper_bound=2, lower_clamp=7, upper_clamp=13):
    def smoothstep(x):
        return x * x * (3 - 2 * x)

    t = (nps - lower_clamp) / (upper_clamp - lower_clamp)
    t = np.clip(t, 0, 1)
    return lower_bound + (upper_bound - lower_bound) * smoothstep(t)



import matplotlib.pyplot as plt

nps_values = np.linspace(1, 30, 1000)  # Generate 1000 equally spaced NPS values between 1 and 30
multiplier_values = [multiplier(nps) for nps in nps_values]

plt.plot(nps_values, multiplier_values)
plt.xlabel('Note Speed (NPS)')
plt.ylabel('Multiplier')
plt.title('Multiplier vs Note Speed (NPS)')
plt.grid()
plt.show()