"""Pin-guarded, opt-in PIF controller RESPONSE trace for RMG v0.9.0.

Observe game-visible Joybus read replies after netplay_update_input(), not
physical SDL edge timestamps and not guest consumer callback execution.
Independent input ring uses existing MKMSZR_TRACE=1 host observer header.
No game/ROM writes; no new guest PIF reads; no guest CP0 update.
"""
from pathlib import Path

PIF = Path("Source/3rdParty/mupen64plus-core/src/device/pif/pif.c")

INJECT = r"""
/* MKMSZR v05 read-only Joybus response sampling. The PIF request has
   already been processed by the stock controller backend + netplay path.
   All raw values come from the returned PIF 4-byte controller payload. */
static void mkmszr_input_observe_joybus(struct pif *pif)
{
    static int enabled = -1;
    size_t port;
    const char *env;
    if (enabled < 0) {
        env = getenv("MKMSZR_TRACE_INPUT");
        enabled = env != NULL && strcmp(env, "1") == 0 &&
                  getenv("MKMSZR_TRACE") != NULL &&
                  strcmp(getenv("MKMSZR_TRACE"), "1") == 0;
    }
    if (!enabled || pif == NULL || pif->ram == NULL ||
        pif->r4300 == NULL) return;
    for (port = 0; port < PIF_CHANNELS_COUNT; ++port) {
        const struct pif_channel *ch = &pif->channels[port];
        uintptr_t begin = (uintptr_t)pif->ram, end = begin + PIF_RAM_SIZE;
        uintptr_t tx, rx, payload, reply;
        uint32_t input, buttons, error;
        if (ch->tx == NULL || ch->rx == NULL ||
            ch->tx_buf == NULL || ch->rx_buf == NULL)
            continue;
        tx = (uintptr_t)ch->tx;
        rx = (uintptr_t)ch->rx;
        payload = (uintptr_t)ch->tx_buf;
        reply = (uintptr_t)ch->rx_buf;
        if (tx < begin || tx >= end || rx < begin || rx >= end ||
            payload < begin || payload >= end ||
            reply < begin || reply > end - 4u)
            continue;
        /* Controller-data request: exactly 1 Tx byte, 4 Rx bytes. */
        if ((*ch->tx & 0x3fu) != 1u ||
            (*ch->rx & 0x3fu) != 4u ||
            ch->tx_buf[0] != 0x01u)
            continue;
        input = (uint32_t)ch->rx_buf[0] |
            ((uint32_t)ch->rx_buf[1] << 8) |
            ((uint32_t)ch->rx_buf[2] << 16) |
            ((uint32_t)ch->rx_buf[3] << 24);
        buttons = input & 0xffffu;
        error = *ch->rx & 0xc0u;
        mkmszr_trace(0x60u,
            r4300_cp0_regs(&pif->r4300->cp0)[CP0_COUNT_REG],
            (uint32_t)port, input, buttons,
            (uint32_t)(int32_t)(int8_t)ch->rx_buf[2],
            (uint32_t)(int32_t)(int8_t)ch->rx_buf[3],
            error, (uint32_t)(*ch->tx & 0x3fu),
            (uint32_t)(*ch->rx & 0x3fu));
    }
}
"""


def replace_once(source: str, old: str, new: str) -> str:
    count = source.count(old)
    if count != 1:
        raise RuntimeError(
            f"RMG pinned source anchor missing/ambiguous ({count}): {old[:100]!r}"
        )
    return source.replace(old, new)


def apply(path: Path = PIF) -> None:
    source = path.read_text()
    if "mkmszr_input_observe_joybus" in source:
        raise RuntimeError("Joybus observer already installed")
    source = replace_once(
        source,
        '#include "device/r4300/r4300_core.h"\n',
        '#include "device/r4300/r4300_core.h"\n'
        '#define MKMSZR_TRACE_CAP 131072u\n'
        '#define MKMSZR_TRACE_CHANNEL "input"\n'
        '#include "mkmszr_trace.h"\n',
    )
    source = replace_once(
        source,
        'void update_pif_ram(struct pif* pif)\n',
        INJECT + '\nvoid update_pif_ram(struct pif* pif)\n',
    )
    source = replace_once(
        source,
        '    netplay_update_input(pif);\n',
        '    netplay_update_input(pif);\n'
        '    mkmszr_input_observe_joybus(pif);\n',
    )
    path.write_text(source)


if __name__ == "__main__":
    apply()
    print("Applied RMG v05 host-only controller/PIF response observer")
