import numpy as np

from config.config import get_config

conf = get_config()


def nothing_but_theory_multiplier(
    nps,
    lower_bound=conf["nothing_but_theory_low_bound"],
    upper_bound=conf["nothing_but_theory_up_bound"],
    lower_clamp=conf["nothing_but_theory_low_clamp"],
    upper_clamp=conf["nothing_but_theory_up_clamp"],
):
    # 1.3 ~ 6.7 | 1.5 ~ 12
    def smoothstep(x):
        return x * x * (3 - (2 * x))

    t = (nps - lower_clamp) / (upper_clamp - lower_clamp)
    t = max(min(t, 1), 0)
    return lower_bound + (upper_bound - lower_bound) * smoothstep(t)


def varying_streams(
    nps,
    lower_bound=conf["varying_streams_low_bound"],
    upper_bound=conf["varying_streams_up_bound"],
    lower_clamp=conf["varying_streams_low_clamp"],
    upper_clamp=conf["varying_streams_up_clamp"],
):
    def smoothstep(x):
        return x * x * (3 - (2 * x))

    t = (nps - lower_clamp) / (upper_clamp - lower_clamp)
    t = max(min(t, 1), 0)
    return lower_bound + (upper_bound - lower_bound) * smoothstep(t)


def zig_zag_multiplier(
    nps,
    lower_bound=conf["zig_zag_low_bound"],
    upper_bound=conf["zig_zag_up_bound"],
    lower_clamp=conf["zig_zag_low_clamp"],
    upper_clamp=conf["zig_zag_up_clamp"],
):
    def ease_in_cubic(x):
        return x**4

    t = (nps - lower_clamp) / (upper_clamp - lower_clamp)
    t = max(min(t, 1), 0)
    return lower_bound + (upper_bound - lower_bound) * ease_in_cubic(t)


def even_circle_multiplier(
    nps,
    lower_bound=conf["even_circle_low_bound"],
    upper_bound=conf["even_circle_up_bound"],
):
    def ease_in_out(x):
        return 3 * x**2 - 2 * x**3

    t = np.clip(nps / 30, 0, 1)
    return lower_bound + (upper_bound - lower_bound) * ease_in_out(t)


def skewed_circle_multiplier(
    nps,
    lower_bound=conf["skewed_circle_low_bound"],
    upper_bound=conf["skewed_circle_up_bound"],
):
    def ease_in_out(x):
        return 3 * x**2 - 2 * x**3

    t = np.clip(nps / 30, 0, 1)
    return lower_bound + (upper_bound - lower_bound) * ease_in_out(t)


def stream_multiplier(
    nps,
    lower_bound=conf["stream_low_bound"],
    upper_bound=conf["stream_up_bound"],
    lower_clamp=conf["stream_low_clamp"],
    upper_clamp=conf["stream_up_clamp"],
):
    def smoothstep(x):
        return x * x * (3 - (2 * x))

    t = (nps - lower_clamp) / (upper_clamp - lower_clamp)
    t = max(min(t, 1), 0)
    return lower_bound + (upper_bound - lower_bound) * smoothstep(t)


def pattern_stream_length_multiplier(
    num_notes,
    lower_bound=conf["pattern_stream_length_low_bound"],
    upper_bound=conf["pattern_stream_length_up_bound"],
    lower_clamp=conf["pattern_stream_length_low_clamp"],
    upper_clamp=conf["pattern_stream_length_up_clamp"],
):
    def smoothstep(x):
        return x * x * (3 - (2 * x))

    t = (num_notes - lower_clamp) / (upper_clamp - lower_clamp)
    t = max(min(t, 1), 0)
    return lower_bound + (upper_bound - lower_bound) * smoothstep(t)


def zig_zag_length_multiplier(
    num_notes,
    lower_bound=conf["zig_zag_length_low_bound"],
    upper_bound=conf["zig_zag_length_up_bound"],
    lower_clamp=conf["zig_zag_length_low_clamp"],
    upper_clamp=conf["zig_zag_length_up_clamp"],
):
    def smoothstep(x):
        return x * x * (3 - (2 * x))

    t = (num_notes - lower_clamp) / (upper_clamp - lower_clamp)
    t = max(min(t, 1), 0)
    return lower_bound + (upper_bound - lower_bound) * smoothstep(t)


def four_stack_multiplier(
    nps,
    lower_bound=conf["four_stack_low_bound"],
    upper_bound=conf["four_stack_up_bound"],
    lower_clamp=conf["four_stack_low_clamp"],
    upper_clamp=conf["four_stack_up_clamp"],
):
    def smoothstep(x):
        return x * x * (3 - (2 * x))

    t = (nps - lower_clamp) / (upper_clamp - lower_clamp)
    t = max(min(t, 1), 0)
    return lower_bound + (upper_bound - lower_bound) * smoothstep(t)


def three_stack_multiplier(
    nps,
    lower_bound=conf["three_stack_low_bound"],
    upper_bound=conf["three_stack_up_bound"],
    lower_clamp=conf["three_stack_low_clamp"],
    upper_clamp=conf["three_stack_up_clamp"],
):
    def smoothstep(x):
        return x * x * (3 - (2 * x))

    t = (nps - lower_clamp) / (upper_clamp - lower_clamp)
    t = max(min(t, 1), 0)
    return lower_bound + (upper_bound - lower_bound) * smoothstep(t)


def two_stack_multiplier(
    nps,
    lower_bound=conf["two_stack_low_bound"],
    upper_bound=conf["two_stack_up_bound"],
    lower_clamp=conf["two_stack_low_clamp"],
    upper_clamp=conf["two_stack_up_clamp"],
):
    def smoothstep(x):
        return x * x * (3 - 2 * x)

    t = (nps - lower_clamp) / (upper_clamp - lower_clamp)
    t = max(min(t, 1), 0)
    return lower_bound + (upper_bound - lower_bound) * smoothstep(t)


def varying_stacks_multiplier(
    nps,
    lower_bound=conf["varying_stacks_low_bound"],
    upper_bound=conf["varying_stacks_up_bound"],
    lower_clamp=conf["varying_stacks_low_clamp"],
    upper_clamp=conf["varying_stacks_up_clamp"],
):
    def smoothstep(x):
        return x * x * (3 - (2 * x))

    t = (nps - lower_clamp) / (upper_clamp - lower_clamp)
    t = max(min(t, 1), 0)
    return lower_bound + (upper_bound - lower_bound) * smoothstep(t)


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    nps_values = np.linspace(
        1, 30, 1000
    )  # Generate 1000 equally spaced NPS values between 1 and 30

    even_circle = [even_circle_multiplier(nps) for nps in nps_values]

    skewed_values = [skewed_circle_multiplier(nps) for nps in nps_values]

    zig_zag_values = [zig_zag_multiplier(nps) for nps in nps_values]

    nbt_values = [nothing_but_theory_multiplier(nps) for nps in nps_values]
    stream_values = [stream_multiplier(nps) for nps in nps_values]
    pattern_stream_values = [pattern_stream_length_multiplier(nps) for nps in nps_values]

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
    plt.plot(nps_values, zig_zag_length_values, label="Zig Zag (Multiplier for Num notes)")

    plt.xlabel("Note Speed (NPS)")
    plt.ylabel("Multiplier")
    plt.title("Multiplier vs Note Speed (NPS)")
    plt.grid()
    plt.legend()  # add a legend to the plot
    plt.show()
