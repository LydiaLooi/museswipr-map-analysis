import numpy as np


def nothing_but_theory_multiplier(
    nps, lower_bound=1, upper_bound=2, lower_clamp=2.5, upper_clamp=21.5
):
    # 1.3 ~ 6.7 | 1.5 ~ 12
    def smoothstep(x):
        return x * x * (3 - (2 * x))

    t = (nps - lower_clamp) / (upper_clamp - lower_clamp)
    t = np.clip(t, 0, 1)
    return lower_bound + (upper_bound - lower_bound) * smoothstep(t)


def varying_streams(
    nps, lower_bound=1, upper_bound=2, lower_clamp=2.5, upper_clamp=20.5
):
    def smoothstep(x):
        return x * x * (3 - (2 * x))

    t = (nps - lower_clamp) / (upper_clamp - lower_clamp)
    t = np.clip(t, 0, 1)
    return lower_bound + (upper_bound - lower_bound) * smoothstep(t)


def zig_zag_multiplier(
    nps, lower_bound=1, upper_bound=2, lower_clamp=6, upper_clamp=18
):
    def ease_in_cubic(x):
        return x**4

    t = (nps - lower_clamp) / (upper_clamp - lower_clamp)
    t = np.clip(t, 0, 1)
    return lower_bound + (upper_bound - lower_bound) * ease_in_cubic(t)


def even_circle_multiplier(nps, lower_bound=1, upper_bound=1.55):
    def ease_in_out(x):
        return 3 * x**2 - 2 * x**3

    t = np.clip(nps / 30, 0, 1)
    return lower_bound + (upper_bound - lower_bound) * ease_in_out(t)


def skewed_circle_multiplier(nps, lower_bound=1, upper_bound=1.75):
    def ease_in_out(x):
        return 3 * x**2 - 2 * x**3

    t = np.clip(nps / 30, 0, 1)
    return lower_bound + (upper_bound - lower_bound) * ease_in_out(t)


def stream_multiplier(
    nps, lower_bound=1, upper_bound=1.3, lower_clamp=6.5, upper_clamp=12
):
    def smoothstep(x):
        return x * x * (3 - (2 * x))

    t = (nps - lower_clamp) / (upper_clamp - lower_clamp)
    t = np.clip(t, 0, 1)
    return lower_bound + (upper_bound - lower_bound) * smoothstep(t)


def pattern_stream_length_multiplier(
    num_notes, lower_bound=1.1, upper_bound=1.2, lower_clamp=6.5, upper_clamp=12
):
    def smoothstep(x):
        return x * x * (3 - (2 * x))

    t = (num_notes - lower_clamp) / (upper_clamp - lower_clamp)
    t = np.clip(t, 0, 1)
    return lower_bound + (upper_bound - lower_bound) * smoothstep(t)


def zig_zag_length_multiplier(
    num_notes, lower_bound=1.0, upper_bound=1.2, lower_clamp=10, upper_clamp=30
):
    def smoothstep(x):
        return x * x * (3 - (2 * x))

    t = (num_notes - lower_clamp) / (upper_clamp - lower_clamp)
    t = np.clip(t, 0, 1)
    return lower_bound + (upper_bound - lower_bound) * smoothstep(t)


def four_stack_multiplier(
    nps, lower_bound=1.0, upper_bound=1.4, lower_clamp=6, upper_clamp=12
):
    def smoothstep(x):
        return x * x * (3 - (2 * x))

    t = (nps - lower_clamp) / (upper_clamp - lower_clamp)
    t = np.clip(t, 0, 1)
    return lower_bound + (upper_bound - lower_bound) * smoothstep(t)


def three_stack_multiplier(
    nps, lower_bound=1.0, upper_bound=1.25, lower_clamp=6, upper_clamp=12
):
    def smoothstep(x):
        return x * x * (3 - (2 * x))

    t = (nps - lower_clamp) / (upper_clamp - lower_clamp)
    t = np.clip(t, 0, 1)
    return lower_bound + (upper_bound - lower_bound) * smoothstep(t)


def two_stack_multiplier(
    nps, lower_bound=1.0, upper_bound=1.20, lower_clamp=6, upper_clamp=12
):
    def smoothstep(x):
        return x * x * (3 - (2 * x))

    t = (nps - lower_clamp) / (upper_clamp - lower_clamp)
    t = np.clip(t, 0, 1)
    return lower_bound + (upper_bound - lower_bound) * smoothstep(t)


def varying_stacks_multiplier(
    nps, lower_bound=1.0, upper_bound=1.35, lower_clamp=4, upper_clamp=14
):
    def smoothstep(x):
        return x * x * (3 - (2 * x))

    t = (nps - lower_clamp) / (upper_clamp - lower_clamp)
    t = np.clip(t, 0, 1)
    return lower_bound + (upper_bound - lower_bound) * smoothstep(t)


if __name__ == "__main__":
    print(nothing_but_theory_multiplier(12))

    import matplotlib.pyplot as plt

    nps_values = np.linspace(
        1, 30, 1000
    )  # Generate 1000 equally spaced NPS values between 1 and 30

    even_circle = [even_circle_multiplier(nps) for nps in nps_values]

    skewed_values = [skewed_circle_multiplier(nps) for nps in nps_values]

    zig_zag_values = [zig_zag_multiplier(nps) for nps in nps_values]

    nbt_values = [nothing_but_theory_multiplier(nps) for nps in nps_values]
    stream_values = [stream_multiplier(nps) for nps in nps_values]
    pattern_stream_values = [
        pattern_stream_length_multiplier(nps) for nps in nps_values
    ]

    zig_zag_length_values = [zig_zag_length_multiplier(nps) for nps in nps_values]

    four_stack_values = [four_stack_multiplier(nps) for nps in nps_values]
    three_stack_values = [three_stack_multiplier(nps) for nps in nps_values]
    two_stack_values = [two_stack_multiplier(nps) for nps in nps_values]
    varying_stacks_values = [varying_stacks_multiplier(nps) for nps in nps_values]

    plt.plot(nps_values, even_circle, label="Even Circle")
    plt.plot(nps_values, skewed_values, label="Skewed Circle")
    plt.plot(nps_values, zig_zag_values, label="Zig Zag")
    plt.plot(nps_values, nbt_values, label="Nothing but Theory")
    plt.plot(nps_values, stream_values, label="Single Streams")
    plt.plot(nps_values, varying_stacks_values, label="Varying Stacks)")

    plt.plot(nps_values, four_stack_values, label="Four Stacks)")
    plt.plot(nps_values, three_stack_values, label="Three Stacks)")
    plt.plot(nps_values, two_stack_values, label="Two Stacks)")

    plt.plot(
        nps_values,
        pattern_stream_values,
        label="Pattern Stream (Multiplier for Num notes)",
    )
    plt.plot(
        nps_values, zig_zag_length_values, label="Zig Zag (Multiplier for Num notes)"
    )

    plt.xlabel("Note Speed (NPS)")
    plt.ylabel("Multiplier")
    plt.title("Multiplier vs Note Speed (NPS)")
    plt.grid()
    plt.legend()  # add a legend to the plot
    plt.show()
