function main(splash)
    treat = require("treat")
    splash.private_mode_enabled = false
    assert(splash:go(splash.args.url))
    splash:wait(2)

    ---------------------------------------------------------------------------
    -- JS Helpers
    ---------------------------------------------------------------------------
    local coordinates = splash:jsfunc([[
        function() {
            var url = document.querySelector('img.map');
            return url.dataset.imgUrl.match(/\d+.\d+,\d+.\d+/);
        }
    ]])
    local dish_modal_content = splash:jsfunc([[
        function(el) {
            var json = JSON.parse(el.dataset.object);
            var variations = json.product_variations;

            var results = {
                modal: true,
                only_toppings: false,
                only_variations: false,
                click_all_variations: false,
            };

            if (variations.length > 1) {
                results.only_variations = true;

                for (var i = 0; i < variations.length; i++) {
                    if (variations[i].topping_ids.length) {
                        results.only_variations = false;
                        break;
                    }
                }

                if (!results.only_variations) {
                    for (var i = 1; i < variations.length; i++) {
                        if (
                            JSON.stringify(variations[i-1].topping_ids) 
                            !== JSON.stringify(variations[i].topping_ids)
                        ) {
                            results.click_all_variations = true;
                            break;
                        }
                    }
                } 
            } else {
                var topping_ids = variations[0].topping_ids;
                if (topping_ids.length) {
                    results.only_toppings = true;
                } else {
                    results.modal = false;
                }
            }

            return results;
        }
    ]])

    ---------------------------------------------------------------------------
    -- Lua Script
    ---------------------------------------------------------------------------
    local response = {}
    -- Submit Address and get page HTML
    local coords = coordinates()
    -- local address = assert(splash:select('.vendor-location')).node.textContent
    local address_input = assert(splash:select('.restaurants-search-form__input'))
    local address_verify_button = assert(splash:select('.restaurants-search-form__button--full'))
    splash:set_viewport_full()
    address_input:mouse_click{}
    splash:send_text(coords)
    address_verify_button:mouse_click{}
    splash:wait(1.9)
    response['html'] = splash:html()

    -- Click items with modal content and store topping_selectors
    local topping_selectors = {}
    response['topping_selectors'] = topping_selectors
    
    local dishes = splash:select_all('div.dish-card.menu__item')
    for _, dish in ipairs(dishes) do
        local results = dish_modal_content(dish)
        local dish_name = dish:querySelector('h3.dish-name.fn.p-name > span').node.textContent
        if results.modal then
            if results.only_toppings then
                topping_selectors[dish_name] = 'only toppings'
            elseif results.only_variations then
                topping_selectors[dish_name] = 'only variations'
            else
                if results.click_all_variations then
                    topping_selectors[dish_name] = 'click all variations'
                else
                    topping_selectors[dish_name] = 'click only first'
                end
            end
        end
    end

    return response
end