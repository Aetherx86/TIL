import unittest
from ip_cidr_trie.trie import PatriciaTrie

class TestPatriciaTrie(unittest.TestCase):
    def test_longest_prefix_matching_ipv4(self):
        trie = PatriciaTrie()
        trie.insert("10.0.0.0/8", "TEN_DEFAULT")
        trie.insert("10.1.0.0/16", "OFFICE_NET")
        trie.insert("10.1.2.0/24", "SERVER_RACK")
        trie.insert("10.1.2.5/32", "SPECIAL_HOST")

        self.assertEqual(trie.find_longest_prefix("10.1.2.5"), "SPECIAL_HOST")
        self.assertEqual(trie.find_longest_prefix("10.1.2.99"), "SERVER_RACK")
        self.assertEqual(trie.find_longest_prefix("10.1.50.1"), "OFFICE_NET")
        self.assertEqual(trie.find_longest_prefix("10.250.0.1"), "TEN_DEFAULT")
        self.assertIsNone(trie.find_longest_prefix("192.168.1.1"))

    def test_ipv6_trie(self):
        trie = PatriciaTrie()
        trie.insert("2001:db8::/32", "DOC_NET")
        trie.insert("2001:db8:1::/48", "SUBNET_1")
        self.assertEqual(trie.find_longest_prefix("2001:db8:1::cafe"), "SUBNET_1")
        self.assertEqual(trie.find_longest_prefix("2001:db8:2::beef"), "DOC_NET")

    def test_route_aggregation(self):
        cidrs = ["192.168.0.0/24", "192.168.1.0/24"]
        supernet = PatriciaTrie.aggregate_routes(cidrs)
        self.assertEqual(supernet, ["192.168.0.0/23"])

if __name__ == "__main__":
    unittest.main()
