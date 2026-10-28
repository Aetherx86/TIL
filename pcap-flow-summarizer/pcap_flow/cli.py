import argparse
from .parser import FlowSummarizer

def main():
    parser = argparse.ArgumentParser(prog="pcap-flow")
    parser.add_argument("pcap_file", help="Path to pcap file")
    args = parser.parse_args()
    flows = FlowSummarizer.summarize(args.pcap_file)
    print(f"{'Endpoint A':<25} {'Endpoint B':<25} {'Proto':<8} {'Packets':<10} {'Bytes':<10}")
    print("-" * 80)
    for (src_ip, dst_ip, src_p, dst_p, proto), st in flows.items():
        ep_a = f"{src_ip}:{src_p}"
        ep_b = f"{dst_ip}:{dst_p}"
        print(f"{ep_a:<25} {ep_b:<25} {proto:<8} {st.packet_count:<10} {st.total_bytes:<10}")

if __name__ == "__main__":
    main()
