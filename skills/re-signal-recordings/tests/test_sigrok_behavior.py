"""Behavioral tests for sigrok session reading and UART decode."""
import io
import os
import sys
import unittest
import zipfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import sigrok

SAMPLE_RATE = 1_000_000
BAUD = 9600


def _uart_bits(data_bytes, samples_per_bit):
    bits = [1] * 20  # idle
    for value in data_bytes:
        bits += [0] * samples_per_bit  # start
        for bit in range(8):
            bits += [(value >> bit) & 1] * samples_per_bit
        bits += [1] * samples_per_bit  # stop
        bits += [1] * 10
    return bits


def build_sr():
    spb = round(SAMPLE_RATE / BAUD)
    bits = _uart_bits([0x41], spb)  # 'A'
    logic = bytes(bits)
    metadata = (
        "[device 1]\n"
        "samplerate=1 MHz\n"
        "total probes=8\n"
        "probe1=TX\n"
        "probe2=RX\n"
        "unitsize=1\n"
    )
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("metadata", metadata)
        archive.writestr("version", "2")
        archive.writestr("logic-1-1", logic)
    return buffer.getvalue()


class SigrokBehaviorTests(unittest.TestCase):
    def test_session_metadata_and_samples(self):
        session = sigrok.parse_sr(build_sr())
        self.assertEqual(session["samplerate_hz"], 1_000_000)
        self.assertEqual(session["probes"], {1: "TX", 2: "RX"})
        self.assertEqual(session["samples"], len(session["logic"]))

    def test_edges_found(self):
        session = sigrok.parse_sr(build_sr())
        transitions = sigrok.edges(sigrok.channel_samples(session, 1))
        self.assertGreaterEqual(len(transitions), 4)
        self.assertEqual(transitions[0]["direction"], "falling")

    def test_uart_decodes_a(self):
        session = sigrok.parse_sr(build_sr())
        result = sigrok.decode_uart(session, 1, BAUD)
        self.assertEqual(result["bytes"], [0x41])
        self.assertEqual(result["text"], "A")


if __name__ == "__main__":
    unittest.main()
