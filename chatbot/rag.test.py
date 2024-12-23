import unittest
from rag import RAG

class TestRAG(unittest.TestCase):
    def setUp(self):
        self.rag = RAG()

def test_create_prompt_with_search_results(self):
    # Arrange
    search_results = [
        {
            'name': 'Test Product',
            'price': '100000',
            'final_price': '90000',
            'shop_free_shipping': 1,
            'attribute': 'Color: Red, Size: M',
            'description': 'A great test product'
        }
    ]
    query = 'Test query'

    # Act
    result = self.rag.create_prompt(search_results, query)

    # Assert
    expected_product_details = "- Tên sản phẩm: Test Product, Giá: 100000, Giá sau giảm: 90000, Miễn phí giao hàng: Có, Thuộc tính: Color: Red, Size: M, Mô tả: A great test product"
    self.assertIn(expected_product_details, result)
    self.assertIn(f"Khách hàng: \n{query}", result)
    self.assertIn("Answer:", result)

if __name__ == '__main__':
    unittest.main()
