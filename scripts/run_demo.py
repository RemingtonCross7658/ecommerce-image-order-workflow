from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.ecommerce_images import InfraiImageGenerator, OrderRequest, process_order


def main() -> None:
    order = OrderRequest("order-1001", "ceramic travel mug", "buyer@example.com", 2)
    result = process_order(order, InfraiImageGenerator(), Path("artifacts"))
    print(result.receipt)
    print(result.customer_update)
    print("image:", result.image_path)


if __name__ == "__main__":
    main()
