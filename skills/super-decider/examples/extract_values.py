"""Pull values out of text with span questions, then validate them in code.

A span is copied verbatim from the state, with character offsets, so code can normalize and check it.
"""
import os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from decide import decide

email = ("Hi, this is Dana Ruiz. My order A-58213 arrived without the charger. "
         "I also bought a laptop sleeve and a USB-C hub last week, both fine. Please send the charger by Friday.")

a = decide(email, {
    "order_id": {"type": "span", "instructions": "The order number the customer refers to"},
    "missing_item": {"type": "span", "instructions": "The item the customer says is missing"},
    "products": {"type": "spans", "instructions": "Every product the customer mentions buying", "criteria": {"max_items": 10}},
    "deadline": {"type": "span", "instructions": "When the customer wants the problem solved"},
})

order = a["order_id"]
if order["found"] and re.fullmatch(r"[A-Z]-\d{5}", order["text"]):
    print(f"order id: {order['text']} (chars {order['start']}-{order['end']})")
else:
    print("order id: not found or wrong format, ask the customer")
print("missing item:", a["missing_item"]["text"] if a["missing_item"]["found"] else None)
print("products:", [item["text"] for item in a["products"]["items"]] if a["products"]["found"] else [])
print("deadline phrase:", a["deadline"]["text"] if a["deadline"]["found"] else None)
