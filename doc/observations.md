- Deals https://www.foodpanda.ro/chain/cj2cc/pizza-romana
- 2 types of vendors: restaurant/chain
  - chain sometimes redirects to a local restaurant (https://www.foodpanda.ro/restaurant/v4no/pizza-hut-delivery-brasov-nord) (https://www.foodpanda.ro/chain/cw9yi/pizza-hut-delivery)
  - address' can't be verified after delivery hours for chains => can't get toppings
- cdn imagini: https://images.deliveryhero.io/image/fd-ro/LH/v6cs-hero.jpg?width=2000&height=500|https://images.deliveryhero.io/image/fd-ro/LH/v6cs-hero.jpg?width=4000&height=1000 (link from node datasets); how to store widths/heights, what are the limits? (vendor banner might have higher limit than dish cards)
- Handling 504 (splash timeout), 400 (splash error), 404 (foodpanda not found)
- for now parsing a vendor already in the db deletes (cascade) everything related to that vendor and inserts the new data again



- Concurent requests: easily managed in settings.py
- topping types: req/optional + radio/checkbox




Psql
```
SELECT d.name, var.id, top.description, o.name
FROM vendors v
JOIN dishes d ON d.vendor_id = v.id
JOIN variations var ON var.dish_id = d.id
JOIN variations_toppings vartop ON vartop.variation_id = var.id
RIGHT OUTER JOIN toppings top ON top.id = vartop.topping_id
JOIN options o ON o.topping_id = top.id
WHERE v.id = 2
ORDER BY d.name, var.id, top.id, o.id
```