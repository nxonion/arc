from sqlalchemy.orm import Session
from typing import Dict, List
from ..repositories.product_repository import ProductRepository
from ..schemas.cart import CartResponse, CartItem, CartItemCreate, CartItemUpdate
from ..models.product import Product
from fastapi import HTTPException, status


class CartService:
    def __init__(self, db: Session):
        self.product_repository = ProductRepository(db)

    def add_to_cart(
        self, cart_data: Dict[int, int], item: CartItemCreate
    ) -> Dict[int, int]:
        product = self.product_repository.get_by_id(item.product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with id {item.product_id} not found",
            )
        if item.product_id in cart_data:
            cart_data[item.product_id] += item.quantity
        else:
            cart_data[item.product_id] = item.quantity

        return cart_data

    def update_cart_item(
        self, cart_data: Dict[int, int], item: CartItemUpdate
    ) -> Dict[int, int]:
        if item.product_id not in cart_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with id {item.product_id} not found in cart",
            )
        cart_data[item.product_id] = item.quantity
        return cart_data

    def remove_from_cart(
        self, cart_data: Dict[int, int], product_id: int
    ) -> Dict[int, int]:
        if product_id not in cart_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with id {product_id} not found in cart",
            )
        del cart_data[product_id]
        return cart_data

    def get_cart_details(self, cart_data: Dict[int, int]) -> CartResponse:
        if not cart_data:
            return CartResponse(items=[], total=0.0, items_count=0)

        product_ids: List[int] = list(cart_data.keys())
        products: List[Product] = self.product_repository.get_multiple_by_ids(product_ids)
        products_dict: Dict[int, Product] = {p.id: p for p in products}  # type: ignore

        cart_items: List[CartItem] = []
        total_price: float = 0.0
        total_items: int = 0

        for product_id, quantity in cart_data.items():
            product: Product | None = products_dict.get(product_id)
            if product is not None:
                product_id_val: int = product.id  # type: ignore
                product_name: str = product.name  # type: ignore
                product_price: float = float(product.price)  # type: ignore
                product_image: str | None = product.image_url  # type: ignore
                
                subtotal: float = product_price * quantity

                cart_item: CartItem = CartItem(
                    product_id=product_id_val,
                    name=product_name,
                    price=product_price,
                    quantity=quantity,
                    subtotal=subtotal,
                    image_url=product_image,
                )

                cart_items.append(cart_item)
                total_price += subtotal
                total_items += quantity

        return CartResponse(
            items=cart_items, total=round(total_price, 2), items_count=total_items
        )