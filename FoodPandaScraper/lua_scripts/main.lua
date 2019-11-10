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
    local get_topping_id = splash:jsfunc([[
        function(el) {
            return el.dataset.toppingId;
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

    -- local func
    local function add_topping_selectors(modal)
        local toppings = modal:querySelectorAll('div.topping')
        for _, topping in ipairs(toppings) do
            local topping_container = topping:querySelector('div.product-topping-list')
            local topping_id = get_topping_id(topping_container)
            topping_selectors[topping_id] = topping.node.outerHTML
        end
    end

    -- Loop over all dishes to get topping selectors
    local dishes = splash:select_all('div.dish-card.menu__item')
    for _, dish in ipairs(dishes) do
        local dish_name = dish:querySelector('h3.dish-name.fn.p-name > span').node.textContent
        local results = dish_modal_content(dish)
        
        -- Dish has modal
        if results.modal then
            dish:click{}
            splash:wait(math.random(1.5, 2))
            local modal = splash:select('#choices-toppings-modal .modal-body')
            if not results.only_toppings and not results.only_variations then
                local variations = modal:querySelectorAll('div.product-topping-item')
                if results.click_all_variations then
                    for _, variation in ipairs(variations) do
                        variation:click{}
                        splash:wait(math.random(0.7, 1))
                        add_topping_selectors(modal)
                    end
                else
                    variations[1]:click{}
                    splash:wait(math.random(0.7, 1))
                    add_topping_selectors(modal)
                end
            elseif results.only_toppings then
                add_topping_selectors(modal)
            end
            -- done, close modal
            splash:send_keys('<Escape>')
            splash:wait(math.random(1.4, 1.7))
        end
    end

    return response
end