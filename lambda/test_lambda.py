import unittest
import json
from unittest.mock import patch, MagicMock
from lambda_function import compute_mst, lambda_handler

class TestMSTAlgorithm(unittest.TestCase):
    def test_compute_mst(self):
        num_nodes = 4
        edges = [(3, 1, 2), (1, 2, 3), (4, 3, 4), (2, 1, 4)]
        total_cost, mst_edges = compute_mst(num_nodes, edges)
        self.assertEqual(total_cost, 6)
        self.assertEqual(len(mst_edges), num_nodes - 1)

    @patch("lambda_function.s3_client.get_object")
    @patch("lambda_function.sqs_client.send_message")
    def test_lambda_handler(self, mock_send_message, mock_get_object):
        mock_get_object.return_value = {
            "Body": MagicMock(read=MagicMock(return_value=b"4\n1 2 3\n2 3 1\n3 4 4\n1 4 2"))
        }

        event = {
            "Records": [
                {
                    "s3": {
                        "bucket": {"name": "network-optimization-bucket"},
                        "object": {"key": "sample_network.txt"}
                    }
                }
            ]
        }

        response = lambda_handler(event, None)

        self.assertEqual(response["statusCode"], 200)
        mock_send_message.assert_called_once()
        message_body = json.loads(mock_send_message.call_args[1]["MessageBody"])
        self.assertEqual(message_body["total_cost"], 6)
        self.assertEqual(len(message_body["connections"]), 3)

if __name__ == "__main__":
    unittest.main()
